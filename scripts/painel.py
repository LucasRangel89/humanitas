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

RAIZ_PADRAO = pathlib.Path(__file__).resolve().parents[1]

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


def _frontmatter_simples(bruto: str) -> dict:
    """Fallback sem PyYAML: cobre o subconjunto usado no repositório."""
    dados: dict = {}
    for linha in bruto.splitlines():
        if ":" not in linha or linha.lstrip().startswith("#"):
            continue
        chave, valor = linha.split(":", 1)
        chave = chave.strip().lower()
        valor = valor.strip()
        if valor.startswith("[") and valor.endswith("]"):
            itens = [
                item.strip().strip("\"'")
                for item in valor[1:-1].split(",")
                if item.strip()
            ]
            dados[chave] = itens
        else:
            dados[chave] = valor.strip("\"'")
    return dados


def parse_frontmatter(texto: str) -> dict:
    """Lê o cabeçalho YAML entre `---`. Nunca levanta exceção."""
    if not texto.lstrip().startswith("---"):
        return {}
    partes = texto.lstrip().split("---", 2)
    if len(partes) < 3:
        return {}
    bruto = partes[1]
    try:  # PyYAML é opcional: o fallback entende o formato usado no painel
        import yaml  # type: ignore

        dados = yaml.safe_load(bruto)
        if isinstance(dados, dict):
            return {str(k).strip().lower(): v for k, v in dados.items()}
    except Exception:
        pass
    return _frontmatter_simples(bruto)


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


# ---------------------------------------------------------------------------
# Coleta de dados
# ---------------------------------------------------------------------------


def coletar_conceitos(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "conceitos", recursivo=True):
        texto = ler(arq)
        fm = parse_frontmatter(texto)
        tipo = str(fm.get("tipo") or ("eixo" if fm.get("eixo") else "conceito")).strip()
        nome = (
            fm.get("conceito")
            or fm.get("eixo")
            or titulo_h1(texto)
        )
        nome = re.sub(r"^(Conceito|Eixo)\s*[—–-]\s*", "", str(nome or "")).strip()
        definicao = extrair_secao(texto, "Definição em uma frase") or extrair_secao(
            texto, "A questão em uma frase"
        )
        faltando = [
            secao
            for secao in SECOES_OBRIGATORIAS.get(tipo, [])
            if not achar_secao(texto, secao).strip()
        ]
        registros.append(
            {
                "arquivo": arq.name,
                "caminho": rel(arq, raiz),
                "conceito": nome,
                "tipo": tipo,
                "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
                "nivel": str(fm.get("nivel") or "").strip().lower(),
                "status": str(fm.get("status") or "").strip().lower(),
                "obra_origem": str(fm.get("obra_origem") or "").strip(),
                "autor_origem": str(fm.get("autor_origem") or "").strip(),
                "definicao": definicao,
                "tags": parse_tags(fm.get("tags")),
                "secoes_faltando": faltando,
                "tem_trecho": bool(achar_secao(texto, SECAO_TRECHO).strip()),
                "_texto": texto,
            }
        )
    return registros


def coletar_livros(raiz: pathlib.Path, tema_antigo: dict | None = None) -> tuple[list[dict], list[dict]]:
    tema_antigo = tema_antigo or {}
    livros, fichas = [], []
    for arq in listar_md(raiz / "acervo", recursivo=True):
        texto = ler(arq)
        fm = parse_frontmatter(texto)
        tema = str(fm.get("tema") or "").strip().lower()
        if not tema:
            tema = tema_antigo.get(arq.name, "sem-tema")
        registro = {
            "arquivo": arq.name,
            "caminho": rel(arq, raiz),
            "tema": tema or "sem-tema",
            "palavras": len(texto.split()),
        }
        ficha = arq.name.lower().endswith("-ficha.md") or fm.get("tipo") == "ficha-de-leitura"
        if ficha:
            registro.update(
                {
                    "obra": str(fm.get("obra") or "").strip(),
                    "autor": str(fm.get("autor") or "").strip(),
                    "ano": fm.get("ano"),
                    "status": str(fm.get("status") or "").strip().lower(),
                }
            )
            fichas.append(registro)
        else:
            registro["titulo"] = str(fm.get("obra") or arq.stem.replace("-", " "))
            livros.append(registro)
    return livros, fichas


def tema_do_indice_antigo(raiz: pathlib.Path) -> dict:
    caminho = raiz / "indices" / "indice.json"
    if not caminho.exists():
        return {}
    try:
        antigo = json.loads(ler(caminho))
    except Exception:
        return {}
    mapa = {}
    for chave in ("livros", "fichas"):
        for item in antigo.get(chave, []) or []:
            if isinstance(item, dict) and item.get("arquivo"):
                tema = (item.get("tema") or "").strip().lower()
                if tema:
                    mapa[item["arquivo"]] = tema
    return mapa


def coletar_trechos(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "trechos", recursivo=True):
        texto = ler(arq)
        fm = parse_frontmatter(texto)
        registros.append(
            {
                "arquivo": arq.name,
                "caminho": rel(arq, raiz),
                "titulo": titulo_h1(texto),
                "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
                "obra": str(fm.get("obra") or "").strip(),
                "autor": str(fm.get("autor") or "").strip(),
                "capitulo": str(fm.get("capitulo") or "").strip(),
                "pagina": str(fm.get("pagina") or "").strip(),
            }
        )
    return registros


def progresso_trilha(texto: str) -> dict:
    """Conta nós por checkbox; se não houver, usa os títulos `### Nó ...`."""
    itens = REGEX_CHECKBOX.findall(texto)
    if itens:
        total = len(itens)
        feitos = sum(1 for marca, _ in itens if marca.strip().lower() == "x")
        proximo = next(
            (limpar_markdown(txt).strip() for marca, txt in itens if marca.strip() != "x"),
            "",
        )
        formato = "checkbox"
    else:
        secoes_no = REGEX_SECAO_NO.findall(texto)
        total, feitos = len(secoes_no), 0
        proximo = limpar_markdown(secoes_no[0]).strip() if secoes_no else ""
        formato = "secoes"
    return {
        "nos_total": total,
        "nos_concluidos": feitos,
        "formato": formato,
        "proximo_no": proximo,
    }


def coletar_trilhas(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "trilhas", recursivo=True):
        texto = ler(arq)
        fm = parse_frontmatter(texto)
        registro = {
            "arquivo": arq.name,
            "caminho": rel(arq, raiz),
            "trilha": str(fm.get("trilha") or titulo_h1(texto)).strip(),
            "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
            "nivel": str(fm.get("nivel") or "").strip().lower(),
            "status": str(fm.get("status") or "").strip().lower(),
            "objetivo": extrair_secao(texto, "Objetivo da trilha"),
        }
        registro.update(progresso_trilha(texto))
        registros.append(registro)
    return registros


def coletar_diario(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "diario", recursivo=True):
        texto = ler(arq)
        fm = parse_frontmatter(texto)
        data = fm.get("data")
        if isinstance(data, (dt.date, dt.datetime)):
            data = data.isoformat()
        registros.append(
            {
                "arquivo": arq.name,
                "caminho": rel(arq, raiz),
                "data": str(data or "").strip(),
                "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
                "origem": str(fm.get("origem") or "").strip(),
                "titulo": titulo_h1(texto),
            }
        )
    return registros


def montar_indice(raiz: pathlib.Path) -> dict:
    tema_antigo = tema_do_indice_antigo(raiz)
    livros, fichas = coletar_livros(raiz, tema_antigo)
    conceitos = coletar_conceitos(raiz)
    trechos = coletar_trechos(raiz)
    trilhas = coletar_trilhas(raiz)
    diario = coletar_diario(raiz)

    for registro in conceitos:
        registro["pendencias"] = pendencias_da_nota(registro)
        registro.pop("_texto", None)

    indice = {
        "projeto": "humanitas",
        "descricao": (
            "Mapa geral do painel. Gerado por `python -m scripts.painel indice` "
            "— não edite à mão."
        ),
        "atualizado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "totais": {
            "livros": len(livros),
            "fichas": len(fichas),
            "conceitos": sum(1 for c in conceitos if c["tipo"] == "conceito"),
            "eixos": sum(1 for c in conceitos if c["tipo"] == "eixo"),
            "trechos": len(trechos),
            "trilhas": len(trilhas),
            "diario": len(diario),
        },
        "livros": livros,
        "fichas": fichas,
        "conceitos": conceitos,
        "trechos": trechos,
        "trilhas": trilhas,
        "diario": diario,
    }
    return indice


# ---------------------------------------------------------------------------
# Geração de tabelas e artefatos
# ---------------------------------------------------------------------------


def tabela_temas(indice: dict) -> str:
    conceitos = Counter(c.get("tema", "sem-tema") for c in indice["conceitos"])
    livros = Counter(l.get("tema", "sem-tema") for l in indice["livros"])
    fichas = Counter(f.get("tema", "sem-tema") for f in indice["fichas"])
    trilhas = Counter(t.get("tema", "sem-tema") for t in indice.get("trilhas", []))

    temas = dict(TEMAS)
    for chave in sorted(set(conceitos) | set(livros) | set(fichas) | set(trilhas)):
        temas.setdefault(chave, chave.replace("-", " ").title())

    linhas = [
        "| Tema | Status | Notas de conceito | Livros processados | Fichas | Trilhas |",
        "|---|---|---|---|---|---|",
    ]
    for chave, nome in temas.items():
        nc, nl, nf = conceitos.get(chave, 0), livros.get(chave, 0), fichas.get(chave, 0)
        nt = trilhas.get(chave, 0)
        status = "Ativo" if (nc + nl + nf + nt) > 0 else "Em breve"
        linhas.append(f"| {nome} | {status} | {nc} | {nl} | {nf} | {nt} |")
    return "\n".join(linhas)


def substituir_bloco(texto: str, marcadores: tuple[str, str], bloco: str) -> str:
    inicio, fim = marcadores
    if inicio not in texto or fim not in texto:
        return texto
    pre = texto.split(inicio)[0]
    pos = texto.split(fim, 1)[1]
    return f"{pre}{inicio}\n\n{bloco}\n\n{fim}{pos}"


def gravar_indice(raiz: pathlib.Path, indice: dict) -> pathlib.Path:
    """Grava o índice; se nada além do timestamp mudou, mantém o arquivo intacto.

    Isso é o que permite ao CI rodar `indice` e conferir com `git diff --exit-code`
    sem falhar só porque o relógio andou.
    """
    caminho = raiz / "indices" / "indice.json"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    comparavel = {k: v for k, v in indice.items() if k != "atualizado_em"}
    if caminho.exists():
        try:
            anterior = json.loads(ler(caminho))
            anterior_comparavel = {k: v for k, v in anterior.items() if k != "atualizado_em"}
            if anterior_comparavel == comparavel:
                return caminho
        except Exception:
            pass
    caminho.write_text(
        json.dumps(indice, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return caminho


def atualizar_readme_temas(raiz: pathlib.Path, tabela: str) -> bool:
    readme = raiz / "README.md"
    if not readme.exists():
        return False
    texto = ler(readme)
    novo = substituir_bloco(texto, MARCADOR_TEMAS, tabela)
    if novo == texto:
        return False
    readme.write_text(novo, encoding="utf-8")
    return True


def progresso_barra(feitos: int, total: int, largura: int = 10) -> str:
    if total <= 0:
        return "—"
    preenchido = round(largura * feitos / total)
    return f"[{'#' * preenchido}{'-' * (largura - preenchido)}] {feitos * 100 // total}%"


def pendencias_da_nota(registro: dict) -> list[str]:
    """O que falta para a nota virar padrão-ouro (lista vazia = pronta)."""
    texto = registro.get("_texto", "")
    faltas = []
    if eh_placeholder(registro.get("definicao", "")):
        faltas.append("definição em uma frase")
    if eh_placeholder(extrair_secao(texto, "Explicação com as minhas palavras")):
        faltas.append("explicação com as suas palavras")
    trecho = achar_secao(texto, "Trecho de apoio")
    if not trecho.strip() or eh_placeholder(trecho) or "> \"" in trecho:
        faltas.append("citação de apoio (com capítulo/página)")
    if registro.get("tipo") == "conceito" and eh_placeholder(
        extrair_secao(texto, "Exemplos que ilustram")
    ):
        faltas.append("exemplo próprio (de preferência brasileiro)")
    if re.search(
        r"guia de estudos|planos de estudo|anexo|wikip", registro.get("obra_origem", ""), re.I
    ):
        faltas.append("fonte primária")
    if registro.get("tipo") == "eixo" and eh_placeholder(
        achar_secao(texto, "Posições no debate")
    ):
        faltas.append("posições com autor e obra")
    if registro.get("status") != "ok":
        faltas.append("status ainda é rascunho")
    return faltas


def calcular_progresso(indice: dict) -> dict:
    conceitos = indice["conceitos"]
    status = Counter(c["status"] or "sem-status" for c in conceitos)
    ok = status.get("ok", 0)
    rascunho = status.get("rascunho", 0)
    com_trecho = sum(1 for c in conceitos if c["tem_trecho"])
    fonte_secundaria = re.compile(r"guia de estudos|planos de estudo|anexo|wikip", re.I)
    com_fonte_primaria = sum(
        1
        for c in conceitos
        if c["obra_origem"] and not fonte_secundaria.search(c["obra_origem"])
    )
    datas = sorted(d["data"] for d in indice["diario"] if d["data"])
    semanas = {
        dt.date.fromisoformat(d[:10]).isocalendar()[:2]
        for d in datas
        if re.match(r"^\d{4}-\d{2}-\d{2}", d)
    }
    ultima = datas[-1] if datas else ""
    return {
        "conceitos": len(conceitos),
        "ok": ok,
        "rascunho": rascunho,
        "com_trecho": com_trecho,
        "fonte_primaria": com_fonte_primaria,
        "diario_total": len(indice["diario"]),
        "diario_semanas": len(semanas),
        "diario_ultima": ultima,
        "trilhas_total": len(indice["trilhas"]),
        "nos_total": sum(t["nos_total"] for t in indice["trilhas"]),
        "nos_concluidos": sum(t["nos_concluidos"] for t in indice["trilhas"]),
        "fichas": len(indice["fichas"]),
        "trechos": len(indice["trechos"]),
        "livros": len(indice["livros"]),
    }


def texto_progresso(indice: dict) -> str:
    p = calcular_progresso(indice)
    linhas = [
        "# Progresso do painel",
        "",
        "> Gerado automaticamente por `python -m scripts.painel progresso`. "
        "Não edite à mão.",
        "",
        "## Resumo",
        "",
        "| Indicador | Valor |",
        "|---|---|",
        f"| Notas de conceito | {p['conceitos']} |",
        f"| Notas reescritas (`status: ok`) | {p['ok']} |",
        f"| Notas em rascunho | {p['rascunho']} |",
        f"| Notas com citação de apoio | {p['com_trecho']} |",
        f"| Notas com fonte primária declarada | {p['fonte_primaria']} |",
        f"| Nós de trilha concluídos | {p['nos_concluidos']} de {p['nos_total']} |",
        f"| Entradas de diário | {p['diario_total']} (em {p['diario_semanas']} semana(s)) |",
        f"| Fichas de leitura | {p['fichas']} |",
        f"| Trechos guardados | {p['trechos']} |",
        f"| Livros no acervo | {p['livros']} |",
        "",
        "## Trilhas",
        "",
        "| Trilha | Nós | Concluídos | Progresso | Próximo nó |",
        "|---|---|---|---|---|",
    ]
    for t in indice["trilhas"]:
        proximo = t["proximo_no"] or "—"
        if len(proximo) > 70:
            proximo = proximo[:67].rstrip() + "…"
        linhas.append(
            f"| {t['trilha']} | {t['nos_total']} | {t['nos_concluidos']} | "
            f"{progresso_barra(t['nos_concluidos'], t['nos_total'])} | {proximo} |"
        )
    linhas += [
        "",
        "## Notas por tema",
        "",
        "| Tema | Notas | ok | rascunho | Com citação | Fonte primária |",
        "|---|---|---|---|---|---|",
    ]
    temas = Counter(c["tema"] for c in indice["conceitos"])
    for tema, total in sorted(temas.items(), key=lambda item: (-item[1], item[0])):
        do_tema = [c for c in indice["conceitos"] if c["tema"] == tema]
        nome = TEMAS.get(tema, tema)
        linhas.append(
            f"| {nome} | {total} | "
            f"{sum(1 for c in do_tema if c['status'] == 'ok')} | "
            f"{sum(1 for c in do_tema if c['status'] == 'rascunho')} | "
            f"{sum(1 for c in do_tema if c['tem_trecho'])} | "
            f"{sum(1 for c in do_tema if c['obra_origem'] and not re.search('guia de estudos|planos de estudo|anexo|wikip', c['obra_origem'], re.I))} |"
        )
    # próximas notas a reescrever — o trabalho de estudo da semana
    pendentes = []
    for c in indice["conceitos"]:
        faltas = c.get("pendencias") or []
        if faltas and c.get("status") != "ok":
            pendentes.append((len(faltas), c["conceito"], c["tema"], faltas))
    if pendentes:
        pendentes.sort(key=lambda item: (-item[0], item[1]))
        linhas += [
            "",
            "## Próximas notas a reescrever",
            "",
            "As notas com mais pendências primeiro. Reescrever uma nota é o que a "
            "move para `status: ok`.",
            "",
            "| Nota | Tema | Pendências |",
            "|---|---|---|",
        ]
        for _, nome, tema, faltas in pendentes[:12]:
            linhas.append(f"| {nome} | {TEMAS.get(tema, tema)} | {len(faltas)} — {faltas[0]} |")
        if len(pendentes) > 12:
            linhas.append(f"| … | | mais {len(pendentes) - 12} nota(s) |")
    if p["diario_ultima"]:
        linhas += ["", f"Última entrada no diário: **{p['diario_ultima']}**."]
    linhas += [
        "",
        "## Como melhorar estes números",
        "",
        "- A métrica que importa não é quantidade de notas, é **nota reescrita** "
        "(`status: ok`) e **entrada de diário**.",
        "- Uma nota só vira `ok` depois de reescrita com as suas palavras, com um "
        "exemplo seu e, quando possível, uma citação com capítulo/página.",
        "- O diário é o único arquivo que a IA nunca escreve por você.",
        "",
    ]
    return "\n".join(linhas)


def bloco_progresso_readme(indice: dict) -> str:
    p = calcular_progresso(indice)
    linhas = [
        "| Indicador | Valor |",
        "|---|---|",
        f"| Nós de trilha concluídos | {p['nos_concluidos']} de {p['nos_total']} |",
        f"| Notas reescritas (`ok`) | {p['ok']} de {p['conceitos']} |",
        f"| Entradas de diário | {p['diario_total']} |",
        f"| Notas com citação de apoio | {p['com_trecho']} de {p['conceitos']} |",
        "",
        "Detalhes por trilha e por tema em [`progresso.md`](progresso.md).",
    ]
    return "\n".join(linhas)


def atualizar_readme_progresso(raiz: pathlib.Path, bloco: str) -> bool:
    readme = raiz / "README.md"
    if not readme.exists():
        return False
    texto = ler(readme)
    novo = substituir_bloco(texto, MARCADOR_PROGRESSO, bloco)
    if novo == texto:
        return False
    readme.write_text(novo, encoding="utf-8")
    return True


# ---------------------------------------------------------------------------
# Flashcards
# ---------------------------------------------------------------------------


def cartoes_de(registro: dict) -> list[list[str]]:
    """Cartões com GUID estável: reimportar no Anki atualiza em vez de duplicar."""
    nome = registro["conceito"]
    if not nome:
        return []
    base = uuid.uuid5(uuid.NAMESPACE_URL, f"humanitas/{normalizar(nome)}")
    tema = TEMAS.get(registro["tema"], registro["tema"])
    tags = " ".join(dict.fromkeys(["humanitas", registro["tema"], *registro["tags"][:3]]))
    fonte = registro["obra_origem"]
    cartoes: list[list[str]] = []

    def adicionar(tipo: str, frente: str, verso: str) -> None:
        verso = limpar_markdown(verso)
        if not verso:
            return
        cartoes.append(
            [
                str(uuid.uuid5(base, tipo)),
                frente,
                verso,
                tags,
                f"Humanitas::{tema}",
            ]
        )

    definicao = registro["definicao"]
    if not eh_placeholder(definicao):  # texto de exemplo do template não vira cartão
        adicionar("definicao", f"O que é {nome}?", definicao + (f" — Fonte: {fonte}" if fonte else ""))

    if registro["tipo"] == "conceito":
        exemplos = extrair_secao(registro["_texto"], "Exemplos que ilustram")
        adicionar(
            "aplicacao",
            f"Dê um exemplo concreto de {nome} e explique por que ele ilustra o conceito.",
            exemplos,
        )
    else:
        posicoes = achar_secao(registro["_texto"], "Posições no debate")
        itens = []
        for linha in posicoes.splitlines():
            if not linha.strip().startswith("|"):
                continue
            celulas = [c.strip() for c in linha.strip().strip("|").split("|")]
            if len(celulas) < 2 or set(celulas[0]) <= {"-", ":"} or celulas[0].lower() == "posição":
                continue
            itens.append(f"{celulas[0]} — {celulas[1]}")
        adicionar(
            "posicoes",
            f"Quais posições compõem o eixo “{nome}”?",
            "; ".join(itens),
        )
    return cartoes


def gerar_flashcards(raiz: pathlib.Path, indice: dict | None = None) -> list[list[str]]:
    indice = indice or montar_indice(raiz)
    conceitos = coletar_conceitos(raiz)
    # usa os textos completos (com `_texto`) para montar os cartões
    registros = {c["arquivo"]: c for c in conceitos}
    linhas: list[list[str]] = []
    vistos: set[str] = set()
    for registro in registros.values():
        for linha in cartoes_de(registro):
            if linha[0] in vistos:
                continue
            vistos.add(linha[0])
            linhas.append(linha)
    linhas.sort(key=lambda item: (item[4], item[1]))
    return linhas


# ---------------------------------------------------------------------------
# Auditoria
# ---------------------------------------------------------------------------


def _links_quebrados(raiz: pathlib.Path, arquivos: list[pathlib.Path]) -> list[str]:
    problemas = []
    for arq in arquivos:
        texto = sem_codigo(ler(arq))
        for alvo in REGEX_LINK.findall(texto):
            if alvo.startswith(("http://", "https://", "mailto:", "#")):
                continue
            caminho = alvo.split("#")[0].strip()
            if not caminho or not caminho.lower().endswith(".md"):
                continue
            if (arq.parent / caminho).exists() or (raiz / caminho).exists():
                continue
            problemas.append(
                f"Link quebrado em {rel(arq, raiz)}: ({alvo})"
            )
    return problemas


def _wikilinks(raiz: pathlib.Path, arquivos: list[pathlib.Path]) -> list[str]:
    problemas = []
    for arq in arquivos:
        for achado in REGEX_WIKILINK.findall(sem_codigo(ler(arq))):
            problemas.append(
                f"Wikilink (não vira link no GitHub) em {rel(arq, raiz)}: {achado}"
            )
    return problemas


def _validar_metadados(conceitos: list[dict], trilhas: list[dict], diario: list[dict], trechos: list[dict]) -> list[str]:
    erros = []
    for c in conceitos:
        onde = f"conceitos/{c['arquivo']}"
        if c["tema"] == "sem-tema" or c["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({c['tema']!r})")
        if c["tipo"] not in TIPOS_VALIDOS:
            erros.append(f"{onde}: tipo inválido ({c['tipo']!r})")
        if c["status"] and c["status"] not in STATUS_VALIDOS:
            erros.append(f"{onde}: status inválido ({c['status']!r})")
        if not c["status"]:
            erros.append(f"{onde}: campo obrigatório ausente: status")
        if c["nivel"] and c["nivel"] not in NIVEIS_VALIDOS:
            erros.append(f"{onde}: nivel inválido ({c['nivel']!r})")
        if not c["nivel"]:
            erros.append(f"{onde}: campo obrigatório ausente: nivel")
        if not c["conceito"]:
            erros.append(f"{onde}: nome do conceito ausente (frontmatter ou título)")
        if not c["definicao"]:
            erros.append(f"{onde}: sem definição em uma frase (flashcard ficaria vazio)")
        for secao in c["secoes_faltando"]:
            erros.append(f"{onde}: seção obrigatória ausente ou vazia: '{secao}'")
    for t in trilhas:
        onde = f"trilhas/{t['arquivo']}"
        if t["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({t['tema']!r})")
        if t["status"] and t["status"] not in STATUS_VALIDOS:
            erros.append(f"{onde}: status inválido ({t['status']!r})")
        if not t["status"]:
            erros.append(f"{onde}: campo obrigatório ausente: status")
    for d in diario:
        onde = f"diario/{d['arquivo']}"
        if not d["data"]:
            erros.append(f"{onde}: campo obrigatório ausente: data")
        if d["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({d['tema']!r})")
    for t in trechos:
        onde = f"trechos/{t['arquivo']}"
        if not t["obra"]:
            erros.append(f"{onde}: campo obrigatório ausente: obra")
        if t["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({t['tema']!r})")
    return erros


def _duplicados(conceitos: list[dict]) -> tuple[list[str], list[str]]:
    erros, avisos = [], []
    nomes = [(c["arquivo"], normalizar(c["conceito"])) for c in conceitos]
    for i in range(len(nomes)):
        arq_a, nome_a = nomes[i]
        if not nome_a:
            continue
        for j in range(i + 1, len(nomes)):
            arq_b, nome_b = nomes[j]
            if not nome_b:
                continue
            if nome_a == nome_b:
                erros.append(
                    f"Conceito duplicado: conceitos/{arq_a} e conceitos/{arq_b} "
                    f"(\"{conceitos[i]['conceito']}\") — junte as duas notas."
                )
            elif difflib.SequenceMatcher(None, nome_a, nome_b).ratio() >= 0.9:
                avisos.append(
                    f"Conceitos parecidos: \"{conceitos[i]['conceito']}\" ({arq_a}) e "
                    f"\"{conceitos[j]['conceito']}\" ({arq_b}) — são o mesmo conceito?"
                )
    return erros, avisos


def auditar(raiz: pathlib.Path) -> tuple[list[str], list[str]]:
    """Devolve (erros, avisos). Erros bloqueiam o CI."""
    erros, avisos = [], []

    pastas = ["conceitos", "trechos", "trilhas", "diario", "acervo", "docs"]
    arquivos = []
    for nome in pastas:
        arquivos.extend(listar_md(raiz / nome, recursivo=(nome == "acervo")))
    if (raiz / "README.md").exists():
        arquivos.append(raiz / "README.md")

    erros.extend(_links_quebrados(raiz, arquivos))
    erros.extend(_wikilinks(raiz, arquivos))

    conceitos = coletar_conceitos(raiz)
    trilhas = coletar_trilhas(raiz)
    diario = coletar_diario(raiz)
    trechos = coletar_trechos(raiz)

    erros.extend(_validar_metadados(conceitos, trilhas, diario, trechos))
    duplicados_erros, duplicados_avisos = _duplicados(conceitos)
    erros.extend(duplicados_erros)
    avisos.extend(duplicados_avisos)

    # notas não citadas em nenhuma trilha
    texto_trilhas = "\n".join(ler(p) for p in listar_md(raiz / "trilhas"))
    orfas = [c["arquivo"] for c in conceitos if c["arquivo"] not in texto_trilhas]
    if orfas:
        avisos.append(
            "Notas não citadas em nenhuma trilha (podem ser exploração livre): "
            + ", ".join(orfas)
        )

    # notas sem citação de apoio (informativo, não bloqueia)
    sem_trecho = [c["arquivo"] for c in conceitos if not c["tem_trecho"]]
    if sem_trecho:
        avisos.append(
            f"{len(sem_trecho)} nota(s) sem seção '{SECAO_TRECHO}' preenchida "
            "(o padrão-ouro pede citação com capítulo/página)."
        )

    # fontes secundárias declaradas
    secundarias = [
        c["arquivo"]
        for c in conceitos
        if re.search(r"guia de estudos|planos de estudo|anexo|wikip", c["obra_origem"], re.I)
    ]
    if secundarias:
        avisos.append(
            f"{len(secundarias)} nota(s) declaram fonte secundária (guia/planos) — "
            "priorize substituir por obra primária ao reescrever."
        )

    # texto integral versionado (risco de direitos autorais)
    livros = [p for p in listar_md(raiz / "acervo", recursivo=True)]
    if livros:
        avisos.append(
            f"{len(livros)} arquivo(s) em acervo/ — confirme que o repositório é "
            "privado ou que o texto integral está fora do Git (.gitignore)."
        )

    # rascunhos
    rascunhos = sum(1 for c in conceitos if c["status"] == "rascunho")
    if rascunhos:
        avisos.append(f"{rascunhos} nota(s) ainda em `status: rascunho` para reescrever.")

    return erros, avisos


# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------


def _imprimir_lista(titulo: str, itens: list[str]) -> None:
    if not itens:
        return
    print(f"\n{titulo} ({len(itens)}):")
    for item in itens:
        print(f"  - {item}")


def cmd_indice(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    caminho = gravar_indice(raiz, indice)
    t = indice["totais"]
    print(
        f"{rel(caminho, raiz)} regenerado: {t['livros']} livro(s), {t['fichas']} ficha(s), "
        f"{t['conceitos']} conceito(s), {t['eixos']} eixo(s), {t['trechos']} trecho(s), "
        f"{t['trilhas']} trilha(s), {t['diario']} entrada(s) de diário."
    )
    return 0


def cmd_tabela(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    tabela = tabela_temas(indice)
    readme = raiz / "README.md"
    texto = ler(readme) if readme.exists() else ""
    inicio, fim = MARCADOR_TEMAS
    if inicio not in texto or fim not in texto:
        destino = raiz / "indices" / "tabela-temas.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("## Painel de temas\n\n" + tabela + "\n", encoding="utf-8")
        print(
            "Aviso: marcadores PAINEL-TEMAS não encontrados no README. "
            f"Tabela salva em {rel(destino, raiz)}."
        )
    elif atualizar_readme_temas(raiz, tabela):
        print("README.md atualizado com a tabela de temas.")
    else:
        print("Tabela de temas já estava atualizada.")
    print()
    print(tabela)
    return 0


def cmd_progresso(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    conteudo = texto_progresso(indice)
    destino = raiz / "progresso.md"
    destino.write_text(conteudo, encoding="utf-8")
    atualizar_readme_progresso(raiz, bloco_progresso_readme(indice))
    p = calcular_progresso(indice)
    print(
        f"{rel(destino, raiz)} regenerado: {p['ok']}/{p['conceitos']} notas ok, "
        f"{p['nos_concluidos']}/{p['nos_total']} nós de trilha, "
        f"{p['diario_total']} entrada(s) de diário."
    )
    return 0


def cmd_flashcards(raiz: pathlib.Path) -> int:
    linhas = gerar_flashcards(raiz)
    destino = raiz / "flashcards.csv"
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["guid", "frente", "verso", "tags", "baralho"])
        escritor.writerows(linhas)
    print(f"{rel(destino, raiz)} criado com {len(linhas)} cartão(ões).")
    if not linhas:
        print("Nenhum cartão: crie notas com 'Definição em uma frase' preenchida.")
    return 0


def cmd_auditar(raiz: pathlib.Path, estrito: bool = False) -> int:
    erros, avisos = auditar(raiz)
    print("# Auditoria do painel")
    _imprimir_lista("Erros", erros)
    _imprimir_lista("Avisos", avisos)
    if not erros and not avisos:
        print("Painel limpo: nenhum erro e nenhum aviso.")
    print(
        f"\nResumo: {len(erros)} erro(s), {len(avisos)} aviso(s)."
    )
    if erros or (estrito and avisos):
        return 1
    return 0


# ---------------------------------------------------------------------------
# Scaffold de notas novas
# ---------------------------------------------------------------------------

# tipo -> (template, pasta-destino, campos extras)
TIPOS_NOVA = {
    "conceito": ("template-conceito.md", "conceitos", ("autor", "obra", "nivel")),
    "eixo": ("template-eixo.md", "conceitos", ("autor", "nivel")),
    "ficha": ("template-livro.md", "acervo/fichas", ("autor", "obra", "ano")),
    "trecho": ("template-trecho.md", "trechos", ("autor", "obra", "capitulo", "pagina")),
    "diario": ("template-diario.md", "diario", ("origem", "data")),
}

ROTULO_H1 = {
    "conceito": "Nome do conceito",
    "eixo": "Nome da grande questão",
    "ficha": "Título da obra",
    "trecho": "tema curto do trecho",
    "diario": "tema curto da reflexão",
}


def slug(texto: str) -> str:
    """Nome de arquivo compatível com o GitHub: sem acento, minúsculo, com hífens."""
    return re.sub(r"-+", "-", normalizar(texto).replace(" ", "-")).strip("-")


def yaml_escalar(valor) -> str:
    if isinstance(valor, (list, tuple)):
        return "[" + ", ".join(str(v) for v in valor) + "]"
    if isinstance(valor, int):
        return str(valor)
    return '"' + str(valor).replace('"', '\\"') + '"'


def serializar_frontmatter(dados: dict) -> str:
    linhas = ["---"]
    for chave, valor in dados.items():
        linhas.append(f"{chave}: {yaml_escalar(valor)}")
    linhas.append("---")
    return "\n".join(linhas) + "\n"


def corpo_do_template(caminho: pathlib.Path) -> str:
    """Corpo do template, sem cabeçalho e sem os blocos de instrução."""
    texto = ler(caminho)
    if texto.lstrip().startswith("---"):
        partes = texto.lstrip().split("---", 2)
        if len(partes) >= 3:
            texto = partes[2]
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return texto.strip("\n")


def desativar_links_quebrados(texto: str, raiz: pathlib.Path, pasta: pathlib.Path) -> str:
    """Troca exemplos de link do template (que não existem) por texto simples."""

    def trocar(match: re.Match) -> str:
        rotulo, alvo = match.group(1), match.group(2)
        if alvo.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        caminho = alvo.split("#")[0].strip()
        if not caminho.lower().endswith(".md"):
            return match.group(0)
        if (pasta / caminho).exists() or (raiz / caminho).exists():
            return match.group(0)
        return rotulo

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", trocar, texto)


def cmd_nova(raiz: pathlib.Path, **opcoes) -> int:
    tipo = (opcoes.get("tipo") or "").strip().lower()
    if tipo not in TIPOS_NOVA:
        print(f"Tipo inválido: {tipo!r}. Use um de: {', '.join(TIPOS_NOVA)}.")
        return 1

    nome = (opcoes.get("nome") or "").strip()
    if not nome:
        print("Informe o nome com --nome (ex.: --nome \"Habitus\").")
        return 1

    tema = (opcoes.get("tema") or "").strip().lower()
    if tema not in TEMAS:
        print(f"Tema inválido: {tema!r}. Use um de: {', '.join(sorted(TEMAS))}.")
        return 1

    template, pasta_nome, _ = TIPOS_NOVA[tipo]
    origem = raiz / "templates" / template
    if not origem.exists():
        print(f"Template não encontrado: {rel(origem, raiz)}.")
        return 1

    nivel = (opcoes.get("nivel") or "iniciante").strip().lower()
    if nivel not in NIVEIS_VALIDOS:
        print(f"Nível inválido: {nivel!r}. Use um de: {', '.join(sorted(NIVEIS_VALIDOS))}.")
        return 1

    autor = (opcoes.get("autor") or "").strip()
    obra = (opcoes.get("obra") or "").strip()
    data = (opcoes.get("data") or dt.date.today().isoformat()).strip()
    tags = parse_tags(opcoes.get("tags") or f"{tema}")
    if tema not in tags:
        tags = [tema, *tags]

    frente = {
        "conceito": {
            "conceito": nome,
            "obra_origem": obra,
            "autor_origem": autor,
            "tema": tema,
            "tipo": "conceito",
            "nivel": nivel,
            "status": "rascunho",
            "tags": tags,
        },
        "eixo": {
            "eixo": nome,
            "tema": tema,
            "tipo": "eixo",
            "nivel": nivel,
            "status": "rascunho",
            "tags": ["eixo", *tags],
        },
        "ficha": {
            "obra": obra or nome,
            "autor": autor,
            "ano": opcoes.get("ano") or "",
            "tema": tema,
            "tipo": "ficha-de-leitura",
            "status": "em-andamento",
            "tags": tags,
        },
        "trecho": {
            "obra": obra or nome,
            "autor": autor,
            "capitulo": opcoes.get("capitulo") or "",
            "pagina": opcoes.get("pagina") or "",
            "tema": tema,
            "tipo": "trecho",
            "tags": tags,
        },
        "diario": {
            "data": data,
            "tema": tema,
            "origem": opcoes.get("origem") or nome,
            "tipo": "diario",
            "tags": ["diario", *tags],
        },
    }[tipo]

    ident = slug(nome)
    if tipo == "conceito":
        arquivo = f"{tema}-{ident}.md"
    elif tipo == "eixo":
        arquivo = f"eixo-{ident}.md"
    elif tipo == "ficha":
        arquivo = f"{ident}-ficha.md"
    elif tipo == "diario":
        arquivo = f"{data}-{tema}-{ident}.md"
    else:
        arquivo = f"{ident}.md"

    pasta = raiz / pasta_nome
    destino = pasta / arquivo
    if destino.exists() and not opcoes.get("forcar"):
        print(f"Já existe: {rel(destino, raiz)}. Use --forcar para sobrescrever.")
        return 1

    corpo = corpo_do_template(origem)
    corpo = corpo.replace(ROTULO_H1[tipo], nome)
    corpo = desativar_links_quebrados(corpo, raiz, pasta)
    pendente = (
        "<!-- PENDENTE (padrão-ouro): preencha as seções e depois rode\n"
        f"     `python -m scripts.painel pendencias --tema {tema}`.\n"
        "     Ao terminar, mude o status para ok. -->\n"
    )
    conteudo = serializar_frontmatter(frente) + "\n" + pendente + corpo + "\n"

    pasta.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")
    print(f"Criado: {rel(destino, raiz)}")
    print()
    print("Próximos passos:")
    print(f"  1. preencha as seções (sem consultar a IA enquanto escreve)")
    print(f"  2. python -m scripts.painel pendencias --tema {tema}")
    print(f"  3. ao terminar, troque status: rascunho -> ok")
    return 0


def cmd_pendencias(raiz: pathlib.Path, **opcoes) -> int:
    """Checklist do padrão-ouro: o que falta em cada nota para virar `ok`."""
    registros = coletar_conceitos(raiz)
    tema = (opcoes.get("tema") or "").strip().lower()
    limite = opcoes.get("limite")
    mostrar_prontas = bool(opcoes.get("prontas"))

    if tema:
        if tema not in TEMAS:
            print(f"Tema inválido: {tema!r}. Use um de: {', '.join(sorted(TEMAS))}.")
            return 1
        registros = [r for r in registros if r["tema"] == tema]

    blocos, prontas = [], []
    for registro in registros:
        faltas = pendencias_da_nota(registro)
        if not faltas:
            prontas.append(registro)
            continue
        blocos.append((len(faltas), registro, faltas))

    blocos.sort(key=lambda item: (-item[0], item[2][0]))
    if limite:
        blocos = blocos[:limite]

    print("# Pendências para o padrão-ouro")
    if tema:
        print(f"# tema: {TEMAS[tema]}")
    print()

    if not blocos:
        print("Nenhuma pendência: as notas filtradas estão no padrão-ouro.")
    for quantidade, registro, faltas in blocos:
        print(f"{quantidade} pendência(s) — {registro['conceito']} ({rel(raiz / 'conceitos' / registro['arquivo'], raiz)})")
        for falta in faltas:
            print(f"    - {falta}")
        print()

    if mostrar_prontas and prontas:
        print("Já no padrão-ouro:")
        for registro in prontas:
            print(f"    ok  {registro['conceito']} ({registro['arquivo']})")
        print()

    total = len(registros)
    print(
        f"Resumo: {total} nota(s) analisada(s), {len(prontas)} pronta(s), "
        f"{total - len(prontas)} com pendência."
    )
    if limite and total - len(prontas) > limite:
        print(f"Mostrando as {limite} notas com mais pendências (use --limite para ver mais).")
    return 0


# ---------------------------------------------------------------------------
# Site (MkDocs Material)
# ---------------------------------------------------------------------------


def montar_site_src(raiz: pathlib.Path, destino: pathlib.Path | None = None) -> pathlib.Path:
    """Monta a pasta de fontes do site só com o que pode ser público."""
    import shutil

    destino = destino or (raiz / "site-src")
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    for nome in ARQUIVOS_SITE:
        origem = raiz / nome
        if not origem.exists():
            continue
        alvo = destino / ("index.md" if nome == "README.md" else nome)
        alvo.write_text(ler(origem), encoding="utf-8")

    # página de índice das tags (o plugin `tags` do Material preenche a lista)
    (destino / "tags.md").write_text(
        "# Tags\n\nTodas as etiquetas do painel, geradas a partir do frontmatter das notas.\n\n"
        "<!-- material/tags -->\n",
        encoding="utf-8",
    )

    for pasta in PASTAS_SITE:
        origem = raiz / pasta
        if origem.exists():
            shutil.copytree(origem, destino / pasta, dirs_exist_ok=True)

    # guias do projeto, sem os anexos de terceiros
    docs = raiz / "docs"
    if docs.exists():
        shutil.copytree(
            docs, destino / "docs", dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("anexos"),
        )

    # fichas de leitura (produção própria) — nunca o texto integral
    fichas = raiz / "acervo" / "fichas"
    if fichas.exists():
        shutil.copytree(fichas, destino / "acervo" / "fichas", dirs_exist_ok=True)

    return destino


def cmd_site(raiz: pathlib.Path, **opcoes) -> int:
    destino = raiz / "site-src"
    montar_site_src(raiz, destino)
    paginas = sorted(destino.rglob("*.md"))
    # os templates têm links de exemplo de propósito — não entram na checagem
    auditaveis = [p for p in paginas if "templates" not in p.relative_to(destino).parts]
    problemas = _links_quebrados(destino, auditaveis)
    print(f"site-src/ montado com {len(paginas)} página(s).")
    print("O texto integral do acervo e docs/anexos ficaram de fora.")
    if problemas:
        print(f"\nAviso: {len(problemas)} link(s) relativo(s) não resolvem no site:")
        for problema in problemas[:10]:
            print(f"  - {problema.replace(str(destino) + '/', '')}")
    else:
        print("Todos os links relativos resolvem dentro do site.")
    print()
    print("Para ver localmente:  mkdocs serve")
    print("Para gerar o HTML:    mkdocs build")
    return 0


def cmd_tudo(raiz: pathlib.Path) -> int:
    for comando in (cmd_indice, cmd_tabela, cmd_progresso, cmd_flashcards):
        codigo = comando(raiz)
        if codigo:
            return codigo
    return 0


COMANDOS = {
    "indice": cmd_indice,
    "tabela": cmd_tabela,
    "progresso": cmd_progresso,
    "flashcards": cmd_flashcards,
    "auditar": cmd_auditar,
    "tudo": cmd_tudo,
    "nova": cmd_nova,
    "pendencias": cmd_pendencias,
    "site": cmd_site,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manutenção do painel Humanitas (índice, tabelas, auditoria e flashcards)."
    )
    parser.add_argument(
        "--raiz",
        default=str(RAIZ_PADRAO),
        help="Raiz do repositório (padrão: pasta do projeto).",
    )
    parser.add_argument("comando", choices=COMANDOS)
    parser.add_argument(
        "--estrito",
        action="store_true",
        help="No comando auditar, tratar avisos como erro.",
    )

    grupo = parser.add_argument_group("nova")
    grupo.add_argument("--tipo", choices=sorted(TIPOS_NOVA), help="Tipo de nota a criar (nova).")
    grupo.add_argument("--nome", help="Nome do conceito, do eixo, da obra ou da reflexão (nova).")
    grupo.add_argument("--tema", help="Tema da nota (nova, pendencias).")
    grupo.add_argument("--nivel", help="iniciante | entusiasta | avancado (nova).")
    grupo.add_argument("--autor", help="Autor da obra (nova).")
    grupo.add_argument("--obra", help="Obra de origem (nova).")
    grupo.add_argument("--ano", help="Ano da obra (nova, ficha).")
    grupo.add_argument("--capitulo", help="Capítulo do trecho (nova, trecho).")
    grupo.add_argument("--pagina", help="Página do trecho (nova, trecho).")
    grupo.add_argument("--data", help="Data AAAA-MM-DD (nova, diario). Padrão: hoje.")
    grupo.add_argument("--origem", help="Módulo/conceito que gerou o diário (nova).")
    grupo.add_argument("--tags", help="Tags separadas por vírgula (nova).")
    grupo.add_argument("--forcar", action="store_true", help="Sobrescrever arquivo existente (nova).")
    grupo.add_argument("--limite", type=int, help="Máximo de notas listadas (pendencias).")
    grupo.add_argument("--prontas", action="store_true", help="Incluir as notas já prontas (pendencias).")

    args = parser.parse_args(argv)
    raiz = pathlib.Path(args.raiz).resolve()
    comando = COMANDOS[args.comando]
    if args.comando == "auditar":
        return comando(raiz, estrito=args.estrito)  # type: ignore[call-arg]
    if args.comando in ("nova", "pendencias"):
        opcoes = {
            chave: getattr(args, chave)
            for chave in (
                "tipo", "nome", "tema", "nivel", "autor", "obra", "ano", "capitulo",
                "pagina", "data", "origem", "tags", "forcar", "limite", "prontas",
            )
        }
        return comando(raiz, **opcoes)  # type: ignore[call-arg]
    return comando(raiz)


if __name__ == "__main__":
    sys.exit(main())
