#!/usr/bin/env python3
"""CLI de manutenção do painel Humanitas.

Substitui o notebook `atualizador-do-painel.ipynb` por um script único, testável
e rodável tanto na máquina local quanto no GitHub Actions.

Comandos:
    python -m scripts.painel indice      # regenera indices/indice.json
    python -m scripts.painel tabela      # regenera a tabela do README
    python -m scripts.painel progresso   # regenera progresso.md + bloco do README
    python -m scripts.painel flashcards  # gera flashcards.csv (Anki)
    python -m scripts.painel auditar     # links, frontmatter, duplicados, órfãs
    python -m scripts.painel tudo        # indice + tabela + progresso + flashcards

Só o CLI escreve em `indices/`, `progresso.md`, `flashcards.csv` e no README.
O conversor de PDFs não gera mais índice (evita sobrescrever dados).
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import difflib
import json
import pathlib
import re
import sys
import unicodedata
import uuid
from collections import Counter

RAIZ_PADRAO = pathlib.Path(__file__).resolve().parents[2]

# ---------------------------------------------------------------------------
# Constantes de domínio
# ---------------------------------------------------------------------------

TEMAS = {
    "historia": "História",
    "sociologia": "Sociologia",
    "filosofia": "Filosofia",
    "ciencia-politica": "Ciência Política",
    "antropologia": "Antropologia",
    "economia": "Economia",
    "geografia": "Geografia",
    "psicologia": "Psicologia",
    "psicologia-social": "Psicologia Social",
    "integrada": "Integrada",
}

STATUS_VALIDOS = {
    "rascunho",
    "ok",
    "arquivada",
    "em-andamento",
    "concluida",
    "pausada",
}

NIVEIS_VALIDOS = {"iniciante", "entusiasta", "avancado"}

TIPOS_VALIDOS = {"conceito", "eixo"}

NIVEIS_EVIDENCIA_VALIDOS = {"alta", "media", "baixa", "teorica", "empirica", "forte", "moderada", "fraca"}


MARCADOR_TEMAS = ("<!-- PAINEL-TEMAS-INICIO -->", "<!-- PAINEL-TEMAS-FIM -->")
MARCADOR_PROGRESSO = ("<!-- PROGRESSO-INICIO -->", "<!-- PROGRESSO-FIM -->")

# Seções obrigatórias por tipo de nota. O template marca as demais como opcionais.
SECOES_OBRIGATORIAS = {
    "conceito": [
        "Definição em uma frase",
        "Explicação com as minhas palavras",
        "Conceitos relacionados",
        "Conexões interdisciplinares",
        "Por que este conceito importa",
    ],
    "eixo": [
        "A questão em uma frase",
        "Posições no debate",
        "Conexões interdisciplinares",
    ],
}

# Seção usada como "citação de apoio" na auditoria de qualidade.
SECAO_TRECHO = "Trecho de apoio"

REGEX_CHECKBOX = re.compile(r"^\s*(?:\d+\.|[-*])\s*\[([ xX])\]\s*(.+)$", re.M)
REGEX_SECAO_NO = re.compile(r"^###\s+Nó\s+(.+)$", re.M)
REGEX_FENCE = re.compile(r"```.*?```", re.S)
REGEX_CODIGO_INLINE = re.compile(r"`[^`\n]*`")
REGEX_LINK = re.compile(r"\]\(([^)\s]+)\)")
REGEX_WIKILINK = re.compile(r"\[\[[^\]]+\]\]")
REGEX_TITULO = re.compile(r"^#\s+(.+?)\s*$", re.M)
REGEX_SECAO = re.compile(r"^##\s+(.+?)\s*$", re.M)

# Textos de exemplo dos templates: se a nota ainda os contiver, a seção está pendente.
PLACEHOLDERS = (
    "a definição mais enxuta possível",
    "explique o conceito em 3 a 5 frases",
    "capítulo ou seção onde o autor apresenta",
    "citação literal curta do autor",
    "exemplo 1",
    "formule o debate como uma pergunta",
    "3 a 5 frases: o que está em jogo",
    "uma frase sobre a consequência de entender",
    "nome do conceito",
    "cole aqui",
    "o que este livro mudou",
    "100 a 150 palavras",
)

# Arquivos e pastas que entram no site (o texto integral do acervo fica de fora).
PASTAS_SITE = ("conceitos", "trilhas", "diario", "trechos")
ARQUIVOS_SITE = ("README.md", "progresso.md", "LICENSE", "LICENSE-CONTEUDO.md")


# ---------------------------------------------------------------------------
# Leitura e parsing
# ---------------------------------------------------------------------------


def ler(caminho: pathlib.Path) -> str:
    return caminho.read_text(encoding="utf-8")


def normalizar(texto: str) -> str:
    """Minúsculas, sem acento e sem pontuação — para comparar nomes."""
    texto = unicodedata.normalize("NFKD", texto or "")
    texto = "".join(c for c in texto if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", texto.lower()).strip()


class ErroFrontmatter(Exception):
    """YAML inválido, delimitador faltando ou frontmatter ausente onde é obrigatório."""


# Lista de erros de frontmatter capturados durante a coleta (para auditoria).
_ERROS_FRONTMATTER: list[str] = []


def _limpar_erros_frontmatter() -> None:
    _ERROS_FRONTMATTER.clear()


def _registrar_erro_frontmatter(caminho: str, mensagem: str) -> None:
    _ERROS_FRONTMATTER.append(f"Erro de frontmatter em {caminho}: {mensagem}")


def parse_frontmatter(texto: str) -> dict:
    """Lê o cabeçalho YAML entre `---`. Levanta ErroFrontmatter se inválido."""
    if not texto.lstrip().startswith("---"):
        return {}
    partes = texto.lstrip().split("---", 2)
    if len(partes) < 3:
        raise ErroFrontmatter("Delimitador de frontmatter faltando (esperado '---' de fechamento).")
    bruto = partes[1]
    try:
        import yaml  # type: ignore

        dados = yaml.safe_load(bruto)
        if dados is None:
            return {}
        if not isinstance(dados, dict):
            raise ErroFrontmatter(f"Frontmatter não é um dicionário (encontrado {type(dados).__name__}).")
        return {str(k).strip().lower(): v for k, v in dados.items()}
    except ErroFrontmatter:
        raise
    except Exception as exc:
        raise ErroFrontmatter(f"YAML inválido: {exc}") from exc


def parse_tags(valor) -> list[str]:
    if isinstance(valor, (list, tuple)):
        return [str(v).strip() for v in valor if str(v).strip()]
    if not valor:
        return []
    return [
        t.strip().strip("\"'")
        for t in str(valor).strip().strip("[]").split(",")
        if t.strip()
    ]


def secoes(texto: str) -> list[tuple[str, str]]:
    """Lista (título, corpo) das seções `##` do arquivo."""
    achados = list(REGEX_SECAO.finditer(texto))
    saida = []
    for i, m in enumerate(achados):
        inicio = m.end()
        fim = achados[i + 1].start() if i + 1 < len(achados) else len(texto)
        saida.append((m.group(1).strip(), texto[inicio:fim]))
    return saida


def achar_secao(texto: str, titulo: str) -> str:
    """Corpo da seção cujo título começa pelo texto pedido (ignora acento/caixa)."""
    alvo = normalizar(titulo)
    for nome, corpo in secoes(texto):
        if normalizar(nome).startswith(alvo):
            return corpo
    return ""


def extrair_secao(texto: str, titulo: str) -> str:
    """Primeiro parágrafo útil de uma seção, sem comentários HTML nem citações."""
    corpo = achar_secao(texto, titulo)
    if not corpo:
        return ""
    corpo = re.sub(r"<!--.*?-->", "", corpo, flags=re.S)
    linhas = []
    for linha in corpo.splitlines():
        limpa = linha.strip()
        if not limpa:
            if linhas:
                break
            continue
        if limpa.startswith((">", "|")):
            continue
        linhas.append(limpa.lstrip("-* ").strip())
    return " ".join(linhas).strip()


def titulo_h1(texto: str) -> str:
    m = REGEX_TITULO.search(texto)
    return m.group(1).strip() if m else ""


def limpar_markdown(texto: str) -> str:
    """Remove marcação suficiente para um cartão de Anki legível."""
    texto = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", texto)
    texto = re.sub(r"[*_`]+", "", texto)
    return re.sub(r"\s+", " ", texto).strip()


def sem_codigo(texto: str) -> str:
    """Remove blocos e trechos de código: links de exemplo não devem ser auditados."""
    return REGEX_CODIGO_INLINE.sub("", REGEX_FENCE.sub("", texto))


def listar_md(pasta: pathlib.Path, recursivo: bool = False) -> list[pathlib.Path]:
    if not pasta.exists():
        return []
    itens = pasta.rglob("*.md") if recursivo else pasta.glob("*.md")
    return sorted(p for p in itens if p.name.upper() != "README.MD")


def eh_placeholder(texto: str) -> bool:
    """True quando o trecho ainda é o texto de exemplo do template."""
    normalizado = normalizar(texto)
    return not normalizado or any(p in normalizado for p in map(normalizar, PLACEHOLDERS))


def rel(caminho: pathlib.Path, raiz: pathlib.Path) -> str:
    try:
        return str(caminho.relative_to(raiz))
    except ValueError:
        return str(caminho)


def substituir_bloco(texto: str, marcadores: tuple[str, str], bloco: str) -> str:
    inicio, fim = marcadores
    if inicio not in texto or fim not in texto:
        return texto
    pre = texto.split(inicio)[0]
    pos = texto.split(fim, 1)[1]
    return f"{pre}{inicio}\n\n{bloco}\n\n{fim}{pos}"


