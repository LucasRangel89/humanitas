from __future__ import annotations

import html
import json as _json
import pathlib
import re
import shutil
from collections import Counter

from .modelo import TEMAS, PASTAS_SITE, ARQUIVOS_SITE, ler, listar_md
from .indice import montar_indice
from .progresso import calcular_progresso, progresso_barra
from .midias import (
    carregar as carregar_midias,
    cobertura_trilhas,
    titulos_dos_conceitos,
)
from .auditoria import _links_quebrados
from .livro import (
    CORES_TEMA,
    PARTES_LIVRO,
    enriquecer_nota_conceito,
    enriquecer_pagina_trilha,
    gerar_pagina_midias_interativa,
    indexar_aparicoes_em_trilhas,
    indexar_estante_por_conceito_e_trilha,
    mapear_volumes_ordenados,
    transformar_estante_editorial,
    url_site,
)

# Site (MkDocs Material — Edição Livro Digital Interativo)
# ---------------------------------------------------------------------------


def barra(feitos: int, total: int, largura: int = 10) -> str:
    """Barra de progresso em blocos, para sumários e tabelas."""
    if total <= 0:
        return "—"
    preenchido = round(largura * feitos / total)
    return "█" * preenchido + "░" * (largura - preenchido)


GLIFO_STATUS = {"ok": "✔", "rascunho": "○", "arquivada": "·"}


def _link_nota(registro: dict, prefixo: str = "conceitos/") -> str:
    """Link relativo para uma nota de conceito/eixo."""
    alvo = registro.get("caminho") or f"conceitos/{registro['arquivo']}"
    if alvo.startswith("conceitos/"):
        alvo = alvo[len("conceitos/") :]
    return f"[{registro['conceito']}]({prefixo}{alvo})"


def _obras_reais(obras_dict: dict) -> list[tuple[str, dict]]:
    """Filtra 'Sem obra', guias internos e anexos para destacar obras autorais de verdade."""
    ruido = re.compile(r"sem obra|guia de estudos|planos? de estudo|anexo", re.I)
    validas = [
        (obra, dados)
        for obra, dados in obras_dict.items()
        if not ruido.search(obra) and dados.get("autor") and dados.get("autor") != "Desconhecido"
    ]
    return sorted(validas, key=lambda kv: (-kv[1]["total"], kv[0]))


def pagina_dashboard(
    indice: dict,
    *,
    qtd_midias: int = 0,
    tem_midias: bool = False,
    tem_estante: bool = False,
    tem_prioridades: bool = False,
) -> str:
    """Capa & Sumário Editorial do Livro Digital Interativo."""
    p = calcular_progresso(indice)
    temas = Counter(c["tema"] for c in indice["conceitos"])
    eixos = sorted(
        [c for c in indice["conceitos"] if c.get("tipo") == "eixo"],
        key=lambda c: c["conceito"],
    )
    volumes = mapear_volumes_ordenados(indice["trilhas"])
    pct_nos = (p["nos_concluidos"] * 100 // p["nos_total"]) if p["nos_total"] else 0
    pct_ok = (p["ok"] * 100 // p["conceitos"]) if p["conceitos"] else 0

    # Escolhe o primeiro volume recomendado (Filosofia ou primeiro não concluído na ordem curada)
    proxima_trilha = next(
        (v for v in volumes if v["nos_total"] and v["status"] != "concluida"),
        volumes[0] if volumes else None,
    )

    try:
        from .obras import agrupar_obras as _agrupar_obras_dashboard
        obras_data = _agrupar_obras_dashboard(indice)
    except Exception:
        obras_data = {"obras": {}}

    cta_url = url_site("index.md", f"trilhas/{proxima_trilha['arquivo']}" if proxima_trilha else "trilhas/index.md")
    cta_nome = proxima_trilha["trilha"].split(":")[0] if proxima_trilha else "Sumário dos Volumes"

    botao_midias = (
        f'  <a class="eb-btn-secondary" href="{url_site("index.md", "midias.md")}">🎬 Cinemateca & Videoaulas</a>'
        if tem_midias
        else f'  <a class="eb-btn-secondary" href="{url_site("index.md", "obras.md")}">📚 Obras & Autores</a>'
    )

    links_acervo = []
    if tem_midias:
        links_acervo.append("[Cinemateca & Aulas →](midias.md)")
    if tem_estante:
        links_acervo.append("[Estante de Obras →](estante.md)")
    links_acervo.append("[Obras & Autores →](obras.md)")

    linhas = [
        '<section class="humanitas-hero eb-book-cover" markdown>',
        "",
        '<div class="eb-cover-kicker">Livro Digital Interativo · Ciências Humanas</div>',
        "",
        "# Humanitas",
        "",
        '<p class="eb-cover-subtitle">Uma travessia guiada pela Filosofia, Psicologia, Sociologia, Antropologia, '
        "História, Geografia, Ciência Política e Economia — com ensaios conceituais, grandes debates e "
        "aulas verificadas integradas em cada capítulo.</p>",
        "",
        '<div class="eb-cover-actions" id="eb-continue-banner">',
        f'  <a class="eb-btn-primary" id="eb-primary-cta" href="{cta_url}">📖 Abrir Volume I · {html.escape(cta_nome)}</a>',
        f'  <a class="eb-btn-secondary" href="{url_site("index.md", "conceitos/index.md")}">🧭 Explorar Atlas de Conceitos</a>',
        botao_midias,
        "</div>",
        "",
        '<div class="eb-cover-colophon">',
        f"  <span><strong>{len(volumes)}</strong> volumes guiados</span> · ",
        f"  <span><strong>{p['conceitos']}</strong> ensaios e eixos</span> · ",
        *(
            [f"  <span><strong>{qtd_midias}</strong> mídias integradas</span> · "]
            if tem_midias
            else []
        ),
        f"  <span><strong>{len(eixos)}</strong> grandes debates</span>",
        "</div>",
        "",
        "</section>",
        "",
        "## Como ler esta obra",
        "",
        '<div class="grid cards eb-entry-cards" markdown>',
        "",
        "-   :material-book-open-page-variant:{ .lg .middle } **1. Ler em sequência (Os Volumes)**",
        "",
        "    ---",
        "",
        "    Cada trilha foi organizada como um **volume com capítulos encadeados**: tese central, ensaio, videoaula na própria página e prática reflexiva.",
        "",
        f"    [Ir ao Sumário dos {len(volumes)} Volumes →](trilhas/index.md)",
        "",
        "-   :material-compass-outline:{ .lg .middle } **2. Navegar pelas grandes questões (Eixos)**",
        "",
        "    ---",
        "",
        f"    **{len(eixos)} debates transversais** — como *Estrutura × Agência*, *Mente × Corpo* e *Natureza × Cultura* — costuram autores de épocas e disciplinas distintas.",
        "",
        "    [Abrir Mapa de Debates →](eixos.md) · [Grafo vivo →](grafo.md)",
        "",
        "-   :material-play-box-multiple-outline:{ .lg .middle } **3. Aulas, Cinema e Obras**",
        "",
        "    ---",
        "",
        "    Aulas universitárias, cursos abertos, artigos e obras de referência aparecem **dentro de cada parada do livro** e também reunidos para consulta.",
        "",
        "    " + " · ".join(links_acervo),
        "",
        "-   :material-progress-check:{ .lg .middle } **Onde você está**",
        "",
        "    ---",
        "",
        f"    - Paradas concluídas: **{p['nos_concluidos']} de {p['nos_total']}** `{barra(p['nos_concluidos'], p['nos_total'])}` ({pct_nos}%)",
        f"    - Notas autorais (`ok`): **{p['ok']} de {p['conceitos']}** `{progresso_barra(p['ok'], p['conceitos'])}` ({pct_ok}%)",
        f"    - Citações verificadas: **{p['com_trecho']}** · Diários escritos: **{p['diario_total']}**",
        "",
        "    [Caderno & Diário →](registrar.md) · [Relatório completo →](progresso.md)",
        "",
        "</div>",
        "",
        "## Trilhas e Volumes — Sumário Geral",
        "",
        '<p class="eb-section-lead">O livro divide-se em três partes complementares: comece pelas fundações clássicas, '
        "expanda o repertório histórico-espacial ou vá direto às sínteses interdisciplinares.</p>",
        "",
    ]

    # Agrupa os volumes por Parte do livro
    partes_vistas: dict[str, list[dict]] = {}
    desc_partes: dict[str, str] = {}
    for v in volumes:
        p_nome = v["parte_nome"]
        partes_vistas.setdefault(p_nome, []).append(v)
        desc_partes[p_nome] = v["parte_desc"]

    for p_nome, vols_parte in partes_vistas.items():
        linhas += [
            f"### {p_nome}",
            "",
            f"*{desc_partes.get(p_nome, '')}*",
            "",
            '<div class="eb-volume-grid">',
        ]
        for v in vols_parte:
            cor = CORES_TEMA.get(v["tema"], "#3b4cca")
            titulo_curto, _, subtitulo = v["trilha"].partition(":")
            objetivo = (v.get("objetivo") or subtitulo or "").strip()
            if len(objetivo) > 190:
                objetivo = objetivo[:187].rstrip() + "…"
            proximo = (v.get("proximo_no") or "").split("—")[0].strip()
            pct_v = (v["nos_concluidos"] * 100 // v["nos_total"]) if v["nos_total"] else 0

            href_v = url_site("index.md", f"trilhas/{v['arquivo']}")
            linhas.append(
                f'<a class="eb-volume-card" href="{href_v}" data-trilha-slug="{v["arquivo"].removesuffix(".md")}" data-trilha-total="{v["nos_total"]}" style="--tema-cor:{cor}">'
                f'  <div class="eb-vol-spine"></div>'
                f'  <div class="eb-vol-content">'
                f'    <div class="eb-vol-top">'
                f'      <span class="eb-vol-num">Volume {v["volume_romano"]}</span>'
                f'      <span class="eb-vol-theme">{html.escape(TEMAS.get(v["tema"], v["tema"]))}</span>'
                f"    </div>"
                f'    <h4 class="eb-vol-title">{html.escape(titulo_curto.strip())}</h4>'
                + (f'    <div class="eb-vol-sub">{html.escape(subtitulo.strip())}</div>' if subtitulo.strip() else "")
                + f'    <p class="eb-vol-desc">{html.escape(objetivo)}</p>'
                f'    <div class="eb-vol-footer">'
                f'      <span class="eb-vol-stops">{v["nos_concluidos"]}/{v["nos_total"]} paradas · {pct_v}%</span>'
                + (f'      <span class="eb-vol-next">Começa em: {html.escape(proximo[:38])}</span>' if proximo else "")
                + "    </div>"
                "  </div>"
                "</a>"
            )
        linhas += ["</div>", ""]

    # Seção de Eixos / Bússolas de Debate
    if eixos:
        linhas += [
            "## As Bússolas — Grandes Eixos de Debate",
            "",
            '<p class="eb-section-lead">Em ciências humanas, conceitos não são definições isoladas: são respostas '
            "diferentes às mesmas perguntas permanentes. Use estes eixos para situar cada autor.</p>",
            "",
            '<div class="eb-axis-strip">',
        ]
        for ex in eixos[:8]:
            cor = CORES_TEMA.get(ex["tema"], "#7a3e2e")
            href_ex = url_site("index.md", f"conceitos/{ex['arquivo']}")
            linhas.append(
                f'<a class="eb-axis-card" href="{href_ex}" style="--tema-cor:{cor}">'
                f'  <span class="eb-axis-kicker">Eixo · {html.escape(TEMAS.get(ex["tema"], ex["tema"]))}</span>'
                f'  <strong>{html.escape(ex["conceito"])}</strong>'
                f'  <p>{html.escape((ex["definicao"] or "")[:135])}{"…" if len(ex.get("definicao","")) > 135 else ""}</p>'
                f"</a>"
            )
        linhas += [
            "</div>",
            "",
            f"[Explorar todos os {len(eixos)} eixos de debate →](eixos.md)",
            "",
        ]

    # Atlas de Temas e disciplinas (mantém visibilidade por área e progresso compatível com testes)
    linhas += [
        "## Temas e Disciplinas do Acervo",
        "",
        "| Tema | Ensaios | Revisados (`ok`) | Com citação | Maturidade |",
        "|---|---|---|---|---|",
    ]
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        do_tema = [c for c in indice["conceitos"] if c["tema"] == tema]
        ok = sum(1 for c in do_tema if c["status"] == "ok")
        cit = sum(1 for c in do_tema if c["tem_trecho"])
        linhas.append(
            f"| [{TEMAS.get(tema, tema)}](conceitos/index.md#{tema}) | {qtd} | {ok} | {cit} | `{barra(ok, qtd)}` |"
        )

    linhas += [
        "",
        "## Mapa de Conexões — Como as ideias dialogam",
        "",
        '<p class="eb-section-lead">Passe o cursor para inspecionar as pontes entre conceitos e eixos; clique em qualquer nó para abrir o ensaio correspondente.</p>',
        "",
        '<div class="grafo-container">',
        '  <canvas id="grafo-canvas" width="960" height="420" aria-label="Grafo interativo de conceitos"></canvas>',
        "</div>",
        '<div class="grafo-legend">',
        '  <span><span class="dot" style="background:#2d6a64"></span> Filosofia</span>',
        '  <span><span class="dot" style="background:#3b4cca"></span> Sociologia</span>',
        '  <span><span class="dot" style="background:#b85d19"></span> Psicologia</span>',
        '  <span><span class="dot" style="background:#8c3b5a"></span> Antropologia</span>',
        '  <span><span class="dot" style="background:#7c5832"></span> História</span>',
        '  <span><span class="dot" style="background:#2f6f4e"></span> Geografia</span>',
        '  <span><span class="dot" style="background:#5b3e82"></span> Ciência Política</span>',
        '  <span><span class="dot" style="background:#1f5f7a"></span> Economia</span>',
        '  <span><span class="dot" style="background:#c0392b"></span> Eixo de debate</span>',
        "</div>",
        "",
        "[Abrir mapa de conexões em tela ampla →](grafo.md)",
        "",
    ]

    obras_limpas = _obras_reais(obras_data.get("obras", {}))
    if obras_limpas:
        linhas += [
            "## Obras Clássicas e Contemporâneas Citadas",
            "",
            '<div class="obra-list">',
        ]
        for obra, dados in obras_limpas[:4]:
            tags_html = "".join(
                f'<a class="tag" href="{url_site("index.md", "conceitos/" + c["arquivo"])}">{html.escape(c["conceito"])}</a>'
                for c in dados["conceitos"][:5]
            )
            linhas.append(
                f'<div class="obra-item">'
                f'  <h4>{html.escape(obra)}</h4>'
                f'  <div class="autor">{html.escape(dados["autor"])} · {dados["total"]} conceito(s) conectado(s)</div>'
                f'  <div class="conceitos-tags">{tags_html}</div>'
                f"</div>"
            )
        linhas += ["</div>", "", "[Ver índice completo de obras e autores →](obras.md)", ""]

    if indice["diario"]:
        linhas += ["## Últimas Páginas do Diário de Leitura", ""]
        for e in sorted(indice["diario"], key=lambda d: d.get("data", ""), reverse=True)[:3]:
            alvo = e.get("caminho", f"diario/{e['arquivo']}").replace("diario/", "")
            linhas.append(
                f"- `{e.get('data', '')}` [{e['titulo'] or e['arquivo']}](diario/{alvo}) — {e.get('origem', '')}"
            )
        linhas.append("")

    linhas += [
        "---",
        "",
        f"*Gerado em {indice.get('atualizado_em', '').replace('T', ' ') or '—'} · "
        f"{indice['totais']['conceitos'] + indice['totais']['eixos']} notas · "
        f"{indice['totais']['trilhas']} volumes · [Sobre o projeto](sobre.md) · [Guias](docs/index.md)*",
        "",
    ]
    return "\n".join(linhas)


def pagina_conceitos(indice: dict, *, midias_por_conceito: dict[str, list[dict]] | None = None) -> str:
    """Atlas de Conceitos: busca instantânea + filtros reais + cartões editoriais limpos."""
    midias_por_conceito = midias_por_conceito or {}
    total_conceitos = len(indice["conceitos"])
    temas = Counter(c["tema"] for c in indice["conceitos"])

    linhas = [
        '<header class="eb-book-cover eb-atlas-hero">',
        '  <div class="eb-cover-kicker">Enciclopédia Viva & Glossário Crítico</div>',
        "# Atlas de Conceitos",
        "",
        f'  <p class="eb-cover-subtitle">Os <strong>{total_conceitos} conceitos e eixos</strong> do livro reunidos para '
        "consulta rápida ou exploração transversal. Cada verbete traz definição enxuta, ensaio explicativo, "
        "conexões entre disciplinas e aulas verificadas.</p>",
        "</header>",
        "",
        '<section class="eb-filter-bar" aria-label="Buscar e filtrar conceitos">',
        '  <input id="humanitas-search" class="humanitas-search" type="search" '
        'placeholder="Buscar por conceito, pensador, obra ou tema… (atalho: Ctrl+K ou /)" '
        'aria-label="Buscar conceitos">',
        '  <div class="humanitas-filters">',
        f'    <button type="button" class="humanitas-filter active" data-filter="todos">Todos ({total_conceitos})</button>',
    ]
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        linhas.append(
            f'    <button type="button" class="humanitas-filter" data-filter="{tema}">'
            f'{html.escape(TEMAS.get(tema, tema))} ({qtd})</button>'
        )
    linhas += [
        "  </div>",
        '  <div class="eb-filter-row eb-filter-row-secondary" id="eb-conceito-tipo-filters">',
        '    <button type="button" class="eb-pill-filter active" data-tipo-filter="todos">Conceitos + Eixos</button>',
        '    <button type="button" class="eb-pill-filter" data-tipo-filter="conceito">Apenas conceitos</button>',
        '    <button type="button" class="eb-pill-filter" data-tipo-filter="eixo">Apenas eixos de debate</button>',
        "  </div>",
        '  <div id="conceito-counter" class="eb-filter-counter"></div>',
        "</section>",
        "",
        '<div class="conceito-grid">',
    ]

    todos = sorted(
        indice["conceitos"],
        key=lambda c: (c["tipo"] == "eixo", c["conceito"]),
    )
    for c in todos:
        slug_c = c["arquivo"].removesuffix(".md")
        qtd_m = len(midias_por_conceito.get(slug_c, []))
        cor = CORES_TEMA.get(c["tema"], "#3b4cca")
        autor = c.get("autor_origem", "")
        definicao = c.get("definicao") or "Sem definição cadastrada ainda."
        if len(definicao) > 210:
            definicao = definicao[:207].rstrip() + "…"

        badges = [
            f'<span class="eb-card-theme" style="--tema-cor:{cor}">{html.escape(TEMAS.get(c["tema"], c["tema"]))}</span>'
        ]
        if c.get("tipo") == "eixo":
            badges.append('<span class="eb-card-badge eb-badge-axis">Eixo</span>')
        if c.get("nivel"):
            badges.append(f'<span class="eb-card-badge">{html.escape(c["nivel"])}</span>')
        if qtd_m:
            badges.append(f'<span class="eb-card-badge">🎬 {qtd_m} mídia{"s" if qtd_m > 1 else ""}</span>')

        href_c = url_site("conceitos/index.md", f"conceitos/{c['arquivo']}")
        linhas.append(
            f'<article class="conceito-card" id="{slug_c}" data-tema="{html.escape(c["tema"])}" '
            f'data-tipo="{html.escape(c.get("tipo", "conceito"))}" data-status="{html.escape(c["status"])}" style="--tema-cor:{cor}">'
            f'  <div class="meta">{"".join(badges)}</div>'
            f'  <h3><a href="{href_c}">{html.escape(c["conceito"])}</a></h3>'
            + (f'  <div class="eb-card-author">{html.escape(autor)}</div>' if autor else "")
            + f'  <p class="def">{html.escape(definicao)}</p>'
            f'  <div class="eb-card-foot">'
            f'    <span class="eb-card-status">{GLIFO_STATUS.get(c["status"], "○")} {"Revisado" if c["status"] == "ok" else "Estudo"}</span>'
            f'    <a class="eb-card-cta" href="{href_c}">Ler ensaio →</a>'
            f"  </div>"
            f"</article>"
        )

    linhas += ["</div>", ""]

    # Índice completo em Markdown para leitores, busca estática e auditoria de links relativos
    linhas += [
        '<details class="eb-method-box" markdown>',
        "<summary>Índice remissivo completo por disciplina</summary>",
        "",
    ]
    for tema, _qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        linhas.append(f"### {TEMAS.get(tema, tema)} {{ #{tema} }}")
        linhas.append("")
        for c in [x for x in todos if x["tema"] == tema]:
            linhas.append(f"- [{c['conceito']}]({c['arquivo']}) — {c.get('definicao', '')[:120]}")
        linhas.append("")
    linhas += ["</details>", ""]
    return "\n".join(linhas)


def pagina_trilhas(indice: dict, *, midias_por_conceito: dict[str, list[dict]] | None = None, raiz: pathlib.Path | None = None) -> str:
    """Sumário de Volumes do Livro Digital: estante organizada em Partes I, II e III."""
    volumes = mapear_volumes_ordenados(indice["trilhas"])
    midias_por_conceito = midias_por_conceito or {}

    linhas = [
        '<header class="eb-book-cover eb-volumes-hero">',
        '  <div class="eb-cover-kicker">Percurso Guiado de Leitura</div>',
        "# Volumes & Capítulos",
        "",
        f'  <p class="eb-cover-subtitle">Cada um dos <strong>{len(volumes)} volumes</strong> propõe uma ordem deliberada '
        "de estudo — do conceito fundador às sínteses contemporâneas — integrando texto, aulas universitárias, "
        "obras de apoio e exercícios reflexivos.</p>",
        "</header>",
        "",
        '<div class="eb-reader-tip">',
        "  <strong>Como percorrer um volume:</strong> abra o volume desejado, estude parada por parada na sequência, "
        "assista à mídia correspondente no próprio capítulo e marque as caixas concluídas (o progresso fica salvo neste navegador).",
        "</div>",
        "",
    ]

    partes_vistas: dict[str, list[dict]] = {}
    desc_partes: dict[str, str] = {}
    for v in volumes:
        partes_vistas.setdefault(v["parte_nome"], []).append(v)
        desc_partes[v["parte_nome"]] = v["parte_desc"]

    for p_nome, vols_parte in partes_vistas.items():
        linhas += [
            f"## {p_nome}",
            "",
            f"*{desc_partes.get(p_nome, '')}*",
            "",
            '<div class="eb-volume-grid eb-volume-grid-large">',
        ]
        for v in vols_parte:
            cor = CORES_TEMA.get(v["tema"], "#3b4cca")
            titulo_curto, _, subtitulo = v["trilha"].partition(":")
            objetivo = (v.get("objetivo") or subtitulo or "").strip()
            primeiros_nos = [n.split("—")[0].strip() for n in (v.get("nos") or [])[:4]]
            amostra_html = "".join(
                f"<li>{html.escape(no[:48])}</li>" for no in primeiros_nos if no
            )
            href_vol = url_site("trilhas/index.md", f"trilhas/{v['arquivo']}")
            linhas.append(
                f'<a class="eb-volume-card eb-volume-card-detailed" href="{href_vol}" '
                f'data-trilha-slug="{v["arquivo"].removesuffix(".md")}" data-trilha-total="{v["nos_total"]}" style="--tema-cor:{cor}">'
                f'  <div class="eb-vol-spine"></div>'
                f'  <div class="eb-vol-content">'
                f'    <div class="eb-vol-top">'
                f'      <span class="eb-vol-num">Volume {v["volume_romano"]}</span>'
                f'      <span class="eb-vol-theme">{html.escape(TEMAS.get(v["tema"], v["tema"]))} · {html.escape(v["nivel"] or "iniciante")}</span>'
                f"    </div>"
                f'    <h3 class="eb-vol-title">{html.escape(titulo_curto.strip())}</h3>'
                + (f'    <div class="eb-vol-sub">{html.escape(subtitulo.strip())}</div>' if subtitulo.strip() else "")
                + f'    <p class="eb-vol-desc">{html.escape(objetivo)}</p>'
                + (f'    <ol class="eb-vol-preview">{amostra_html}</ol>' if amostra_html else "")
                + f'    <div class="eb-vol-footer">'
                f'      <span class="eb-vol-stops">{v["nos_concluidos"]}/{v["nos_total"]} paradas · {barra(v["nos_concluidos"], v["nos_total"], 6)}</span>'
                f'      <span class="eb-vol-cta">Abrir volume →</span>'
                f"    </div>"
                f"  </div>"
                f"</a>"
            )
        linhas += ["</div>", ""]

    tem_g03 = bool(raiz and (raiz / "docs" / "03-prompts-notebooklm.md").exists())
    ref_g03 = "[Guia 03](../docs/03-prompts-notebooklm.md)" if tem_g03 else "Guia 03"
    linhas += [
        "## Rito de fechamento de cada parada",
        "",
        "1. **Ler e assistir:** percorra a tese, o ensaio do conceito e a aula/leitura recomendada da parada.",
        f"2. **Explicar sem olhar:** formule a ideia central em voz alta com um exemplo concreto (consulte os prompts do {ref_g03} se quiser debater com o Modo Tutor).",
        "3. **Escrever no Diário:** registre sua resposta à pergunta reflexiva em [Diário de leitura](../diario/index.md) ou pelo [Caderno de estudo](../registrar.md).",
        "",
    ]
    return "\n".join(linhas)


def pagina_eixos(indice: dict) -> str:
    """Mapa editorial dos grandes Eixos de Debate."""
    eixos = sorted(
        [c for c in indice["conceitos"] if c["tipo"] == "eixo"],
        key=lambda c: c["conceito"],
    )
    conceitos_normais = [c for c in indice["conceitos"] if c["tipo"] == "conceito"]

    linhas = [
        '<header class="eb-book-cover eb-axes-hero">',
        '  <div class="eb-cover-kicker">Mapa Transversal de Debates</div>',
        "# Eixos de Debate",
        "",
        f'  <p class="eb-cover-subtitle">As <strong>{len(eixos)} grandes tensões</strong> que atravessam épocas e disciplinas. '
        "Posicionar cada pensador nestes eixos é o que transforma leituras soltas em repertório articulado.</p>",
        "</header>",
        "",
    ]
    if not eixos:
        linhas.append("Nenhum eixo criado ainda.")
        return "\n".join(linhas)

    linhas.append('<div class="eb-axes-grid">')
    for eixo in eixos:
        slug_eixo = eixo["arquivo"].removesuffix(".md")
        cor = CORES_TEMA.get(eixo["tema"], "#7a3e2e")
        href_eixo = url_site("eixos.md", f"conceitos/{eixo['arquivo']}")
        # Conceitos ligados a este eixo
        ligados = [
            c
            for c in conceitos_normais
            if slug_eixo in (c.get("eixos") or []) or eixo["conceito"] in (c.get("eixos") or [])
        ]
        chips = "".join(
            f'<a class="eb-chip-link" href="{url_site("eixos.md", "conceitos/" + c["arquivo"])}">{html.escape(c["conceito"])}</a>'
            for c in ligados[:8]
        )
        linhas.append(
            f'<article class="eb-axis-feature" style="--tema-cor:{cor}">'
            f'  <div class="eb-axis-kicker">Bússola · {html.escape(TEMAS.get(eixo["tema"], eixo["tema"]))}</div>'
            f'  <h2><a href="{href_eixo}">{html.escape(eixo["conceito"])}</a></h2>'
            f'  <p class="eb-axis-question">{html.escape(eixo["definicao"] or "Sem questão definida ainda.")}</p>'
            + (f'  <div class="eb-media-links"><span>Conceitos posicionados aqui:</span> {chips}</div>' if chips else "")
            + f'  <div class="eb-axis-actions"><a href="{href_eixo}">Abrir debate completo e quadro de posições →</a></div>'
            f"</article>"
        )
    linhas.append("</div>\n")

    # Índice sumário em Markdown para consulta rápida e auditoria de links
    linhas += [
        '<details class="eb-method-box" markdown>',
        "<summary>Lista remissiva de todos os eixos de debate</summary>",
        "",
    ]
    for eixo in eixos:
        linhas.append(f"- [{eixo['conceito']}](conceitos/{eixo['arquivo']}) — {eixo.get('definicao', '')}")
    linhas += ["", "</details>", ""]
    return "\n".join(linhas)


def pagina_obras(indice: dict) -> str:
    try:
        from .obras import agrupar_obras
        dados = agrupar_obras(indice)
    except Exception:
        dados = {"obras": {}}

    linhas = [
        '<header class="eb-book-cover eb-works-hero">',
        '  <div class="eb-cover-kicker">Bibliografia Viva do Acervo</div>',
        "# Obras & Autores",
        "",
        '  <p class="eb-cover-subtitle">As fontes primárias e obras de referência de onde nascem os conceitos do livro, '
        "agrupadas por autor e tradição.</p>",
        "</header>",
        "",
    ]
    if not dados.get("obras"):
        linhas.append("Nenhuma obra indexada ainda — rode `make painel`.")
        return "\n".join(linhas)

    obras_principais = _obras_reais(dados["obras"])
    outras = [
        (obra, info)
        for obra, info in sorted(dados["obras"].items(), key=lambda kv: (-kv[1]["total"], kv[0]))
        if (obra, info) not in obras_principais
    ]

    linhas.append('<div class="eb-works-list">')
    for obra, info in obras_principais:
        temas_txt = ", ".join(TEMAS.get(t, t) for t in info["temas"].keys())
        links_c = "".join(
            f'<a class="eb-chip-link" href="{url_site("obras.md", "conceitos/" + c["arquivo"])}">{html.escape(c["conceito"])}</a>'
            for c in info["conceitos"]
        )
        linhas.append(
            f'<article class="eb-work-card">'
            f'  <h3>{html.escape(obra)}</h3>'
            f'  <div class="eb-work-meta"><strong>{html.escape(info["autor"])}</strong> · '
            f'{info["total"]} conceito(s) · {html.escape(temas_txt)}</div>'
            f'  <div class="eb-media-links">{links_c}</div>'
            f"</article>"
        )
    linhas.append("</div>\n")

    if outras:
        linhas += [
            '<details class="eb-method-box" markdown>',
            "<summary>Guias internos, planos de estudo e notas sem obra primária declarada</summary>",
            "",
        ]
        for obra, info in outras:
            linhas.append(f"### {obra} ({info['total']})")
            for c in info["conceitos"]:
                linhas.append(f"- [{c['conceito']}](conceitos/{c['arquivo']}) — {TEMAS.get(c['tema'], c['tema'])}")
            linhas.append("")
        linhas += ["</details>", ""]

    return "\n".join(linhas)


def pagina_grafo(indice: dict) -> str:
    temas = Counter(c["tema"] for c in indice["conceitos"])
    linhas = [
        '<header class="eb-book-cover eb-graph-hero">',
        '  <div class="eb-cover-kicker">Constelação Interdisciplinar</div>',
        "# Mapa de Conexões",
        "",
        '  <p class="eb-cover-subtitle">Cada ponto é um conceito ou eixo de debate; cada linha representa uma relação '
        "conceitual direta ou um eixo compartilhado. Filtre por disciplina, arraste nós e clique para ler o ensaio.</p>",
        "</header>",
        "",
        '<div class="humanitas-filters" id="eb-graph-filters">',
        '  <button type="button" class="humanitas-filter active" data-graph-tema="todos">Todas as disciplinas</button>',
    ]
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        linhas.append(
            f'  <button type="button" class="humanitas-filter" data-graph-tema="{tema}">'
            f'{html.escape(TEMAS.get(tema, tema))} ({qtd})</button>'
        )
    linhas += [
        "</div>",
        "",
        '<div class="grafo-container grafo-container-full">',
        '  <canvas id="grafo-canvas" width="1100" height="620" aria-label="Grafo completo de conceitos"></canvas>',
        "</div>",
        '<div class="grafo-legend">',
        '  <span><span class="dot" style="background:#2d6a64"></span> Filosofia</span>',
        '  <span><span class="dot" style="background:#3b4cca"></span> Sociologia</span>',
        '  <span><span class="dot" style="background:#b85d19"></span> Psicologia</span>',
        '  <span><span class="dot" style="background:#8c3b5a"></span> Antropologia</span>',
        '  <span><span class="dot" style="background:#7c5832"></span> História</span>',
        '  <span><span class="dot" style="background:#2f6f4e"></span> Geografia</span>',
        '  <span><span class="dot" style="background:#5b3e82"></span> Ciência Política</span>',
        '  <span><span class="dot" style="background:#1f5f7a"></span> Economia</span>',
        '  <span><span class="dot" style="background:#c0392b"></span> Eixo de debate</span>',
        "</div>",
        "",
    ]
    return "\n".join(linhas)


def pagina_retencao(indice: dict) -> str:
    try:
        ret = (
            _json.loads(pathlib.Path("indices/retencao.json").read_text(encoding="utf-8"))
            if pathlib.Path("indices/retencao.json").exists()
            else {}
        )
    except Exception:
        ret = {}

    # Monta deck interativo de revisão rápida a partir dos conceitos que têm definição
    deck = [
        {
            "conceito": c["conceito"],
            "tema": TEMAS.get(c["tema"], c["tema"]),
            "tipo": c.get("tipo", "conceito"),
            "definicao": c["definicao"],
            "arquivo": c["arquivo"],
        }
        for c in indice["conceitos"]
        if c.get("definicao")
    ]

    linhas = [
        '<header class="eb-book-cover eb-recall-hero">',
        '  <div class="eb-cover-kicker">Memória de Longo Prazo & Revisão Ativa</div>',
        "# Revisão & Flashcards",
        "",
        '  <p class="eb-cover-subtitle">Pratique recordação ativa direto no navegador com os cartões gerados das notas '
        "do livro, ou importe o arquivo <code>flashcards.csv</code> para o Anki.</p>",
        "</header>",
        "",
        '<section class="eb-flashcard-trainer" id="eb-flashcard-trainer">',
        '  <div class="eb-fc-toolbar">',
        '    <span class="eb-fc-kicker">Treinador de Recordação Ativa</span>',
        '    <span id="eb-fc-progress" class="eb-fc-progress"></span>',
        "  </div>",
        '  <div class="eb-fc-stage" id="eb-fc-stage" tabindex="0" role="button" aria-label="Virar cartão de memória">',
        '    <div class="eb-fc-theme" id="eb-fc-theme"></div>',
        '    <div class="eb-fc-front" id="eb-fc-front">Carregando cartões…</div>',
        '    <div class="eb-fc-back" id="eb-fc-back" hidden></div>',
        '    <div class="eb-fc-hint" id="eb-fc-hint">Clique no cartão (ou pressione Espaço) para revelar a síntese</div>',
        "  </div>",
        '  <div class="eb-fc-controls">',
        '    <button type="button" class="hum-btn" id="eb-fc-prev">← Anterior</button>',
        '    <button type="button" class="hum-btn hum-btn-primario" id="eb-fc-flip">Revelar resposta</button>',
        '    <button type="button" class="hum-btn" id="eb-fc-shuffle">Embaralhar</button>',
        '    <button type="button" class="hum-btn" id="eb-fc-next">Próximo →</button>',
        '    <a class="hum-btn hum-btn-sutil" id="eb-fc-open" href="../conceitos/">Abrir ensaio →</a>',
        "  </div>",
        "</section>",
        "",
        f'<script type="application/json" id="eb-flashcards-data">{_json.dumps(deck, ensure_ascii=False)}</script>',
        "",
        "## Métricas de Retenção e Maturidade do Acervo",
        "",
    ]
    if ret:
        linhas += [
            f"- **Taxa de notas revisadas (`ok`):** {ret.get('taxa_ok', 0):.0%} ({ret.get('por_status', {}).get('ok', 0)}/{ret.get('total_conceitos', 0)})",
            f"- **Cartões exportáveis para Anki:** {ret.get('total_cartoes', 0)} cartões no total",
            "",
        ]
    linhas += [
        "### Cobertura por disciplina",
        "",
        "| Tema | Notas | Revisadas (`ok`) | Com citação |",
        "|---|---|---|---|",
    ]
    temas = Counter(c["tema"] for c in indice["conceitos"])
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        do_tema = [c for c in indice["conceitos"] if c["tema"] == tema]
        linhas.append(
            f"| {TEMAS.get(tema, tema)} | {qtd} | "
            f"{sum(1 for c in do_tema if c['status'] == 'ok')} | "
            f"{sum(1 for c in do_tema if c['tem_trecho'])} |"
        )
    return "\n".join(linhas)


def _ajustar_links_readme(destino: pathlib.Path) -> None:
    """No site, os README viram `index.md`: ajusta os links que apontavam para eles."""
    for arquivo in destino.rglob("*.md"):
        texto = ler(arquivo)
        novo = re.sub(r"\]\(([^)\s]*?)README\.md([^)\s]*)\)", r"](\1index.md\2)", texto)
        if novo != texto:
            arquivo.write_text(novo, encoding="utf-8")


REPO_URL = "https://github.com/LucasRangel89/humanitas"

PASTAS_NOVA = {
    "conceito": "conceitos",
    "eixo": "conceitos",
    "ficha": "acervo/fichas",
    "trecho": "trechos",
    "diario": "diario",
}


def pagina_registrar(indice: dict, guias: set[str] | None = None) -> str:
    """Página "Caderno & Progresso" (`registrar.md`): criar nota, ver pendências e sincronizar trilhas."""
    p = calcular_progresso(indice)
    pendentes = sorted(
        (c for c in indice["conceitos"] if c.get("pendencias") and c.get("status") != "ok"),
        key=lambda c: (-len(c["pendencias"]), c["conceito"]),
    )[:8]

    guias = guias or set()
    link_ritual = (
        "[Guia 10](docs/10-ritual-de-estudo.md)" if "10-ritual-de-estudo.md" in guias else "Guia 10"
    )
    link_ci = (
        "[Guia 06](docs/06-manutencao-e-ci.md)" if "06-manutencao-e-ci.md" in guias else "Guia 06"
    )

    volumes = mapear_volumes_ordenados(indice.get("trilhas", []))
    config = {
        "repo": REPO_URL,
        "pastas": PASTAS_NOVA,
        "temas": dict(TEMAS),
        "hoje": __import__("datetime").date.today().isoformat(),
        "trilhas": [
            {
                "slug": str(tr.get("arquivo", "")).removesuffix(".md"),
                "nome": f"Vol. {tr['volume_romano']} · {tr.get('trilha', '')}",
                "arquivo": tr.get("arquivo", ""),
                "total": tr.get("nos_total", 0),
                "nos": tr.get("nos", []),
            }
            for tr in volumes
        ],
    }

    linhas = [
        '<header class="eb-book-cover eb-notebook-hero" markdown>',
        "",
        '<div class="eb-cover-kicker">Escrita Autoral & Sincronização de Leitura</div>',
        "",
        "# Caderno de Estudo & Progresso",
        "",
        "Seu espaço para **acompanhar os volumes lidos**, **escrever entradas do diário** e **criar ou revisar ensaios**. "
        "Como o livro é estático, ele monta o arquivo padronizado e leva você direto ao GitHub com tudo preenchido.",
        "",
        "</header>",
        "",
        '<div class="hum-cards" markdown>',
        "",
        "## Progresso de leitura nos Volumes",
        "",
        "Em cada volume do livro, as paradas têm caixas de conclusão clicáveis salvas **neste navegador** (`localStorage`). "
        "Exporte um backup `.json` quando quiser gravar definitivamente no repositório ou transferir de dispositivo.",
        "",
        "</div>",
        "",
        '<div class="hum-card" id="hum-progresso">',
        '  <table class="hum-tabela-progresso">',
        "    <thead><tr><th>Volume</th><th>Paradas concluídas</th><th></th></tr></thead>",
        '    <tbody id="hum-linhas-progresso"></tbody>',
        "  </table>",
        '  <p class="hum-dica" id="hum-total-progresso"></p>',
        '  <div class="hum-acoes">',
        '    <button type="button" class="hum-btn hum-btn-primario" data-acao="exportar">'
        "Exportar progresso (.json)</button>",
        '    <button type="button" class="hum-btn" data-acao="baixar-md">'
        "Baixar resumo legível (.md)</button>",
        '    <button type="button" class="hum-btn" data-acao="importar">Importar…</button>',
        '    <input type="file" class="hum-input-arquivo" accept="application/json" hidden>',
        '    <button type="button" class="hum-btn hum-btn-sutil" data-acao="limpar-tudo">'
        "Limpar tudo</button>",
        "  </div>",
        '  <p class="hum-dica" id="hum-dica-progresso"></p>',
        '  <p class="hum-nota">Para gravar no repositório, exporte e rode o comando '
        "abaixo na pasta do projeto:</p>",
        '  <div class="hum-comando"><code id="hum-comando">'
        "make aplicar-progresso ARQUIVO=~/Downloads/progresso.json</code>"
        '<button type="button" class="hum-btn hum-btn-sutil" data-acao="copiar-comando">'
        "Copiar comando</button></div>",
        "</div>",
        "",
        '<div class="hum-cards" markdown>',
        "",
        "## 1. Escrever nota, diário ou ficha",
        "",
        "Escolha o formato (Diário de leitura, Conceito, Eixo, Trecho ou Ficha). O Markdown nasce pronto no padrão do livro; "
        "basta **copiar** ou clicar em **Abrir no GitHub preenchido**.",
        "",
        "</div>",
        "",
        '<div class="hum-card" id="hum-criar">',
        '  <div class="hum-form">',
        '    <label>Tipo<select id="hum-tipo">'
        '<option value="diario">Diário de bordo</option>'
        '<option value="conceito" selected>Conceito</option>'
        '<option value="eixo">Eixo (grande questão)</option>'
        '<option value="trecho">Trecho (citação)</option>'
        '<option value="ficha">Ficha de leitura</option>'
        "</select></label>",
        '    <label>Nome<input id="hum-nome" type="text" placeholder="Ex.: Habitus" autocomplete="off"></label>',
        '    <label>Tema<select id="hum-tema"></select></label>',
        '    <label>Nível<select id="hum-nivel">'
        '<option value="iniciante">iniciante</option>'
        '<option value="entusiasta">entusiasta</option>'
        '<option value="avancado">avancado</option></select></label>',
        '    <label>Autor<input id="hum-autor" type="text" placeholder="Ex.: Pierre Bourdieu" autocomplete="off"></label>',
        '    <label>Obra<input id="hum-obra" type="text" placeholder="Ex.: O Senso Prático" autocomplete="off"></label>',
        '    <label id="hum-campo-ano" hidden>Ano<input id="hum-ano" type="text" placeholder="1980" autocomplete="off"></label>',
        '    <label id="hum-campo-cap" hidden>Capítulo<input id="hum-capitulo" type="text" placeholder="3" autocomplete="off"></label>',
        '    <label id="hum-campo-pag" hidden>Página<input id="hum-pagina" type="text" placeholder="94" autocomplete="off"></label>',
        "  </div>",
        '  <p class="hum-arquivo">Arquivo: <code id="hum-caminho">conceitos/…</code></p>',
        '  <textarea id="hum-saida" class="hum-saida" rows="16" spellcheck="false" readonly></textarea>',
        '  <div class="hum-acoes">',
        '    <button type="button" class="hum-btn" data-acao="copiar">Copiar Markdown</button>',
        '    <a class="hum-btn hum-btn-primario" id="hum-github" href="#" target="_blank" rel="noopener">Abrir no GitHub preenchido</a>',
        '    <span class="hum-dica" id="hum-dica"></span>',
        "  </div>",
        '  <p class="hum-nota">No terminal local: '
        '<code>make nova TIPO=conceito NOME="Habitus" TEMA=sociologia</code>.</p>',
        "</div>",
        "",
        '<div class="hum-cards" markdown>',
        "",
        "## 2. Reescrever e consolidar ensaios",
        "",
        f"Situação atual: **{p['ok']} de {p['conceitos']} ensaios** revisados em padrão-ouro. "
        f"O roteiro de 90 minutos para revisar uma nota com fonte primária está no {link_ritual}.",
        "",
        "</div>",
        "",
        "| Ensaio | Tema | Próximo passo editorial | Ações |",
        "|---|---|---|---|",
    ]
    for c in pendentes:
        github = f"{REPO_URL}/edit/main/conceitos/{c['arquivo']}"
        linhas.append(
            f"| [{c['conceito']}](conceitos/{c['arquivo']}) "
            f"| {TEMAS.get(c['tema'], c['tema'])} "
            f"| {c['pendencias'][0]} "
            f"| [editar no GitHub]({github}) |"
        )
    linhas += [
        "",
        '<div class="hum-cards" markdown>',
        "",
        "## 3. Cartões de Memória (Anki & Revisão)",
        "",
        f"Cada ensaio gera automaticamente seus cartões de revisão (**{p['conceitos']} cartões** ativos). "
        f"Pratique agora em [Revisão & Flashcards](retencao.md) ou gere o CSV para Anki com `make painel` ({link_ci}).",
        "",
        "</div>",
        "",
        f'<script type="application/json" id="hum-config">{_json.dumps(config, ensure_ascii=False)}</script>',
        "",
    ]
    return "\n".join(linhas)


def montar_site_src(raiz: pathlib.Path, destino: pathlib.Path | None = None) -> pathlib.Path:
    """Monta `site-src/` transformando o acervo público em um Livro Digital Interativo."""
    destino = destino or (raiz / "site-src")
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    indice = montar_indice(raiz)
    titulos_conceitos = titulos_dos_conceitos(raiz)

    # Carrega biblioteca de mídias verificadas e indexa por conceito
    itens_midia: list[dict] = []
    atualizado_midia = ""
    midias_por_conceito: dict[str, list[dict]] = {}
    if (raiz / "midias" / "biblioteca.yml").exists():
        itens_midia, atualizado_midia, _ = carregar_midias(raiz)
        for item in itens_midia:
            if item.get("_invalido"):
                continue
            for slug_c in item.get("conceitos", []):
                midias_por_conceito.setdefault(slug_c, []).append(item)

    estante_por_conceito, estante_por_trilha = indexar_estante_por_conceito_e_trilha(raiz)
    volumes_ordenados = mapear_volumes_ordenados(indice["trilhas"])
    aparicoes_trilhas = indexar_aparicoes_em_trilhas(raiz, volumes_ordenados)

    # README vira a página "Sobre o projeto"; a capa do livro é gerada em index.md
    if (raiz / "README.md").exists():
        (destino / "sobre.md").write_text(ler(raiz / "README.md"), encoding="utf-8")
    for nome in ARQUIVOS_SITE:
        if nome == "README.md" or not (raiz / nome).exists():
            continue
        conteudo_arq = ler(raiz / nome)
        if nome == "estante.md":
            conteudo_arq = transformar_estante_editorial(conteudo_arq)
        (destino / nome).write_text(conteudo_arq, encoding="utf-8")

    validos_midia = [i for i in itens_midia if not i.get("_invalido")]
    tem_midias_arq = (raiz / "midias" / "biblioteca.yml").exists()
    tem_estante_arq = (raiz / "estante.md").exists()
    guias = {p.name for p in (raiz / "docs").glob("*.md")} if (raiz / "docs").exists() else set()
    (destino / "index.md").write_text(
        pagina_dashboard(
            indice,
            qtd_midias=len(validos_midia),
            tem_midias=tem_midias_arq,
            tem_estante=tem_estante_arq,
            tem_prioridades="05-prioridades-de-leitura.md" in guias,
        ),
        encoding="utf-8",
    )
    if tem_midias_arq:
        cobertura = cobertura_trilhas(raiz, itens_midia)
        (destino / "midias.md").write_text(
            gerar_pagina_midias_interativa(
                itens_midia,
                atualizado_midia,
                titulos_conceitos,
                cobertura,
                tem_guia_11="11-midias-e-videoaulas.md" in guias,
            ),
            encoding="utf-8",
        )

    (destino / "registrar.md").write_text(
        pagina_registrar(indice, guias=guias), encoding="utf-8"
    )
    (destino / "eixos.md").write_text(pagina_eixos(indice), encoding="utf-8")
    (destino / "tags.md").write_text(
        "# Índice Remissivo por Tags\n\nTodas as etiquetas temáticas do livro, geradas a partir dos ensaios e volumes.\n\n"
        "<!-- material/tags -->\n",
        encoding="utf-8",
    )

    for pasta in PASTAS_SITE:
        origem = raiz / pasta
        if origem.exists():
            shutil.copytree(
                origem,
                destino / pasta,
                dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("README.md"),
            )

    # Mapas auxiliares dos conceitos para enriquecimento cruzado
    conceitos_por_slug = {
        c["arquivo"].removesuffix(".md"): c for c in indice["conceitos"]
    }
    textos_conceitos: dict[str, str] = {}
    for arq_c in listar_md(raiz / "conceitos", recursivo=True):
        textos_conceitos[arq_c.stem] = ler(arq_c)

    # Enriquece cada página individual de Conceito e Eixo em site-src/conceitos/
    for c in indice["conceitos"]:
        arq_dest = destino / "conceitos" / c["arquivo"]
        if not arq_dest.exists():
            continue
        slug_c = c["arquivo"].removesuffix(".md")
        enriquecido = enriquecer_nota_conceito(
            c,
            ler(arq_dest),
            midias_do_conceito=midias_por_conceito.get(slug_c, []),
            obras_estante=estante_por_conceito.get(slug_c, []),
            aparicoes=aparicoes_trilhas.get(c["arquivo"], []),
            titulos_conceitos=titulos_conceitos,
        )
        arq_dest.write_text(enriquecido, encoding="utf-8")

    # Enriquece cada página de Trilha como Volume/Capítulo em site-src/trilhas/
    for idx_v, vol in enumerate(volumes_ordenados):
        arq_trilha_dest = destino / "trilhas" / vol["arquivo"]
        if not arq_trilha_dest.exists():
            continue
        vol_ant = volumes_ordenados[idx_v - 1] if idx_v > 0 else None
        vol_prox = volumes_ordenados[idx_v + 1] if idx_v + 1 < len(volumes_ordenados) else None
        enriquecido_t = enriquecer_pagina_trilha(
            vol,
            ler(arq_trilha_dest),
            conceitos_por_slug=conceitos_por_slug,
            textos_conceitos=textos_conceitos,
            midias_por_conceito=midias_por_conceito,
            obras_estante_trilha=estante_por_trilha.get(vol["arquivo"], []),
            titulos_conceitos=titulos_conceitos,
            volume_anterior=vol_ant,
            volume_proximo=vol_prox,
        )
        arq_trilha_dest.write_text(enriquecido_t, encoding="utf-8")

    # Índices gerados
    (destino / "conceitos").mkdir(parents=True, exist_ok=True)
    (destino / "conceitos" / "index.md").write_text(
        pagina_conceitos(indice, midias_por_conceito=midias_por_conceito),
        encoding="utf-8",
    )
    (destino / "trilhas").mkdir(parents=True, exist_ok=True)
    (destino / "trilhas" / "index.md").write_text(
        pagina_trilhas(indice, midias_por_conceito=midias_por_conceito, raiz=raiz),
        encoding="utf-8",
    )
    (destino / "obras.md").write_text(pagina_obras(indice), encoding="utf-8")
    (destino / "grafo.md").write_text(pagina_grafo(indice), encoding="utf-8")
    (destino / "retencao.md").write_text(pagina_retencao(indice), encoding="utf-8")

    # Fichas de leitura (produção própria) — nunca o texto integral
    fichas = raiz / "acervo" / "fichas"
    if fichas.exists():
        shutil.copytree(
            fichas,
            destino / "acervo" / "fichas",
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("README.md"),
        )

    # Pastas de caderno autoral: se ainda vazias, apresentam páginas editoriais acolhedoras em vez de README técnico
    tem_diarios = len(indice.get("diario", [])) > 0
    tem_trechos = len(indice.get("trechos", [])) > 0
    tem_fichas = len(indice.get("fichas", [])) > 0

    paginas_caderno = {
        "diario": (
            ler(raiz / "diario" / "README.md")
            if tem_diarios and (raiz / "diario" / "README.md").exists()
            else "\n".join(
                [
                    '<header class="eb-book-cover eb-notebook-hero">',
                    '  <div class="eb-cover-kicker">Escrita Pessoal · Sem IA</div>',
                    "# Diário de Leitura",
                    "",
                    '  <p class="eb-cover-subtitle">A síntese reflexiva escrita com as suas próprias palavras ao fechar '
                    "cada parada dos volumes. É onde a leitura deixa de ser informação e vira pensamento próprio.</p>",
                    "</header>",
                    "",
                    *(
                        [
                            "## Entradas registradas",
                            "",
                            *[
                                f"- `{d.get('data', '')}` **[{d.get('titulo') or d['arquivo']}]({d['arquivo']})** — *{TEMAS.get(d.get('tema',''), d.get('tema',''))}* ({d.get('origem','')})"
                                for d in sorted(indice.get("diario", []), key=lambda x: x.get("data", ""), reverse=True)
                            ],
                            "",
                        ]
                        if tem_diarios
                        else [
                            '<div class="eb-empty-state" markdown>',
                            "",
                            "### Seu caderno está pronto para a primeira página",
                            "",
                            "Ao concluir o estudo de uma parada em qualquer [Volume do Livro](../trilhas/index.md), responda à **pergunta reflexiva** em 100 a 150 palavras.",
                            "",
                            "[Escrever primeira entrada no Caderno →](../registrar.md)",
                            "",
                            "</div>",
                            "",
                        ]
                    ),
                ]
            )
        ),
        "trechos": (
            ler(raiz / "trechos" / "README.md")
            if tem_trechos and (raiz / "trechos" / "README.md").exists()
            else "\n".join(
                [
                    '<header class="eb-book-cover eb-notebook-hero">',
                    '  <div class="eb-cover-kicker">Antologia Comentada</div>',
                    "# Trechos & Citações",
                    "",
                    '  <p class="eb-cover-subtitle">Passagens literais das obras primárias (com capítulo e página), '
                    "sempre acompanhadas de um comentário sobre o que mudam na compreensão do tema.</p>",
                    "</header>",
                    "",
                    *(
                        [
                            "## Passagens guardadas",
                            "",
                            *[
                                f"- **[{t.get('titulo') or t['arquivo']}]({t['arquivo']})** — *{t.get('obra','')}* ({t.get('autor','')})"
                                for t in indice.get("trechos", [])
                            ],
                            "",
                        ]
                        if tem_trechos
                        else [
                            '<div class="eb-empty-state" markdown>',
                            "",
                            "### Nenhuma passagem destacada separadamente ainda",
                            "",
                            (
                                "Conforme avançar na leitura das obras primárias da [Estante](../estante.md), guarde aqui as citações decisivas com capítulo e página."
                                if tem_estante_arq
                                else "Conforme avançar na leitura das obras primárias, guarde aqui as citações decisivas com capítulo e página."
                            ),
                            "",
                            "[Registrar novo trecho →](../registrar.md)",
                            "",
                            "</div>",
                            "",
                        ]
                    ),
                ]
            )
        ),
        "acervo/fichas": (
            ler(raiz / "acervo" / "fichas" / "README.md")
            if tem_fichas and (raiz / "acervo" / "fichas" / "README.md").exists()
            else "\n".join(
                [
                    '<header class="eb-book-cover eb-notebook-hero">',
                    '  <div class="eb-cover-kicker">Leitura Estrutural de Obras</div>',
                    "# Fichas de Leitura",
                    "",
                    '  <p class="eb-cover-subtitle">Uma ficha por livro estudado por inteiro: o problema do autor, '
                    "a tese central em três frases, o percurso dos capítulos e os conceitos-chave extraídos.</p>",
                    "</header>",
                    "",
                    *(
                        [
                            "## Obras fichadas",
                            "",
                            *[
                                f"- **[{f.get('obra') or f['arquivo']}]({f['arquivo']})** — {f.get('autor','')} ({f.get('ano','')})"
                                for f in indice.get("fichas", [])
                            ],
                            "",
                        ]
                        if tem_fichas
                        else [
                            '<div class="eb-empty-state" markdown>',
                            "",
                            "### Nenhuma ficha de livro completo publicada ainda",
                            "",
                            (
                                "Escolha um livro de entrada nas [Prioridades de Leitura](../../docs/05-prioridades-de-leitura.md) ou na [Estante](../../estante.md) e abra sua ficha."
                                if ("05-prioridades-de-leitura.md" in guias and tem_estante_arq)
                                else "Escolha um livro de entrada em [Obras & Autores](../../obras.md) e abra sua ficha."
                            ),
                            "",
                            "[Criar ficha de leitura →](../../registrar.md)",
                            "",
                            "</div>",
                            "",
                        ]
                    ),
                ]
            )
        ),
    }

    for rel_pasta, conteudo_idx in paginas_caderno.items():
        (destino / rel_pasta).mkdir(parents=True, exist_ok=True)
        (destino / rel_pasta / "index.md").write_text(conteudo_idx, encoding="utf-8")

    # Assets de UI (todo o docs/assets: css, js, imagens)
    origem_assets = raiz / "docs" / "assets"
    if origem_assets.exists():
        shutil.copytree(
            origem_assets,
            destino / "assets",
            dirs_exist_ok=True,
        )

    # Índices JSON para fetch no JS (grafo, mídias, obras, índice)
    if (raiz / "indices").exists():
        (destino / "indices").mkdir(parents=True, exist_ok=True)
        for jf in (raiz / "indices").glob("*.json"):
            shutil.copy2(jf, destino / "indices" / jf.name)

    # Guias do projeto, sem anexos e textos NOBA de terceiros
    docs = raiz / "docs"
    if docs.exists():
        shutil.copytree(
            docs,
            destino / "docs",
            dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("anexos", "NOBA", "assets"),
        )
        if (destino / "docs" / "README.md").exists():
            (destino / "docs" / "index.md").write_text(
                ler(destino / "docs" / "README.md"), encoding="utf-8"
            )
            (destino / "docs" / "README.md").unlink()

    _ajustar_links_readme(destino)
    return destino


def cmd_site(raiz: pathlib.Path, **opcoes) -> int:
    # PR7: portão — não publica site se auditoria falhar
    from .auditoria import auditar as _auditar_gate

    erros, _avisos = _auditar_gate(raiz)
    if erros:
        print("# Portão de publicação bloqueado: auditoria encontrou erros.")
        for e in erros[:10]:
            print(f"  - {e}")
        print(f"\nCorrija {len(erros)} erro(s) antes de publicar o site (rode `make auditar`).")
        return 1
    destino = raiz / "site-src"
    montar_site_src(raiz, destino)
    paginas = sorted(destino.rglob("*.md"))
    auditaveis = [p for p in paginas if "templates" not in p.relative_to(destino).parts]
    problemas = _links_quebrados(destino, auditaveis)
    print(f"site-src/ montado com {len(paginas)} página(s).")
    print("O texto integral do acervo, docs/anexos e docs/NOBA ficaram de fora.")
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
