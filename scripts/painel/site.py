from __future__ import annotations

import pathlib
import re
import shutil
from collections import Counter

from .modelo import TEMAS, PASTAS_SITE, ARQUIVOS_SITE, ler, listar_md, rel, _limpar_erros_frontmatter, normalizar
from .indice import montar_indice, coletar_conceitos
from .progresso import calcular_progresso, pendencias_da_nota, progresso_barra
from .auditoria import _links_quebrados
from .scaffolding import slug

# Site (MkDocs Material)
# ---------------------------------------------------------------------------


def barra(feitos: int, total: int, largura: int = 10) -> str:
    """Barra de progresso em blocos, para o dashboard."""
    if total <= 0:
        return "—"
    preenchido = round(largura * feitos / total)
    return "█" * preenchido + "░" * (largura - preenchido)


GLIFO_STATUS = {"ok": "✔", "rascunho": "○", "arquivada": "·"}


def _link_nota(registro: dict, prefixo: str = "conceitos/") -> str:
    """Link relativo para uma nota de conceito/eixo.

    `prefixo=""` quando a página já está dentro de `conceitos/`.
    """
    alvo = registro.get("caminho") or f"conceitos/{registro['arquivo']}"
    if alvo.startswith("conceitos/"):
        alvo = alvo[len("conceitos/"):]
    return f"[{registro['conceito']}]({prefixo}{alvo})"


def pagina_dashboard(indice: dict) -> str:
    """Dashboard navegável: hero + stats + trilhas + filtros + grafo + obras."""
    p = calcular_progresso(indice)
    temas = Counter(c["tema"] for c in indice["conceitos"])
    pct_nos = (p["nos_concluidos"] * 100 // p["nos_total"]) if p["nos_total"] else 0
    pct_ok = (p["ok"] * 100 // p["conceitos"]) if p["conceitos"] else 0
    pendentes = sorted(
        (c for c in indice["conceitos"] if c.get("pendencias") and c.get("status") != "ok"),
        key=lambda c: (-len(c["pendencias"]), c["conceito"]),
    )[:6]
    proxima_trilha = next(
        (t for t in indice["trilhas"] if t["nos_total"] and t["status"] != "concluida"), None
    )
    try:
        import json
        ret = json.loads((pathlib.Path("indices/retencao.json").read_text(encoding="utf-8"))) if pathlib.Path("indices/retencao.json").exists() else {}
    except Exception:
        ret = {}
    try:
        from .obras import agrupar_obras as _agrupar_obras_dashboard
        obras_data = _agrupar_obras_dashboard(indice)
    except Exception:
        obras_data = {"obras": {}}

    linhas = [
        '<div class="humanitas-hero" markdown>',
        "",
        "# Humanitas — seu painel de estudos",
        "",
        "Conceitos ligados por eixos, trilhas com critério e diário que só você escreve. **3 cliques até qualquer ideia.**",
        "",
        f"*Atualizado em {indice.get('atualizado_em','').replace('T',' ')[:16] or '—'} · {p['conceitos']} notas · {p['trilhas_total']} trilhas*",
        "",
        "</div>",
        "",
        '<div class="humanitas-stats" markdown>',
        f'<div class="humanitas-stat"><div class="num">{p["ok"]}/{p["conceitos"]}</div><div class="label">reescritas {pct_ok}%</div></div>',
        f'<div class="humanitas-stat"><div class="num">{p["nos_concluidos"]}/{p["nos_total"]}</div><div class="label">nós trilha {pct_nos}%</div></div>',
        f'<div class="humanitas-stat"><div class="num">{p["com_trecho"]}</div><div class="label">com citação</div></div>',
        f'<div class="humanitas-stat"><div class="num">{p["diario_total"]}</div><div class="label">diários</div></div>',
        "</div>",
        "",
        '<div class="grid cards" markdown>',
        "",
        "-   :material-progress-clock:{ .lg .middle } **Onde você está**",
        "",
        "    ---",
        "",
        f"    - Nós: **{p['nos_concluidos']} de {p['nos_total']}** ` {barra(p['nos_concluidos'], p['nos_total'])} `",
        f"    - Notas ok: **{p['ok']} de {p['conceitos']}** · ` {progresso_barra(p['ok'], p['conceitos'])} `",
        f"    - Citações: **{p['com_trecho']} de {p['conceitos']}**",
        f"    - Fonte verificada: **{p.get('fonte_verificada',0)}**",
        "",
        "    [Ver progresso →](progresso.md) · [Filtar pendências →](progresso.md#pendências)",
        "",
        "-   :material-play-circle-outline:{ .lg .middle } **Comece por aqui**",
        "",
        "    ---",
        "",
    ]
    if proxima_trilha:
        linhas.append(
            f"    - 🎯 **Retomar:** [{proxima_trilha['trilha']}](trilhas/{proxima_trilha['arquivo']}) — próximo: *{proxima_trilha['proximo_no'][:60]}*"
        )
    else:
        linhas.append("    - 🎯 [Escolher trilha](trilhas/index.md)")
    linhas += [
        "    - 🗺️ [Mapa de eixos](eixos.md) · 5 debates que atravessam tudo",
        "    - 📚 [Mapa de obras](obras.md) — por autor/obra",
        "    - 🧠 [Grafo interativo](grafo.md) — clique nos nós",
        "",
        "-   :material-map-marker-path:{ .lg .middle } **Trilhas**",
        "",
        "    ---",
        "    *Cada nó = uma nota. Só fecha com explicação + quiz + diário.*",
        "",
        "    [Ver 5 trilhas →](trilhas/index.md)",
        "",
        "-   :material-book-open-variant:{ .lg .middle } **Conceitos**",
        "",
        "    ---",
        "    " + " · ".join(
            f"[{TEMAS.get(tema, tema)}](conceitos/index.md#{slug(TEMAS.get(tema, tema))}) ({qtd})"
            for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0]))
        ),
        "",
        "    `Ctrl+K` ou `/` para buscar · [Ver todos →](conceitos/index.md)",
        "",
        "</div>",
        "",
        "## Trilhas — progresso visual",
        "",
        "| Trilha | Tema | Nós | Progresso | Próximo |",
        "|---|---|---|---|---|",
    ]
    for t in indice["trilhas"]:
        proximo = (t["proximo_no"] or "—")[:60]
        linhas.append(
            f"| [{t['trilha']}](trilhas/{t['arquivo']}) | {TEMAS.get(t['tema'], t['tema'])} | {t['nos_concluidos']}/{t['nos_total']} | `{barra(t['nos_concluidos'], t['nos_total'])}` | {proximo} |"
        )
    linhas += [
        "",
        "## Temas — saúde do acervo",
        "",
        "| Tema | Notas | ✅ ok | 💬 citação | Barra |",
        "|---|---|---|---|---|",
    ]
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        do_tema = [c for c in indice["conceitos"] if c["tema"] == tema]
        ok = sum(1 for c in do_tema if c['status']=="ok")
        cit = sum(1 for c in do_tema if c['tem_trecho'])
        linhas.append(
            f"| [{TEMAS.get(tema, tema)}](conceitos/index.md#{slug(TEMAS.get(tema, tema))}) | {qtd} | {ok} | {cit} | `{barra(ok, qtd)}` |"
        )
    linhas += [
        "",
        "## Grafo — como as ideias se ligam",
        "",
        '<div class="grafo-container" markdown>',
        '<canvas id="grafo-canvas" width="900" height="400" aria-label="Grafo de conceitos"></canvas>',
        "</div>",
        '<div class="grafo-legend" markdown>',
        '<span><span class="dot" style="background:#3f51b5"></span> Sociologia</span>',
        '<span><span class="dot" style="background:#009688"></span> Filosofia</span>',
        '<span><span class="dot" style="background:#ff9800"></span> Psicologia</span>',
        '<span><span class="dot" style="background:#e91e63"></span> Eixo</span>',
        "</div>",
        "",
        "[Explorar grafo completo →](grafo.md) · clique nos nós para navegar",
        "",
    ]
    if obras_data.get("obras"):
        top_obras = sorted(obras_data["obras"].items(), key=lambda kv: -kv[1]["total"])[:3]
        linhas += ["", "## Obras — por onde o conhecimento entra", "", '<div class="obra-list" markdown>', ""]
        for obra, dados in top_obras:
            linhas += [
                f'<div class="obra-item" markdown>',
                f"**{obra}** · {dados['autor']} — {dados['total']} conceitos",
                f"<div class=\"conceitos-tags\" markdown>",
            ]
            for c in dados["conceitos"][:5]:
                linhas.append(f"<span class=\"tag\">{c['conceito']}</span>")
            linhas.append("</div></div>")
        linhas += ["</div>", "", "[Todas as obras →](obras.md)", ""]
    if pendentes:
        linhas += [
            "",
            "## Próximas — o que falta para padrão-ouro",
            "",
            "Filtros: `Ctrl+K` busca instantânea nas 50 notas. Pendência = explicação + citação com página + fonte verificada.",
            "",
            "| Nota | Tema | Pendência | Ação |",
            "|---|---|---|---|",
        ]
        for c in pendentes:
            linhas.append(
                f"| {_link_nota(c)} | {TEMAS.get(c['tema'], c['tema'])} | {c['pendencias'][0]} | [editar](conceitos/{c['arquivo']}) |"
            )
        linhas += ["", "[Ver todas as pendências →](progresso.md#pendências)", ""]
    if indice["diario"]:
        linhas += ["", "## Diário — últimas reflexões", ""]
        for e in sorted(indice["diario"], key=lambda d: d.get("data",""), reverse=True)[:3]:
            alvo = e.get("caminho", f"diario/{e['arquivo']}").replace("diario/","")
            linhas.append(f"- `{e.get('data','')}` [{e['titulo'] or e['arquivo']}](diario/{alvo}) — {e.get('origem','')}")
    linhas += [
        "",
        "## Como isto é mantido",
        "",
        "`conceitos/` + `trilhas/` + `diario/` → `make painel` → este site. Sem edição manual. Guias em [docs/](docs/index.md).",
        "",
        f"*Gerado em {indice.get('atualizado_em','').replace('T',' ') or '—'} · {indice['totais']['conceitos']+indice['totais']['eixos']} notas · {indice['totais']['trilhas']} trilhas · [Guias](docs/index.md)*",
        "",
    ]
    return "\n".join(linhas)


def pagina_conceitos(indice: dict) -> str:
    """Índice navegável: busca + filtros + cards."""
    linhas = [
        "# Conceitos",
        "",
        "Uma nota por ideia. **Busque com Ctrl+K ou /**, filtre por tema e clique para abrir. ✔ = reescrita, ○ = rascunho.",
        "",
        '<input id="humanitas-search" class="humanitas-search" placeholder="Buscar conceito, autor, obra… (Ctrl+K)" aria-label="Buscar conceitos">',
        "",
        '<div class="humanitas-filters" markdown>',
    ]
    temas = Counter(c["tema"] for c in indice["conceitos"])
    linhas.append('<button class="humanitas-filter active" data-filter="todos">Todos (50)</button>')
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        linhas.append(f'<button class="humanitas-filter" data-filter="{tema}">{TEMAS.get(tema, tema)} ({qtd})</button>')
    linhas += [
        "</div>",
        "",
        '<div id="conceito-counter" style="font-size:0.8rem; opacity:0.7; margin-bottom:0.5rem"></div>',
        "",
        '<div class="conceito-grid" markdown>',
        "",
    ]
    todos = sorted(indice["conceitos"], key=lambda c: (c["status"] != "ok", c["conceito"]))
    for c in todos:
        glifo = GLIFO_STATUS.get(c["status"], "·")
        cor_status = "ok" if c["status"]=="ok" else "rascunho"
        trad = f"<span>📚 {c.get('tradicao')}</span>" if c.get('tradicao') else ""
        ev = f"<span>🔬 {c.get('nivel_evidencia')}</span>" if c.get('nivel_evidencia') else ""
        pend = f"<div class=\"pendencias\">⚠️ {', '.join(c.get('pendencias',[])[:2])}</div>" if c.get('pendencias') else ""
        link = _link_nota(c, prefixo='')
        linhas += [
            f'<div class="conceito-card" data-tema="{c["tema"]}" data-status="{c["status"]}" markdown>',
            f"**{glifo} {c['conceito']}** {trad} {ev}",
            "",
            f'<div class="meta" markdown><span>{TEMAS.get(c["tema"], c["tema"])}</span><span>{cor_status}</span><span>{c["nivel"]}</span></div>',
            f'<div class="def" markdown>{c["definicao"][:180] or "*Sem definição*"}…</div>',
            pend,
            f"[Abrir nota]({c['arquivo']}) · {link}",
            "</div>",
            "",
        ]
    linhas += ["</div>", "", "Dica: `/` foca busca, clique no grafo para navegar.", ""]
    return "\n".join(linhas)


def pagina_trilhas(indice: dict) -> str:
    linhas = [
        "# Trilhas",
        "",
        "Um caminho ordenado de estudo — cada nó é uma nota do painel, com critério "
        "de conclusão verificável. Trilha é opção, não obrigação.",
        "",
        "| Trilha | Tema | Nós | Progresso | Status |",
        "|---|---|---|---|---|",
    ]
    for t in indice["trilhas"]:
        linhas.append(
            f"| [{t['trilha']}]({t['arquivo']}) | {TEMAS.get(t['tema'], t['tema'])} "
            f"| {t['nos_concluidos']}/{t['nos_total']} "
            f"| `{barra(t['nos_concluidos'], t['nos_total'])}` | {t['status'] or '—'} |"
        )
    linhas += [
        "",
        "## Como percorrer",
        "",
        "1. Escolha uma trilha e leia o objetivo dela.",
        "2. Estude o nó (nota de conceito + prompts do "
        "[Guia 03](../docs/03-prompts-notebooklm.md)).",
        "3. Feche o nó só quando conseguir explicar em voz alta, fazer o quiz e "
        "escrever a entrada no [diário](../diario/index.md).",
        "",
    ]
    return "\n".join(linhas)


def pagina_eixos(indice: dict) -> str:
    eixos = [c for c in indice["conceitos"] if c["tipo"] == "eixo"]
    linhas = [
        "# Eixos de debate",
        "",
        "As grandes questões que atravessam disciplinas. Toda teoria nova pode ser "
        "posicionada em pelo menos um destes eixos: é o que transforma uma pilha de "
        "resumos em um mapa de debates.",
        "",
    ]
    if not eixos:
        linhas.append("Nenhum eixo criado ainda.")
    for eixo in sorted(eixos, key=lambda c: c["conceito"]):
        linhas += [
            f"## {eixo['conceito']}",
            "",
            eixo["definicao"] or "*Sem definição ainda.*",
            "",
            f"[Abrir a nota do eixo](conceitos/{eixo['arquivo']}) · tema: "
            f"{TEMAS.get(eixo['tema'], eixo['tema'])}",
            "",
        ]
    return "\n".join(linhas)


def pagina_obras(indice: dict) -> str:
    try:
        from .obras import agrupar_obras
        dados = agrupar_obras(indice)
    except Exception:
        dados = {"obras": {}}
    linhas = ["# Obras & Autores", "", "De onde vem cada conceito. Clique para ver os conceitos ligados.", ""]
    if not dados.get("obras"):
        linhas.append("Nenhuma obra indexada ainda — rode `make painel`.")
        
    for obra, info in sorted(dados["obras"].items(), key=lambda kv: (-kv[1]["total"], kv[0])):
        linhas += [f"## {obra}", "", f"*Autor: {info['autor']} · {info['total']} conceitos · temas: {', '.join(info['temas'].keys())}*", ""]
        for c in info["conceitos"]:
            linhas.append(f"- [{c['conceito']}](conceitos/{c['arquivo']}) — {TEMAS.get(c['tema'], c['tema'])}")
        linhas.append("")
    


    return "\n".join(linhas)


def pagina_grafo(indice: dict) -> str:
    linhas = [
        "# Grafo de conceitos",
        "",
        "Cada nó é um conceito, cada aresta é uma relação (`relacoes`) ou eixo compartilhado. **Clique no nó para abrir a nota.** Use filtros por tema se quiser focar.",
        "",
        '<div class="grafo-container" style="height:600px" markdown>',
        '<canvas id="grafo-canvas" width="1100" height="600"></canvas>',
        "</div>",
        '<div class="grafo-legend" markdown>',
        '<span><span class="dot" style="background:#3f51b5"></span> Sociologia</span>',
        '<span><span class="dot" style="background:#009688"></span> Filosofia</span>',
        '<span><span class="dot" style="background:#ff9800"></span> Psicologia</span>',
        '<span><span class="dot" style="background:#e91e63"></span> Eixo</span>',
        "</div>",
        "",
        "Dados em `indices/grafo.json` (gerado por `make painel`). Filtre no dashboard com `Ctrl+K`.",
        "",
    ]
    


    return "\n".join(linhas)


def pagina_retencao(indice: dict) -> str:
    try:
        import json
        ret = json.loads(pathlib.Path("indices/retencao.json").read_text(encoding="utf-8")) if pathlib.Path("indices/retencao.json").exists() else {}
    except Exception:
        ret = {}
    linhas = ["# Retenção & Progresso", "", "Métricas para decidir o que revisar.", ""]
    if ret:
        linhas += [
            f"- **Taxa ok:** {ret.get('taxa_ok',0):.0%} ({ret.get('por_status',{}).get('ok',0)}/{ret.get('total_conceitos',0)})",
            f"- **Cartões:** {ret.get('total_cartoes',0)} total · por tema: {ret.get('cartoes_por_tema',{})}",
            f"- **Por nível:** {ret.get('por_nivel',{})}",
            "",
        ]
    p = calcular_progresso(indice)
    linhas += [
        "## Por tema",
        "",
        "| Tema | Notas | ok | citação |",
        "|---|---|---|---|",
    ]
    from collections import Counter
    temas = Counter(c["tema"] for c in indice["conceitos"])
    for tema, qtd in sorted(temas.items(), key=lambda i: (-i[1], i[0])):
        do_tema = [c for c in indice["conceitos"] if c["tema"]==tema]
        linhas.append(f"| {TEMAS.get(tema,tema)} | {qtd} | {sum(1 for c in do_tema if c['status']=='ok')} | {sum(1 for c in do_tema if c['tem_trecho'])} |")
    


    return "\n".join(linhas)


def _ajustar_links_readme(destino: pathlib.Path) -> None:
    """No site, os README viram `index.md`: ajusta os links que apontavam para eles."""
    for arquivo in destino.rglob("*.md"):
        texto = ler(arquivo)
        novo = re.sub(r"\]\(([^)\s]*?)README\.md([^)\s]*)\)", r"](\1index.md\2)", texto)
        if novo != texto:
            arquivo.write_text(novo, encoding="utf-8")


def montar_site_src(raiz: pathlib.Path, destino: pathlib.Path | None = None) -> pathlib.Path:
    """Monta a pasta de fontes do site só com o que pode ser público.

    Além de copiar o conteúdo, gera as páginas de navegação (painel inicial,
    índices por tema, eixos) a partir do índice — nenhuma delas é editada à mão.
    """
    import shutil

    destino = destino or (raiz / "site-src")
    if destino.exists():
        shutil.rmtree(destino)
    destino.mkdir(parents=True)

    indice = montar_indice(raiz)

    # README vira a página "Sobre o projeto"; a home é o painel gerado
    if (raiz / "README.md").exists():
        (destino / "sobre.md").write_text(ler(raiz / "README.md"), encoding="utf-8")
    for nome in ARQUIVOS_SITE:
        if nome == "README.md" or not (raiz / nome).exists():
            continue
        (destino / nome).write_text(ler(raiz / nome), encoding="utf-8")

    (destino / "index.md").write_text(pagina_dashboard(indice), encoding="utf-8")
    (destino / "eixos.md").write_text(pagina_eixos(indice), encoding="utf-8")
    (destino / "tags.md").write_text(
        "# Tags\n\nTodas as etiquetas do painel, geradas a partir do frontmatter das notas.\n\n"
        "<!-- material/tags -->\n",
        encoding="utf-8",
    )

    for pasta in PASTAS_SITE:
        origem = raiz / pasta
        if origem.exists():
            shutil.copytree(
                origem, destino / pasta, dirs_exist_ok=True,
                ignore=shutil.ignore_patterns("README.md"),
            )

    # índices gerados (substituem as listagens de README dentro dessas pastas)
    (destino / "conceitos").mkdir(parents=True, exist_ok=True)
    (destino / "conceitos" / "index.md").write_text(pagina_conceitos(indice), encoding="utf-8")
    (destino / "trilhas").mkdir(parents=True, exist_ok=True)
    (destino / "trilhas" / "index.md").write_text(pagina_trilhas(indice), encoding="utf-8")
    # novas páginas navegáveis PR9
    (destino / "obras.md").write_text(pagina_obras(indice), encoding="utf-8")
    (destino / "grafo.md").write_text(pagina_grafo(indice), encoding="utf-8")
    (destino / "retencao.md").write_text(pagina_retencao(indice), encoding="utf-8")

    # fichas de leitura (produção própria) — nunca o texto integral
    fichas = raiz / "acervo" / "fichas"
    if fichas.exists():
        shutil.copytree(
            fichas, destino / "acervo" / "fichas", dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("README.md"),
        )

    # pastas com README: o README vira o index da seção (com fallback gerado)
    fallback = {
        "diario": "# Diário\n\nA síntese de cada sessão de estudo, escrita por você.\n",
        "trechos": "# Trechos\n\nCitações literais sempre acompanhadas de comentário.\n",
        "acervo/fichas": "# Fichas de leitura\n\nUma ficha por obra estudada.\n",
    }
    for rel_pasta, texto_padrao in fallback.items():
        readme = raiz / rel_pasta / "README.md"
        (destino / rel_pasta).mkdir(parents=True, exist_ok=True)
        (destino / rel_pasta / "index.md").write_text(
            ler(readme) if readme.exists() else texto_padrao, encoding="utf-8"
        )

    # assets de UI (css/js) e indices para o frontend
    for asset in ["docs/assets/css/dashboard.css", "docs/assets/js/dashboard.js"]:
        src = raiz / asset
        if src.exists():
            dst = destino / asset.replace("docs/", "")
            dst.parent.mkdir(parents=True, exist_ok=True)
            import shutil
            shutil.copy2(src, dst)
    # indices JSON para fetch no JS
    if (raiz / "indices").exists():
        import shutil
        (destino / "indices").mkdir(parents=True, exist_ok=True)
        for jf in (raiz / "indices").glob("*.json"):
            shutil.copy2(jf, destino / "indices" / jf.name)

    _ajustar_links_readme(destino)

    # guias do projeto, sem os anexos de terceiros
    docs = raiz / "docs"
    if docs.exists():
        shutil.copytree(
            docs, destino / "docs", dirs_exist_ok=True,
            ignore=shutil.ignore_patterns("anexos"),
        )
        if (destino / "docs" / "README.md").exists():
            (destino / "docs" / "index.md").write_text(
                ler(destino / "docs" / "README.md"), encoding="utf-8"
            )
            (destino / "docs" / "README.md").unlink()

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


