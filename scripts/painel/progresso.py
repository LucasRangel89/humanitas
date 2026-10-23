from __future__ import annotations

import datetime as dt
import pathlib
import re
from collections import Counter

from .modelo import TEMAS, SECOES_OBRIGATORIAS, SECAO_TRECHO, MARCADOR_PROGRESSO, MARCADOR_TEMAS, eh_placeholder, achar_secao, extrair_secao, limpar_markdown, ler, rel, normalizar, sem_codigo, substituir_bloco

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
    if registro.get("fonte_verificada") != "sim":
        faltas.append("fonte verificada")
    if registro.get("status") != "ok":
        faltas.append("status ainda é rascunho")
    return faltas


def calcular_progresso(indice: dict) -> dict:
    conceitos = indice["conceitos"]
    status = Counter(c["status"] or "sem-status" for c in conceitos)
    ok = status.get("ok", 0)
    rascunho = status.get("rascunho", 0)
    com_trecho = sum(1 for c in conceitos if c.get("tem_trecho"))
    fonte_secundaria = re.compile(r"guia de estudos|planos de estudo|anexo|wikip", re.I)
    com_fonte_primaria = sum(
        1
        for c in conceitos
        if c.get("obra_origem") and not fonte_secundaria.search(c["obra_origem"])
    )
    com_fonte_verificada = sum(1 for c in conceitos if c.get("fonte_verificada") == "sim")
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
        "fonte_verificada": com_fonte_verificada,
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


# Marcos que destravam decisões registradas no Guia 07 (Fase 4 / métricas).
MARCOS_DECISAO = (
    ("ok", "Notas reescritas (`ok`)", 25, "Migrar o site (Astro) — Guia 07, Fase 4"),
    ("diario_total", "Entradas de diário", 12, "Migrar o site (Astro) — Guia 07, Fase 4"),
    ("com_trecho", "Notas com citação de apoio", 25, "Meta de 90 dias (Guia 07)"),
    ("fichas", "Fichas de leitura", 3, "Meta de 90 dias (Guia 07)"),
)


def marcos_de_decisao(indice: dict) -> list[tuple[str, int, int, str, bool]]:
    """(rótulo, atual, alvo, porquê, atingido) de cada marco."""
    p = calcular_progresso(indice)
    return [
        (rotulo, p[campo], alvo, motivo, p[campo] >= alvo)
        for campo, rotulo, alvo, motivo in MARCOS_DECISAO
    ]


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
        f"| Notas com fonte verificada | {p['fonte_verificada']} |",
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
        "| Tema | Notas | ok | rascunho | Com citação | Fonte primária | Fonte verificada |",
        "|---|---|---|---|---|---|---|",
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
            f"{sum(1 for c in do_tema if c['obra_origem'] and not re.search('guia de estudos|planos de estudo|anexo|wikip', c['obra_origem'], re.I))} | "
            f"{sum(1 for c in do_tema if c.get('fonte_verificada') == 'sim')} |"
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
    marcos = marcos_de_decisao(indice)
    linhas += [
        "",
        "## Marcos de decisão",
        "",
        "Gatilhos registrados no [Guia 07](docs/07-rumos-e-proximos-passos.md#fase-4-ferramenta-do-site-quando-migrar). "
        "Quando um marco é atingido, a decisão correspondente pode ser reavaliada — "
        "não antes.",
        "",
        "| Marco | Atual | Alvo | Situação | O que destrava |",
        "|---|---|---|---|---|",
    ]
    for rotulo, atual, alvo, motivo, atingido in marcos:
        falta = alvo - atual
        situacao = "✔ atingido" if atingido else f"faltam {falta}" if falta > 1 else "falta 1"
        linhas.append(f"| {rotulo} | {atual} | {alvo} | {situacao} | {motivo} |")
    pendentes = [(rotulo, alvo - atual) for rotulo, atual, alvo, _, ok in marcos if not ok]
    linhas += [
        "",
        (
            "Enquanto houver marco pendente: **escreva notas**, não troque de ferramenta."
            if pendentes
            else "Todos os marcos atingidos: hora de reavaliar as decisões do Guia 07."
        ),
    ]

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
        f"| Notas com fonte verificada | {p['fonte_verificada']} de {p['conceitos']} |",
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


