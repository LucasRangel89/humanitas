from __future__ import annotations

import pathlib
import re
import uuid
from collections import Counter

from .modelo import TEMAS, REGEX_SECAO, normalizar, achar_secao, extrair_secao, limpar_markdown, eh_placeholder
from .indice import coletar_conceitos, montar_indice

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

    # PR4: cartões extras para tradição e nível de evidência
    tradicao = registro.get("tradicao", "")
    if tradicao and not eh_placeholder(tradicao):
        adicionar("tradicao", f"Qual tradição/escola está associada a {nome}?", tradicao)
    nivel_evidencia = registro.get("nivel_evidencia", "")
    if nivel_evidencia:
        adicionar("nivel_evidencia", f"Qual o nível de evidência de {nome}?", nivel_evidencia)
    # relações como pista (sem criar cartão por cada, mas um cartão agregado)
    rels = registro.get("relacoes") or []
    if rels:
        rel_text = ", ".join(r.get("alvo") if isinstance(r, dict) else str(r) for r in rels)
        if rel_text:
            adicionar("relacoes", f"Com quais conceitos {nome} se relaciona?", rel_text)

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


