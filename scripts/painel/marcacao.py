from __future__ import annotations

import pathlib
import re

from .modelo import REGEX_CHECKBOX, ler, rel

# ---------------------------------------------------------------------------
# Progresso marcado no site (localStorage) -> arquivos de trilha
# ---------------------------------------------------------------------------
#
# O site é estático: um clique numa caixa de seleção não pode escrever no
# repositório. A solução é um vaivém explícito e auditável:
#
#   1. no site, você marca os nós (fica no localStorage do navegador);
#   2. o botão "Exportar" baixa um progresso.json;
#   3. `make aplicar-progresso ARQUIVO=progresso.json` grava as marcações nos
#      arquivos de trilha — e é isso que entra no commit e no progresso.md.
#
# Formato do arquivo (versão 1):
#
#   {
#     "versao": 1,
#     "exportado_em": "2026-10-23T12:00:00Z",
#     "trilhas": {"antropologia-nivel-1": [0, 2], "historia-nivel-1": [0]}
#   }
#
# Os números são as posições (0-based) dos nós na ordem em que aparecem no
# arquivo — a mesma ordem que o painel usa para contar `nos_concluidos`.

VERSAO = 1


def _normalizar_indices(valor) -> set[int]:
    """Aceita [0, 2] ou {"checks": [0, 2]} e devolve um conjunto de inteiros."""
    if isinstance(valor, dict):
        valor = valor.get("checks") or valor.get("indices") or []
    if not isinstance(valor, (list, tuple)):
        return set()
    indices = set()
    for item in valor:
        try:
            indice = int(item)
        except (TypeError, ValueError):
            continue
        if indice >= 0:
            indices.add(indice)
    return indices


def aplicar_progresso(
    dados: dict,
    raiz: pathlib.Path,
    *,
    gravar: bool = False,
) -> tuple[list[str], list[str]]:
    """Aplica um progresso exportado aos arquivos de trilha.

    Devolve (mudancas, avisos). Sem `gravar=True` nada é escrito — serve de
    simulação para conferir antes de commitar.
    """
    mudancas: list[str] = []
    avisos: list[str] = []

    if not isinstance(dados, dict):
        return [], ["Arquivo de progresso inválido: esperado um objeto JSON."]
    trilhas = dados.get("trilhas")
    if not isinstance(trilhas, dict):
        return [], ["Arquivo de progresso sem a chave 'trilhas'."]

    for slug, bruto in sorted(trilhas.items()):
        alvo = raiz / "trilhas" / f"{slug}.md"
        if not alvo.exists():
            avisos.append(f"Trilha não encontrada, ignorada: trilhas/{slug}.md")
            continue

        texto = ler(alvo)
        achados = list(REGEX_CHECKBOX.finditer(texto))
        if not achados:
            avisos.append(
                f"trilhas/{slug}.md não tem nós no formato de caixa de seleção; ignorada."
            )
            continue

        desejados = _normalizar_indices(bruto)
        fora = [i for i in desejados if i >= len(achados)]
        if fora:
            avisos.append(
                f"trilhas/{slug}.md tem {len(achados)} nó(s); índice(s) ignorado(s): "
                + ", ".join(str(i) for i in sorted(fora))
            )

        # Reescreve de trás para frente para não deslocar as posições.
        novo = texto
        alterados = []
        for indice in range(len(achados) - 1, -1, -1):
            achado = achados[indice]
            marca_atual = achado.group(1)
            marca_nova = "x" if indice in desejados and indice < len(achados) else " "
            if marca_atual.strip().lower() == marca_nova.strip().lower():
                continue
            novo = novo[: achado.start(1)] + marca_nova + novo[achado.end(1) :]
            alterados.append(indice + 1)

        if alterados:
            alterados.sort()
            mudancas.append(
                f"trilhas/{slug}.md: nó(s) {', '.join(str(i) for i in alterados)} "
                f"→ agora {'marcado(s)' if desejados else 'desmarcado(s)'}"
            )

        # O status da trilha acompanha os nós: concluída quando todos estão feitos.
        concluidos = [i for i in range(len(achados)) if i in desejados]
        todos = len(achados) > 0 and len(concluidos) == len(achados)
        status_novo = None
        if todos and "status: concluida" not in novo:
            status_novo = ("em-andamento", "concluida")
        elif not todos and "status: concluida" in novo:
            status_novo = ("concluida", "em-andamento")
        # Só o campo do frontmatter conta: o corpo da trilha cita a palavra
        # "concluida" nas instruções de fechamento.
        campo = re.compile(r"^status:\s*(em-andamento|concluida)\s*$", re.M)
        achado_status = campo.search(novo)
        status_novo = None
        if achado_status:
            atual = achado_status.group(1)
            if todos and atual == "em-andamento":
                status_novo = ("em-andamento", "concluida")
            elif not todos and atual == "concluida":
                status_novo = ("concluida", "em-andamento")
        if status_novo:
            novo = (
                novo[: achado_status.start(1)]
                + status_novo[1]
                + novo[achado_status.end(1) :]
            )
            mudancas.append(
                f"trilhas/{slug}.md: status {status_novo[0]} → {status_novo[1]}"
            )
            alterados = alterados or [-1]

        if novo != texto and gravar and (alterados or status_novo):
            alvo.write_text(novo, encoding="utf-8")

    if not mudancas and not avisos:
        avisos.append("Nada a fazer: o progresso exportado já está refletido nas trilhas.")
    return mudancas, avisos
