from __future__ import annotations

import json
import pathlib
from collections import Counter, defaultdict

from .indice import montar_indice


def agrupar_obras(indice: dict) -> dict:
    """Agrupa conceitos por obra_origem e autor_origem."""
    obras = defaultdict(lambda: {"autor": "", "conceitos": [], "temas": Counter(), "count": 0})
    autores = defaultdict(lambda: {"obras": set(), "conceitos": [], "count": 0})
    for c in indice.get("conceitos", []):
        obra = c.get("obra_origem", "").strip() or "Sem obra"
        autor = c.get("autor_origem", "").strip() or "Desconhecido"
        obras[obra]["autor"] = autor
        obras[obra]["conceitos"].append({"conceito": c["conceito"], "arquivo": c["arquivo"], "tema": c["tema"]})
        obras[obra]["temas"][c["tema"]] += 1
        obras[obra]["count"] += 1
        autores[autor]["obras"].add(obra)
        autores[autor]["conceitos"].append(c["conceito"])
        autores[autor]["count"] += 1
    # converte para serializável
    obras_out = {}
    for obra, dados in obras.items():
        obras_out[obra] = {
            "autor": dados["autor"],
            "total": dados["count"],
            "temas": dict(dados["temas"]),
            "conceitos": dados["conceitos"],
        }
    autores_out = {}
    for autor, dados in autores.items():
        autores_out[autor] = {
            "total": dados["count"],
            "obras": sorted(dados["obras"]),
            "conceitos": dados["conceitos"],
        }
    return {"obras": obras_out, "autores": autores_out, "atualizado_em": indice.get("atualizado_em", "")}


def gravar_obras(raiz: pathlib.Path, dados: dict) -> pathlib.Path:
    caminho = raiz / "indices" / "obras.json"
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


def cmd_obras(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    dados = agrupar_obras(indice)
    caminho = gravar_obras(raiz, dados)
    print(f"{caminho.relative_to(raiz)} gerado: {len(dados['obras'])} obras, {len(dados['autores'])} autores.")
    return 0
