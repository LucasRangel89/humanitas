from __future__ import annotations

import pathlib
import re

from .modelo import listar_md, rel, ler

# Afirmações (relatório para conferência manual)
# ---------------------------------------------------------------------------

REGEX_AFIRMACOES_PERCENT = re.compile(r"\d+\s*%")
REGEX_AFIRMACOES_ESTUDOS = re.compile(r"estudos?\s+mostram|pesquisas?\s+indicam", re.I)
REGEX_AFIRMACOES_ANO = re.compile(r"\b(19|20)\d{2}\b")
REGEX_AFIRMACOES_SUPERLATIVO = re.compile(
    r"\b\w*íssim[oa]s?\b|\b\w*érrim[oa]s?\b|\b(supremo|máximo|mínimo|melhor|pior|maior|menor|totalmente|absolutamente|completamente|extremamente|sempre|nunca|todos?|todas|jamais)\b",
    re.I,
)


def _afirmacoes_do_texto(texto: str) -> list[tuple[str, str]]:
    """Devolve lista de (categoria, trecho) encontradas no texto."""
    if texto.lstrip().startswith("---"):
        partes = texto.lstrip().split("---", 2)
        if len(partes) >= 3:
            texto = partes[2]
    achados: list[tuple[str, str]] = []
    for linha in texto.splitlines():
        limpa = linha.strip()
        if not limpa or limpa.startswith("#") or limpa.startswith("|"):
            continue
        if REGEX_AFIRMACOES_PERCENT.search(limpa):
            achados.append(("porcentagem", limpa))
        if REGEX_AFIRMACOES_ESTUDOS.search(limpa):
            achados.append(("estudos/pesquisas", limpa))
        if REGEX_AFIRMACOES_ANO.search(limpa):
            achados.append(("ano", limpa))
        if REGEX_AFIRMACOES_SUPERLATIVO.search(limpa):
            achados.append(("superlativo", limpa))
    return achados


def coletar_afirmacoes(raiz: pathlib.Path) -> dict[str, list[tuple[str, str]]]:
    """Mapeia caminho -> lista de afirmações encontradas."""
    resultado: dict[str, list[tuple[str, str]]] = {}
    for arq in listar_md(raiz / "conceitos", recursivo=True):
        texto = ler(arq)
        achados = _afirmacoes_do_texto(texto)
        if achados:
            resultado[rel(arq, raiz)] = achados
    return resultado


def gerar_relatorio_afirmacoes(raiz: pathlib.Path) -> str:
    coletados = coletar_afirmacoes(raiz)
    linhas = [
        "# Relatório de afirmações a conferir",
        "",
        "> Gerado automaticamente por `python -m scripts.painel afirmacoes`. Não edite à mão.",
        "> Este arquivo é ignorado pelo Git — revise manualmente cada afirmação e atualize a nota com fonte verificável quando necessário.",
        "",
        "Este relatório lista, por nota, frases que contêm números/porcentagens, as expressões “estudos mostram” / “pesquisas indicam”, anos (1900–2099) e superlativos, para conferência manual pelo autor.",
        "",
        f"Total de notas com possíveis afirmações: {len(coletados)}.",
        "",
    ]
    if not coletados:
        linhas += ["Nenhuma afirmação encontrada — nada a conferir."]  # sem gatilho, mas limpo
    else:
        for caminho in sorted(coletados):
            linhas += [f"## {caminho}", ""]
            for categoria, trecho in coletados[caminho]:
                # escapa quebras
                trecho_c = trecho.replace("|", "\\|").strip()
                # limita tamanho
                if len(trecho_c) > 200:
                    trecho_c = trecho_c[:197] + "..."
                linhas.append(f"- **{categoria}**: {trecho_c}")
            linhas.append("")
    return "\n".join(linhas)


def cmd_afirmacoes(raiz: pathlib.Path) -> int:
    destino = raiz / "relatorio-afirmacoes.md"
    conteudo = gerar_relatorio_afirmacoes(raiz)
    destino.write_text(conteudo, encoding="utf-8")
    total = sum(len(v) for v in coletar_afirmacoes(raiz).values())
    print(f"{rel(destino, raiz)} gerado com {total} afirmação(ões) em {len(coletar_afirmacoes(raiz))} nota(s).")
    return 0


