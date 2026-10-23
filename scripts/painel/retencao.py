from __future__ import annotations

import json
import pathlib
from collections import Counter

from .indice import montar_indice
from .cartoes import gerar_flashcards


def calcular_retencao(indice: dict, cartoes: list[list[str]] | None = None) -> dict:
    """Calcula métricas simples de retenção com base em status e cartões."""
    conceitos = indice.get("conceitos", [])
    total = len(conceitos)
    por_status = Counter(c.get("status", "sem") for c in conceitos)
    por_nivel = Counter(c.get("nivel", "sem") for c in conceitos)
    por_tema = Counter(c.get("tema", "sem") for c in conceitos)
    # cartões por tema (via tags)
    if cartoes is None:
        # gera rapidamente sem gravar
        from .cartoes import gerar_flashcards
        # evita circular: montar_indice já tem, mas aqui passamos indice
        # gerar_flashcards precisa coletar_conceitos internamente, então passamos None e recalcula
        # para simplificar, não usamos cartoes aqui; calculamos depois se fornecido
        cartoes = []
    cartoes_por_tema = Counter()
    for c in cartoes:
        # c = [guid, frente, verso, tags, baralho]; baralho é "Humanitas::Tema"
        baralho = c[4] if len(c) > 4 else ""
        tema = baralho.split("::")[-1].lower() if "::" in baralho else "geral"
        cartoes_por_tema[tema] += 1
    taxa_ok = por_status.get("ok", 0) / total if total else 0
    return {
        "total_conceitos": total,
        "por_status": dict(por_status),
        "por_nivel": dict(por_nivel),
        "por_tema": dict(por_tema),
        "total_cartoes": len(cartoes),
        "cartoes_por_tema": dict(cartoes_por_tema),
        "taxa_ok": round(taxa_ok, 3),
        "atualizado_em": indice.get("atualizado_em", ""),
    }


def gravar_retencao(raiz: pathlib.Path, dados: dict) -> pathlib.Path:
    caminho = raiz / "indices" / "retencao.json"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    comparavel = {k: v for k, v in dados.items() if k != "atualizado_em"}
    if caminho.exists():
        try:
            anterior = json.loads(caminho.read_text(encoding="utf-8"))
            anterior_comparavel = {k: v for k, v in anterior.items() if k != "atualizado_em"}
            if anterior_comparavel == comparavel:
                return caminho
        except Exception:
            pass
    caminho.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return caminho


def cmd_retencao(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    cartoes = gerar_flashcards(raiz, indice)
    dados = calcular_retencao(indice, cartoes)
    caminho = gravar_retencao(raiz, dados)
    print(f"{caminho.relative_to(raiz)} gerado: {dados['total_conceitos']} conceitos, {dados['total_cartoes']} cartões, taxa ok {dados['taxa_ok']:.0%}.")
    return 0
