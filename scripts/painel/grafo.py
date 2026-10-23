from __future__ import annotations

import json
import pathlib

from .indice import montar_indice


def montar_grafo(indice: dict) -> dict:
    """Constrói grafo a partir de relacoes e eixos dos conceitos."""
    nodes = []
    edges = []
    # índice por nome conceito para resolver alvo
    nome_para_arquivo = {c["conceito"]: c["arquivo"] for c in indice.get("conceitos", [])}
    for c in indice.get("conceitos", []):
        nodes.append({
            "id": c["arquivo"],
            "conceito": c["conceito"],
            "tema": c.get("tema", ""),
            "tipo": c.get("tipo", "conceito"),
            "tradicao": c.get("tradicao", ""),
            "nivel_evidencia": c.get("nivel_evidencia", ""),
            "eixos": c.get("eixos", []),
        })
        # relacoes -> edges
        for rel in c.get("relacoes", []) or []:
            alvo = None
            tipo = "relacionado"
            if isinstance(rel, dict):
                alvo = rel.get("alvo") or rel.get("target")
                tipo = rel.get("tipo", tipo)
            elif isinstance(rel, str):
                alvo = rel
            if not alvo:
                continue
            # tenta resolver por nome ou arquivo
            target_file = nome_para_arquivo.get(alvo) or alvo
            # normaliza para arquivo.md se não tiver extensão
            if "." not in target_file:
                target_file = f"{target_file}.md"
            edges.append({
                "source": c["arquivo"],
                "target": target_file,
                "tipo": tipo,
            })
        # eixos -> edges para eixos
        for eixo in c.get("eixos", []) or []:
            if not eixo:
                continue
            target_file = nome_para_arquivo.get(eixo) or eixo
            if "." not in target_file:
                target_file = f"{target_file}.md"
            edges.append({
                "source": c["arquivo"],
                "target": target_file,
                "tipo": "eixo",
            })
    return {
        "nodes": nodes,
        "edges": edges,
        "atualizado_em": indice.get("atualizado_em", ""),
        "totais": {
            "nodes": len(nodes),
            "edges": len(edges),
        }
    }


def gravar_grafo(raiz: pathlib.Path, grafo: dict) -> pathlib.Path:
    caminho = raiz / "indices" / "grafo.json"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    # compara sem timestamp
    comparavel = {k: v for k, v in grafo.items() if k != "atualizado_em"}
    if caminho.exists():
        try:
            anterior = json.loads(caminho.read_text(encoding="utf-8"))
            anterior_comparavel = {k: v for k, v in anterior.items() if k != "atualizado_em"}
            if anterior_comparavel == comparavel:
                return caminho
        except Exception:
            pass
    caminho.write_text(json.dumps(grafo, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return caminho


def cmd_grafo(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    grafo = montar_grafo(indice)
    caminho = gravar_grafo(raiz, grafo)
    print(f"{caminho.relative_to(raiz)} gerado: {grafo['totais']['nodes']} nós, {grafo['totais']['edges']} arestas.")
    return 0
