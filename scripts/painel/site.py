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
    """Página inicial do site: um painel, não um README."""
    p = calcular_progresso(indice)
    temas = Counter(c["tema"] for c in indice["conceitos"])
    pct_nos = (p["nos_concluidos"] * 100 // p["nos_total"]) if p["nos_total"] else 0
    pendentes = sorted(
        (c for c in indice["conceitos"] if c.get("pendencias") and c.get("status") != "ok"),
        key=lambda c: (-len(c["pendencias"]), c["conceito"]),
    )[:5]
    proxima_trilha = next(
        (t for t in indice["trilhas"] if t["nos_total"] and t["status"] != "concluida"), None
    )

    linhas = [
        "# Humanitas",
        "",
        "**Um painel de estudos de ciências humanas.** Conceitos ligados a eixos de "
        "debate, trilhas com critério de conclusão e um diário que só você escreve.",
        "",
        '<div class="grid cards" markdown>',
        "",
        "-   :material-progress-clock:{ .lg .middle } __Onde você está__",
        "",
        "    ---",
        "",
        f"    - Nós de trilha: **{p['nos_concluidos']} de {p['nos_total']}** ({pct_nos}%)",
        f"    - Notas reescritas: **{p['ok']} de {p['conceitos']}**",
        f"    - Entradas no diário: **{p['diario_total']}**",
        f"    - Notas com citação: **{p['com_trecho']} de {p['conceitos']}**",
        "",
        "    [Ver progresso completo](progresso.md)",
        "",
        "-   :material-play-circle-outline:{ .lg .middle } __Comece por aqui__",
        "",
        "    ---",
        "",
    ]
    if proxima_trilha:
        linhas.append(
            f"    - [Retomar: {proxima_trilha['trilha']}](trilhas/"
            f"{proxima_trilha['arquivo']})"
        )
    else:
        linhas.append("    - [Escolher uma trilha](trilhas/index.md)")
    linhas += [
        "    - [Mapa dos eixos de debate](eixos.md)",
        "    - [Como este painel funciona](sobre.md)",
        "",
        "-   :material-map-marker-path:{ .lg .middle } __Trilhas__",
        "",
        "    ---",
        "",
        "    Cinco caminhos, do básico ao avançado, cada um com critério de conclusão.",
        "",
        "    [As 5 trilhas](trilhas/index.md)",
        "",
        "-   :material-book-open-variant:{ .lg .middle } __Conceitos e eixos__",
        "",
        "    ---",
        "",
        "    "
        + " · ".join(
            f"{TEMAS.get(tema, tema)} ({qtd})"
            for tema, qtd in sorted(temas.items(), key=lambda item: (-item[1], item[0]))
        ),
        "",
        "    [Navegar por tema](conceitos/index.md)",
        "",
        "</div>",
        "",
        "## Trilhas",
        "",
        "| Trilha | Nós | Progresso | Próximo nó |",
        "|---|---|---|---|",
    ]
    for t in indice["trilhas"]:
        proximo = t["proximo_no"] or "—"
        if len(proximo) > 60:
            proximo = proximo[:57].rstrip() + "…"
        linhas.append(
            f"| [{t['trilha']}](trilhas/{t['arquivo']}) | {t['nos_concluidos']}/{t['nos_total']} "
            f"| `{barra(t['nos_concluidos'], t['nos_total'])}` | {proximo} |"
        )

    linhas += [
        "",
        "## Temas",
        "",
        "| Tema | Notas | Reescritas | Com citação |",
        "|---|---|---|---|",
    ]
    for tema, qtd in sorted(temas.items(), key=lambda item: (-item[1], item[0])):
        do_tema = [c for c in indice["conceitos"] if c["tema"] == tema]
        linhas.append(
            f"| [{TEMAS.get(tema, tema)}](conceitos/index.md#{slug(TEMAS.get(tema, tema))}) "
            f"| {qtd} | {sum(1 for c in do_tema if c['status'] == 'ok')} "
            f"| {sum(1 for c in do_tema if c['tem_trecho'])} |"
        )

    if pendentes:
        linhas += [
            "",
            "## O que falta para as notas ficarem boas",
            "",
            "Texto de exemplo, citação sem página e fonte secundária não passam no "
            "padrão-ouro. Estas são as próximas:",
            "",
            "| Nota | Tema | Primeira pendência |",
            "|---|---|---|",
        ]
        for c in pendentes:
            linhas.append(
                f"| {_link_nota(c)} | {TEMAS.get(c['tema'], c['tema'])} "
                f"| {c['pendencias'][0]} |"
            )
        linhas += [
            "",
            "Como fechar uma nota: escrever com as suas palavras, citar com "
            "capítulo/página e mudar o status para `ok`. "
            "Veja o [Guia 07](docs/07-rumos-e-proximos-passos.md).",
        ]

    if indice["diario"]:
        linhas += ["", "## Últimas no diário", ""]
        for entrada in sorted(
            indice["diario"], key=lambda d: d.get("data", ""), reverse=True
        )[:5]:
            alvo = entrada.get("caminho", f"diario/{entrada['arquivo']}").replace("diario/", "")
            data = entrada.get("data", "")
            linhas.append(f"- `{data}` [{entrada['titulo'] or entrada['arquivo']}](diario/{alvo})")

    linhas += [
        "",
        "## Como isto é mantido",
        "",
        "Tudo aqui é **gerado a partir de arquivos Markdown** e regenerado a cada "
        "push em `main`. O que você escreve em `conceitos/`, `trilhas/` e `diario/` "
        "vira este painel sem edição manual. Os guias estão em [docs/](docs/index.md).",
        "",
        f"*Painel gerado em {indice.get('atualizado_em', '').replace('T', ' ') or '—'} "
        "a partir de "
        f"{indice['totais']['conceitos'] + indice['totais']['eixos']} notas, "
        f"{indice['totais']['trilhas']} trilhas e {indice['totais']['diario']} entradas de diário.*",
        "",
    ]
    return "\n".join(linhas)


def pagina_conceitos(indice: dict) -> str:
    """Índice de conceitos agrupado por tema (substitui a listagem crua de arquivos)."""
    linhas = [
        "# Conceitos",
        "",
        "Uma nota por ideia. O símbolo indica o estado: ✔ reescrita e conferida, "
        "○ ainda rascunho.",
        "",
        "Use a **busca** (tecla `/`) para procurar por termo, ou navegue pelas "
        "[tags](../tags.md).",
        "",
    ]
    temas = Counter(c["tema"] for c in indice["conceitos"])
    for tema, _ in sorted(temas.items(), key=lambda item: (-item[1], item[0])):
        do_tema = sorted(
            (c for c in indice["conceitos"] if c["tema"] == tema),
            key=lambda c: (c["status"] != "ok", c["conceito"]),
        )
        linhas += [f"## {TEMAS.get(tema, tema)}", ""]
        for c in do_tema:
            glifo = GLIFO_STATUS.get(c["status"], "·")
            tipo = " *(eixo)*" if c["tipo"] == "eixo" else ""
            linhas.append(f"- {glifo} {_link_nota(c, prefixo='')}{tipo}")
        linhas.append("")
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


