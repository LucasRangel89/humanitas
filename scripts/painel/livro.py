"""Montagem editorial do Livro Digital Interativo (Humanitas).

Este módulo transforma os artefatos Markdown (`conceitos/`, `trilhas/`,
`midias/biblioteca.yml`, `estante.md`) em capítulos e verbetes editoriais ricos
para o `site-src/`, sem alterar os arquivos-fonte do repositório.

Princípios:
- Textos e mídias em ordem pedagógica coerente (aula universitária/curso/artigo
  de base -> divulgação -> obra de apoio/filme/podcast).
- Volumes (Trilhas) apresentados como capítulos sequenciais de um livro digital,
  com cada parada integrando o ensaio do conceito, mídias verificadas (com player
  embutido sob demanda), atividades e perguntas reflexivas.
- Conceitos e Eixos apresentados como páginas de ensaio/atlas com metadados
  editoriais, cartão de revisão rápida (auto-teste), mídias integradas e
  navegação contínua dentro dos volumes a que pertencem.
- Compatibilidade integral com `progresso.js` (`ul.task-list > li.task-list-item`)
  e com a auditoria de links relativos do painel.
"""

from __future__ import annotations

import html
import pathlib
import re
from collections import Counter

from .modelo import (
    TEMAS,
    SECAO_TRECHO,
    REGEX_CHECKBOX,
    REGEX_SECAO_NO,
    achar_secao,
    extrair_secao,
    ler,
    limpar_markdown,
    parse_frontmatter,
    secoes,
    titulo_h1,
)
from .midias import ROTULO_IDIOMA, ROTULO_PESO, ROTULO_TIPO

# Ordem curada dos Volumes do Livro Digital:
# Parte I: Fundações Clássicas -> Parte II: Sociedade, Tempo e Espaço -> Parte III: Sínteses
PARTES_LIVRO = [
    (
        "Parte I · A Mente, o Logos e o Laço Social",
        "As três fundações clássicas do projeto: filosofia, psicologia e sociologia.",
        [
            "filosofia-nivel-1.md",
            "psicologia-nivel-1.md",
            "psicologia-nivel-2.md",
            "sociologia-nivel-1.md",
        ],
    ),
    (
        "Parte II · Cultura, Tempo, Espaço e Poder",
        "As lentes que situam o humano na história, no território, na alteridade e na vida pública.",
        [
            "antropologia-nivel-1.md",
            "historia-nivel-1.md",
            "geografia-nivel-1.md",
            "ciencia-politica-nivel-1.md",
            "economia-nivel-1.md",
        ],
    ),
    (
        "Parte III · Travessias e Sínteses Interdisciplinares",
        "Onde todas as disciplinas se encontram: a formação brasileira e o mundo contemporâneo.",
        [
            "pensamento-social-brasileiro.md",
            "integrada-nivel-1.md",
        ],
    ),
]

ROMANOS = ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X", "XI", "XII", "XIII", "XIV", "XV"]

CORES_TEMA = {
    "filosofia": "#2d6a64",
    "sociologia": "#3b4cca",
    "psicologia": "#b85d19",
    "antropologia": "#8c3b5a",
    "historia": "#7c5832",
    "geografia": "#2f6f4e",
    "ciencia-politica": "#5b3e82",
    "economia": "#1f5f7a",
    "integrada": "#7a3e2e",
}

ORDEM_PESO_MIDIA = {
    "aula-universitaria": 0,
    "fonte-academica": 1,
    "curso-livre": 2,
    "divulgacao": 3,
    "obra-de-apoio": 4,
}

ICONE_TIPO_MIDIA = {
    "videoaula": "▶",
    "curso": "🎓",
    "artigo": "📄",
    "resenha": "📑",
    "verbete": "📖",
    "documentario": "🎞",
    "filme": "🎬",
    "podcast": "🎧",
}

YOUTUBE_WATCH_RE = re.compile(
    r"(?:youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{6,15})"
)
YOUTUBE_LIST_RE = re.compile(r"youtube\.com/playlist\?list=([A-Za-z0-9_-]+)")
LINK_CONCEITO_RE = re.compile(r"\]\((?:\.\./)?conceitos/([a-z0-9-]+)\.md(?:#[^)]*)?\)")


def numero_romano(n: int) -> str:
    if 1 <= n <= len(ROMANOS):
        return ROMANOS[n - 1]
    return str(n)


def url_site(origem: str, destino: str) -> str:
    """Calcula o href HTML relativo entre duas páginas do MkDocs (com directory URLs).

    Exemplos:
      url_site("index.md", "trilhas/filosofia-nivel-1.md") -> "trilhas/filosofia-nivel-1/"
      url_site("index.md", "conceitos/index.md")           -> "conceitos/"
      url_site("conceitos/index.md", "conceitos/x.md")     -> "x/"
      url_site("conceitos/a.md", "conceitos/b.md")         -> "../b/"
      url_site("conceitos/a.md", "trilhas/t.md#parada-2")  -> "../../trilhas/t/#parada-2"
      url_site("trilhas/t.md", "conceitos/a.md")           -> "../../conceitos/a/"
      url_site("trilhas/t.md", "trilhas/index.md")         -> "../"
    """
    ancora = ""
    if "#" in destino:
        destino, resto = destino.split("#", 1)
        ancora = f"#{resto}"

    def partes_dir(doc: str) -> list[str]:
        p = pathlib.PurePosixPath(doc)
        if p.name == "index.md":
            return [x for x in p.parent.parts if x != "."]
        return [x for x in p.with_suffix("").parts if x != "."]

    orig_p = partes_dir(origem)
    dest_p = partes_dir(destino)

    comum = 0
    while comum < len(orig_p) and comum < len(dest_p) and orig_p[comum] == dest_p[comum]:
        comum += 1

    subir = [".."] * (len(orig_p) - comum)
    descer = dest_p[comum:]
    todas = subir + descer
    caminho = ("/".join(todas) + "/") if todas else "./"
    return caminho + ancora


def extrair_youtube_embed(url: str) -> tuple[str, str] | None:
    """Devolve (embed_url, thumb_url) se for vídeo/playlist do YouTube."""
    if not url:
        return None
    m = YOUTUBE_WATCH_RE.search(url)
    if m:
        vid = m.group(1)
        return (
            f"https://www.youtube-nocookie.com/embed/{vid}?rel=0",
            f"https://i.ytimg.com/vi/{vid}/hqdefault.jpg",
        )
    m_pl = YOUTUBE_LIST_RE.search(url)
    if m_pl:
        pl = m_pl.group(1)
        return (
            f"https://www.youtube-nocookie.com/embed/videoseries?list={pl}",
            "",
        )
    return None


def ordenar_midias_pedagogicamente(itens: list[dict]) -> list[dict]:
    """Ordena mídias de estudo: PT antes de estrangeiro, base universitária antes de divulgação/apoio."""
    def chave(item: dict):
        idioma_ordem = 0 if item.get("idioma", "pt") == "pt" else 1
        peso_ordem = ORDEM_PESO_MIDIA.get(item.get("peso", ""), 5)
        return (idioma_ordem, peso_ordem, item.get("titulo", ""))

    return sorted(itens, key=chave)


def selo_idioma_curto(item: dict) -> str:
    idioma = item.get("idioma", "pt")
    if idioma == "pt":
        return ""
    rot = ROTULO_IDIOMA.get(idioma, idioma)
    leg = item.get("legendas", "")
    if leg == "pt":
        return f"{rot} · leg. PT"
    if leg == "pt-auto":
        return f"{rot} · leg. auto PT"
    if leg in ("es", "en"):
        return f"{rot} · leg. {leg.upper()}"
    if leg == "nenhuma":
        return f"{rot} · sem legenda"
    return f"{rot} · leg. a conferir"


def papel_pedagogico(item: dict) -> str:
    peso = item.get("peso", "")
    tipo = item.get("tipo", "")
    if peso == "aula-universitaria":
        return "Base universitária"
    if peso == "fonte-academica":
        return "Leitura acadêmica aberta"
    if peso == "curso-livre":
        return "Curso de formação"
    if peso == "divulgacao":
        return "Primeiro contato & revisão"
    if tipo in ("filme", "documentario"):
        return "Cinema & repertório"
    if tipo == "podcast":
        return "Escuta complementar"
    return "Obra de apoio"


def renderizar_cartao_midia_html(
    item: dict,
    *,
    titulos_conceitos: dict[str, str] | None = None,
    origem_doc: str = "midias.md",
    mostrar_ligacoes: bool = False,
    compacto: bool = False,
) -> str:
    """Renderiza um cartão editorial de mídia (com player embutido sob clique para YouTube)."""
    tipo = item.get("tipo", "videoaula")
    peso = item.get("peso", "")
    icone = ICONE_TIPO_MIDIA.get(tipo, "▶")
    rot_tipo = ROTULO_TIPO.get(tipo, tipo)
    rot_peso = ROTULO_PESO.get(peso, peso)
    papel = papel_pedagogico(item)
    idioma_txt = selo_idioma_curto(item)

    titulo = html.escape(item.get("titulo", ""))
    autor = html.escape(item.get("autor", ""))
    canal = html.escape(item.get("canal") or item.get("veiculo") or "")
    onde = html.escape(item.get("onde", ""))
    nota = html.escape(item.get("nota", ""))
    url = item.get("url", "").strip()
    yt = extrair_youtube_embed(url)

    quem_partes = [p for p in (autor, canal) if p]
    quem_html = " · ".join(quem_partes)

    badges = [
        f'<span class="eb-badge eb-badge-papel eb-peso-{html.escape(peso or "apoio")}">{icone} {html.escape(papel)}</span>',
        f'<span class="eb-badge eb-badge-tipo">{html.escape(rot_tipo)}{" · " + html.escape(rot_peso) if rot_peso else ""}</span>',
    ]
    if idioma_txt:
        badges.append(f'<span class="eb-badge eb-badge-idioma">🌐 {html.escape(idioma_txt)}</span>')

    acoes = []
    player_slot = ""
    if yt:
        embed_url, _thumb = yt
        acoes.append(
            f'<button type="button" class="eb-media-play" data-embed="{html.escape(embed_url)}" '
            f'aria-expanded="false">▶ Assistir na página</button>'
        )
        player_slot = '<div class="eb-media-player" hidden></div>'
    if url:
        rot_ext = "Abrir vídeo original ↗" if yt else ("Ler texto completo ↗" if tipo in ("artigo", "resenha", "verbete") else "Abrir na fonte ↗")
        acoes.append(
            f'<a class="eb-media-ext" href="{html.escape(url)}" target="_blank" rel="noopener">{rot_ext}</a>'
        )
    elif onde:
        acoes.append(f'<span class="eb-media-onde">Disponibilidade: <em>{onde}</em></span>')

    ligacoes_html = ""
    if mostrar_ligacoes and item.get("conceitos"):
        titulos_conceitos = titulos_conceitos or {}
        links = []
        for slug_c in item["conceitos"]:
            nome_c = html.escape(titulos_conceitos.get(slug_c) or slug_c.replace("-", " "))
            href_c = url_site(origem_doc, f"conceitos/{slug_c}.md")
            links.append(f'<a class="eb-chip-link" href="{href_c}">{nome_c}</a>')
        ligacoes_html = f'<div class="eb-media-links"><span>Dialoga com:</span> {" ".join(links)}</div>'

    cls_compacto = " eb-media-compact" if compacto else ""
    titulo_el = (
        f'<a href="{html.escape(url)}" target="_blank" rel="noopener">{titulo}</a>'
        if url
        else titulo
    )

    return "\n".join(
        [
            f'<article class="eb-media-card{cls_compacto}" data-tipo="{html.escape(tipo)}" data-peso="{html.escape(peso)}" data-idioma="{html.escape(item.get("idioma", "pt"))}">',
            f'  <div class="eb-media-badges">{"".join(badges)}</div>',
            f'  <h4 class="eb-media-title">{titulo_el}</h4>',
            f'  <div class="eb-media-byline">{quem_html}</div>' if quem_html else "",
            f'  <p class="eb-media-note">{nota}</p>' if nota else "",
            ligacoes_html,
            f'  <div class="eb-media-actions">{"".join(acoes)}</div>' if acoes else "",
            f"  {player_slot}" if player_slot else "",
            "</article>",
        ]
    )


def mapear_volumes_ordenados(trilhas: list[dict]) -> list[dict]:
    """Ordena as trilhas conforme a sequência curada de PARTES_LIVRO e anexa metadados de volume."""
    por_arq = {t["arquivo"]: dict(t) for t in trilhas}
    ordenados: list[dict] = []
    vistos: set[str] = set()
    num = 1
    for nome_parte, desc_parte, arqs in PARTES_LIVRO:
        for arq in arqs:
            if arq in por_arq:
                item = por_arq[arq]
                item["volume_num"] = num
                item["volume_romano"] = numero_romano(num)
                item["parte_nome"] = nome_parte
                item["parte_desc"] = desc_parte
                ordenados.append(item)
                vistos.add(arq)
                num += 1
    # Qualquer trilha nova (como nos testes mini_repo) entra em seguida sem quebrar nada
    for t in trilhas:
        if t["arquivo"] not in vistos:
            item = dict(t)
            item["volume_num"] = num
            item["volume_romano"] = numero_romano(num)
            item["parte_nome"] = "Volumes de Estudo"
            item["parte_desc"] = "Percursos guiados do painel."
            ordenados.append(item)
            num += 1
    return ordenados


def indexar_aparicoes_em_trilhas(raiz: pathlib.Path, volumes: list[dict]) -> dict[str, list[dict]]:
    """Para cada arquivo de conceito (ex.: 'sociologia-habitus.md'), lista em quais volumes/paradas ele entra."""
    aparicoes: dict[str, list[dict]] = {}
    pasta = raiz / "trilhas"
    if not pasta.exists():
        return aparicoes

    for vol in volumes:
        arq_trilha = pasta / vol["arquivo"]
        if not arq_trilha.exists():
            continue
        texto = ler(arq_trilha)
        paradas = extrair_paradas_trilha(texto)
        for idx, parada in enumerate(paradas):
            ant_slug = None
            prox_slug = None
            if idx > 0 and paradas[idx - 1]["conceitos"]:
                ant_slug = paradas[idx - 1]["conceitos"][0]
            if idx + 1 < len(paradas) and paradas[idx + 1]["conceitos"]:
                prox_slug = paradas[idx + 1]["conceitos"][0]

            for slug_c in parada["conceitos"]:
                chave = f"{slug_c}.md"
                aparicoes.setdefault(chave, []).append(
                    {
                        "trilha_arquivo": vol["arquivo"],
                        "trilha_nome": vol["trilha"],
                        "volume_romano": vol["volume_romano"],
                        "parada_num": idx + 1,
                        "parada_total": len(paradas),
                        "anterior": f"{ant_slug}.md" if ant_slug else None,
                        "proximo": f"{prox_slug}.md" if prox_slug else None,
                    }
                )
    return aparicoes


def extrair_paradas_trilha(texto: str) -> list[dict]:
    """Lê os nós/paradas de uma trilha preservando o texto original, subtarefas e conceitos linkados."""
    corpo = texto.split("\n---\n", 1)[-1] if texto.lstrip().startswith("---") else texto

    # Caso 1: Trilhas baseadas em checkboxes numerados ou com hífen
    linhas = corpo.splitlines()
    inicio_checkbox = re.compile(r"^(\s*(?:\d+\.|[-*])\s*\[([ xX])\]\s*)(.+)$")

    paradas: list[dict] = []
    atual: dict | None = None

    for linha in linhas:
        m = inicio_checkbox.match(linha)
        if m:
            if atual:
                paradas.append(atual)
            feita = m.group(2).strip().lower() == "x"
            cabecalho = m.group(3).strip()
            atual = {
                "formato": "checkbox",
                "feita": feita,
                "cabecalho_md": cabecalho,
                "extras_md": [],
                "conceitos": LINK_CONCEITO_RE.findall(cabecalho),
            }
            continue

        if atual is not None:
            if linha.startswith("## "):
                paradas.append(atual)
                atual = None
            elif linha.strip().startswith(("-", "*")) or linha.startswith("   ") or not linha.strip():
                if linha.strip():
                    atual["extras_md"].append(linha.strip().lstrip("-* ").strip())
                    for achado in LINK_CONCEITO_RE.findall(linha):
                        if achado not in atual["conceitos"]:
                            atual["conceitos"].append(achado)
            else:
                paradas.append(atual)
                atual = None

    if atual:
        paradas.append(atual)

    if paradas:
        return paradas

    # Caso 2: Trilha por seções `### Nó ...` (ex.: Integrada)
    achados = list(REGEX_SECAO_NO.finditer(corpo))
    for i, m in enumerate(achados):
        ini = m.end()
        fim = achados[i + 1].start() if i + 1 < len(achados) else len(corpo)
        bloco = corpo[ini:fim]
        # corta se bater em ## Fechamento ou ## Rota
        corte_h2 = re.search(r"^##\s+", bloco, re.M)
        if corte_h2:
            bloco = bloco[: corte_h2.start()]
        slugs = []
        for s in LINK_CONCEITO_RE.findall(bloco):
            if s not in slugs:
                slugs.append(s)
        paradas.append(
            {
                "formato": "secao",
                "feita": False,
                "cabecalho_md": m.group(1).strip(),
                "bloco_md": bloco.strip(),
                "extras_md": [],
                "conceitos": slugs,
            }
        )
    return paradas


def indexar_estante_por_conceito_e_trilha(raiz: pathlib.Path) -> tuple[dict[str, list[dict]], dict[str, list[dict]]]:
    """Lê `estante.md` e indexa obras sugeridas por conceito e por trilha para integrá-las aos capítulos."""
    por_conceito: dict[str, list[dict]] = {}
    por_trilha: dict[str, list[dict]] = {}
    caminho = raiz / "estante.md"
    if not caminho.exists():
        return por_conceito, por_trilha

    texto = ler(caminho)
    partes_h3 = list(re.finditer(r"^###\s+(.+?)\s*$", texto, re.M))
    for i, m in enumerate(partes_h3):
        titulo_obra = m.group(1).strip()
        ini = m.end()
        fim = partes_h3[i + 1].start() if i + 1 < len(partes_h3) else len(texto)
        bloco = texto[ini:fim]
        corte_h2 = re.search(r"^##\s+", bloco, re.M)
        if corte_h2:
            bloco = bloco[: corte_h2.start()]

        m_perg = re.search(r"\*\*Pergunta:\*\*\s*(.+?)(?:\*\*Limite:\*\*|\n\n|$)", bloco, re.S)
        pergunta = limpar_markdown(m_perg.group(1)) if m_perg else ""
        m_tipo = re.search(r"\*\*Tipo:\*\*\s*([^.\n]+)", bloco)
        tipo_obra = limpar_markdown(m_tipo.group(1)) if m_tipo else "obra sugerida"

        item = {
            "titulo": titulo_obra,
            "tipo": tipo_obra,
            "pergunta": pergunta,
        }
        for slug_c in re.findall(r"conceitos/([a-z0-9-]+)\.md", bloco):
            por_conceito.setdefault(slug_c, []).append(item)
        for arq_t in re.findall(r"trilhas/([a-z0-9-]+\.md)", bloco):
            por_trilha.setdefault(arq_t, []).append(item)

    return por_conceito, por_trilha


def _resumo_curto_conceito(texto_nota: str) -> tuple[str, str]:
    """Extrai (definicao_uma_frase, primeiro_paragrafo_explicacao) de uma nota de conceito/eixo."""
    definicao = extrair_secao(texto_nota, "Definição em uma frase") or extrair_secao(
        texto_nota, "A questão em uma frase"
    )
    explicacao = extrair_secao(texto_nota, "Explicação com as minhas palavras") or extrair_secao(
        texto_nota, "Por que é uma grande questão"
    )
    return definicao, explicacao


def enriquecer_nota_conceito(
    registro: dict,
    texto_original: str,
    *,
    midias_do_conceito: list[dict],
    obras_estante: list[dict],
    aparicoes: list[dict],
    titulos_conceitos: dict[str, str],
) -> str:
    """Transforma uma nota de conceito/eixo em uma página editorial de livro digital interativo.

    Preserva todo o texto autoral e os links Markdown originais, adicionando:
    - Cabeçalho editorial de capítulo/ensaio (disciplina, autor/obra de referência, tradição, status);
    - Destaque tipográfico de abertura (Definição / Questão-bússola);
    - Seção integrada de Mídias & Aulas Verificadas em ordem pedagógica com player in-page;
    - Obras da Estante ligadas ao conceito (se houver);
    - Cartão interativo de Revisão Ativa (Flashcard embutido);
    - Rodapé de navegação sequencial nos Volumes/Trilhas onde este conceito aparece.
    """
    partes = texto_original.lstrip().split("---", 2)
    if len(partes) >= 3 and texto_original.lstrip().startswith("---"):
        frontmatter_raw = f"---{partes[1]}---\n"
        corpo = partes[2].lstrip("\n")
    else:
        frontmatter_raw = ""
        corpo = texto_original

    tema = registro.get("tema", "sem-tema")
    tema_nome = TEMAS.get(tema, tema)
    cor = CORES_TEMA.get(tema, "#3b4cca")
    eh_eixo = registro.get("tipo") == "eixo"
    status = registro.get("status", "rascunho")
    nivel = registro.get("nivel", "iniciante")
    autor = registro.get("autor_origem", "")
    obra = registro.get("obra_origem", "")
    tradicao = registro.get("tradicao", "")
    evidencia = registro.get("nivel_evidencia", "")

    # Remove H1 padrão repetitivo ("# Conceito — X") para dar lugar ao cabeçalho editorial com H1 limpo
    corpo_sem_h1 = re.sub(r"^#\s+.+?\n+", "", corpo, count=1)

    tipo_rotulo = "Eixo Transversal de Debate" if eh_eixo else f"Ensaio Conceitual · {tema_nome}"
    status_rotulo = "✔ Texto revisado (padrão-ouro)" if status == "ok" else "○ Ensaio-base de estudo"

    meta_chips = [
        f'<span class="eb-meta-pill" style="--tema-cor:{cor}">{html.escape(tema_nome)}</span>',
        f'<span class="eb-meta-pill">{html.escape(nivel.capitalize())}</span>',
        f'<span class="eb-meta-pill eb-status-{html.escape(status)}">{status_rotulo}</span>',
    ]
    if tradicao:
        meta_chips.append(f'<span class="eb-meta-pill">Tradição: {html.escape(tradicao)}</span>')
    if evidencia:
        meta_chips.append(f'<span class="eb-meta-pill">Evidência: {html.escape(evidencia)}</span>')

    referencia_html = ""
    if autor or obra:
        ref_partes = []
        if autor:
            ref_partes.append(f"<strong>{html.escape(autor)}</strong>")
        if obra:
            ref_partes.append(f"<em>{html.escape(obra)}</em>")
        referencia_html = f'<div class="eb-chapter-source">Referência central: {" — ".join(ref_partes)}</div>'

    origem_doc = f"conceitos/{registro['arquivo']}"
    trilhas_topo = ""
    if aparicoes:
        links_trilha = [
            f'<a href="{url_site(origem_doc, "trilhas/" + ap["trilha_arquivo"] + "#parada-" + str(ap["parada_num"]))}">'
            f'Vol. {ap["volume_romano"]} · Parada {ap["parada_num"]}/{ap["parada_total"]}</a>'
            for ap in aparicoes[:3]
        ]
        trilhas_topo = (
            '<div class="eb-chapter-breadcrumbs">'
            '<span>Situado em:</span> ' + " · ".join(links_trilha) + "</div>"
        )

    cabecalho = "\n".join(
        [
            f'<header class="eb-chapter-header" style="--tema-cor:{cor}">',
            f'  <div class="eb-chapter-kicker">{html.escape(tipo_rotulo)}</div>',
            f"# {registro['conceito']}",
            "",
            f'  <div class="eb-chapter-meta">{"".join(meta_chips)}</div>',
            f"  {referencia_html}" if referencia_html else "",
            f"  {trilhas_topo}" if trilhas_topo else "",
            "</header>",
            "",
        ]
    )

    # Bloco de mídias curadas em ordem pedagógica (logo após o texto autoral, como caderno multimídia integrado)
    midias_ordenadas = ordenar_midias_pedagogicamente(midias_do_conceito)
    bloco_midias = ""
    if midias_ordenadas:
        cartoes = [
            renderizar_cartao_midia_html(
                m,
                titulos_conceitos=titulos_conceitos,
                origem_doc=origem_doc,
                mostrar_ligacoes=False,
            )
            for m in midias_ordenadas
        ]
        bloco_midias = "\n".join(
            [
                "",
                "## Mídias e aulas verificadas para este tema",
                "",
                '<p class="eb-section-lead">Selecionadas e conferidas na biblioteca do projeto, ordenadas da '
                "<strong>base universitária e acadêmica</strong> ao <strong>primeiro contato audiovisual e cinema</strong>. "
                "Assista na própria página com o caderno aberto.</p>",
                "",
                '<div class="eb-media-grid">',
                *cartoes,
                "</div>",
                "",
            ]
        )

    bloco_estante = ""
    if obras_estante:
        itens_est = []
        for ob in obras_estante:
            itens_est.append(
                f'<div class="eb-shelf-callout">'
                f'<div class="eb-shelf-title">📚 {html.escape(ob["titulo"])} '
                f'<span class="eb-shelf-type">({html.escape(ob["tipo"])})</span></div>'
                f'<p>{html.escape(ob["pergunta"])}</p>'
                f"</div>"
            )
        bloco_estante = "\n".join(
            [
                "",
                "## Obras de fôlego sugeridas na Estante",
                "",
                *itens_est,
                "",
            ]
        )

    # Cartão de auto-teste / revisão ativa (flashcard do próprio conceito)
    definicao = registro.get("definicao", "").strip()
    bloco_flashcard = ""
    if definicao:
        pergunta_fc = (
            f"Qual é a questão central do eixo «{registro['conceito']}»?"
            if eh_eixo
            else f"Como definir «{registro['conceito']}» em uma frase, sem olhar o texto?"
        )
        bloco_flashcard = "\n".join(
            [
                "",
                '<section class="eb-recall-box" aria-label="Auto-teste de retenção">',
                '  <div class="eb-recall-kicker">🧠 Pausa de retenção ativa</div>',
                f'  <p class="eb-recall-question">{html.escape(pergunta_fc)}</p>',
                '  <details class="eb-recall-answer">',
                "    <summary>Revelar síntese-guia para conferir sua resposta</summary>",
                f"    <p>{html.escape(definicao)}</p>",
                '    <p class="eb-recall-actions">'
                f'<a href="{url_site(origem_doc, "registrar.md")}">Registrar síntese no Diário / Reescrever nota →</a></p>',
                "  </details>",
                "</section>",
                "",
            ]
        )

    # Navegação sequencial de livro (Anterior / Volume / Próximo) para cada trilha onde o conceito está
    bloco_nav_livro = ""
    if aparicoes:
        nav_cards = []
        for ap in aparicoes:
            ant_html = '<span class="eb-seq-disabled">Início do volume</span>'
            if ap["anterior"]:
                slug_ant = ap["anterior"].removesuffix(".md")
                nome_ant = html.escape(titulos_conceitos.get(slug_ant) or slug_ant)
                href_ant = url_site(origem_doc, f"conceitos/{ap['anterior']}")
                ant_html = f'<a class="eb-seq-prev" href="{href_ant}">← {nome_ant}</a>'

            href_fech = url_site(origem_doc, f"trilhas/{ap['trilha_arquivo']}#fechamento")
            prox_html = f'<a class="eb-seq-next" href="{href_fech}">Síntese do volume →</a>'
            if ap["proximo"]:
                slug_prox = ap["proximo"].removesuffix(".md")
                nome_prox = html.escape(titulos_conceitos.get(slug_prox) or slug_prox)
                href_prox = url_site(origem_doc, f"conceitos/{ap['proximo']}")
                prox_html = f'<a class="eb-seq-next" href="{href_prox}">{nome_prox} →</a>'

            href_trilha = url_site(origem_doc, f"trilhas/{ap['trilha_arquivo']}")
            nav_cards.append(
                f'<nav class="eb-book-pager" aria-label="Navegação do volume">'
                f'  <div class="eb-pager-vol">'
                f'    <span>Volume {ap["volume_romano"]} · Parada {ap["parada_num"]} de {ap["parada_total"]}</span>'
                f'    <a href="{href_trilha}">{html.escape(ap["trilha_nome"])}</a>'
                f"  </div>"
                f'  <div class="eb-pager-links">{ant_html}{prox_html}</div>'
                f"</nav>"
            )
        bloco_nav_livro = "\n" + "\n".join(nav_cards) + "\n"

    return frontmatter_raw + cabecalho + corpo_sem_h1.rstrip() + "\n" + bloco_midias + bloco_estante + bloco_flashcard + bloco_nav_livro


def enriquecer_pagina_trilha(
    vol: dict,
    texto_original: str,
    *,
    conceitos_por_slug: dict[str, dict],
    textos_conceitos: dict[str, str],
    midias_por_conceito: dict[str, list[dict]],
    obras_estante_trilha: list[dict],
    titulos_conceitos: dict[str, str],
    volume_anterior: dict | None = None,
    volume_proximo: dict | None = None,
) -> str:
    """Transforma uma trilha em um Volume / Capítulo completo do Livro Digital Interativo.

    Mantém intacta a estrutura `<ul class="task-list"><li class="task-list-item">` gerada
    pelo Markdown para que `progresso.js` continue marcando e exportando os nós pelo
    índice exato, mas envolve cada parada com:
    - Resumo e tese central do conceito;
    - Leitura expandida da nota no próprio capítulo (opcional sob clique) + link para o ensaio completo;
    - Mídias verificadas daquela parada ordenadas pedagogicamente (com player embutido);
    - Atividade prática e pergunta reflexiva destacadas como caderno de exercícios.
    """
    partes = texto_original.lstrip().split("---", 2)
    if len(partes) >= 3 and texto_original.lstrip().startswith("---"):
        frontmatter_raw = f"---{partes[1]}---\n"
        corpo = partes[2].lstrip("\n")
    else:
        frontmatter_raw = ""
        corpo = texto_original

    tema = vol.get("tema", "sem-tema")
    tema_nome = TEMAS.get(tema, tema)
    cor = CORES_TEMA.get(tema, "#3b4cca")
    fm = parse_frontmatter(texto_original)
    obras_base = str(fm.get("obra_origem") or "").strip()
    nivel = vol.get("nivel", "iniciante")

    paradas = extrair_paradas_trilha(texto_original)

    # Conta mídias únicas ligadas a este volume
    midias_unicas = {
        m["id"]
        for p in paradas
        for s in p["conceitos"]
        for m in midias_por_conceito.get(s, [])
    }

    cabecalho = [
        f'<header class="eb-volume-header" style="--tema-cor:{cor}">',
        f'  <div class="eb-volume-kicker">{html.escape(vol.get("parte_nome", "Volume de Estudo"))} · Volume {vol["volume_romano"]}</div>',
        f"# {vol['trilha']}",
        "",
        '  <div class="eb-chapter-meta">',
        f'    <span class="eb-meta-pill" style="--tema-cor:{cor}">{html.escape(tema_nome)}</span>',
        f'    <span class="eb-meta-pill">Nível {html.escape(nivel)}</span>',
        f'    <span class="eb-meta-pill">{len(paradas)} paradas de estudo</span>',
        f'    <span class="eb-meta-pill">{len(midias_unicas)} mídias integradas</span>',
        "  </div>",
    ]
    if obras_base:
        cabecalho.append(
            f'  <div class="eb-chapter-source">Obras de horizonte deste volume: <em>{html.escape(obras_base)}</em></div>'
        )
    cabecalho += ["</header>", ""]

    origem_doc = f"trilhas/{vol['arquivo']}"
    # Se for trilha em seções (ex.: Integrada, com 3 rotas), preserva o texto rico das rotas e injeta as mídias e cartões de conceito ao fim de cada nó `### Nó ...`
    if paradas and paradas[0]["formato"] == "secao":
        corpo_sem_h1 = re.sub(r"^#\s+.+?\n+", "", corpo, count=1)
        corpo_enriquecido = _enriquecer_trilha_rotas(
            corpo_sem_h1,
            origem_doc=origem_doc,
            conceitos_por_slug=conceitos_por_slug,
            textos_conceitos=textos_conceitos,
            midias_por_conceito=midias_por_conceito,
            titulos_conceitos=titulos_conceitos,
        )
        rodape = _rodape_volume(origem_doc, volume_anterior, volume_proximo)
        return frontmatter_raw + "\n".join(cabecalho) + corpo_enriquecido + "\n" + rodape

    # Para as trilhas em capítulos/paradas (checkboxes):
    objetivo = achar_secao(corpo, "Objetivo da trilha").strip()
    prereq = achar_secao(corpo, "Pré-requisitos").strip()
    como_ia = achar_secao(corpo, "Como usar com IA").strip()
    exploracao = achar_secao(corpo, "Modo Exploração Livre").strip()
    conclusao = achar_secao(corpo, "Conclusão da trilha").strip()

    linhas = list(cabecalho)

    if objetivo or prereq:
        linhas += [
            '<section class="eb-volume-prologue" markdown>',
            "",
            "## Prólogo do Volume",
            "",
            objetivo,
            "",
        ]
        if prereq:
            linhas += [
                '<div class="eb-prologue-note" markdown>',
                f"**Ponto de partida e preparação:** {prereq}",
                "</div>",
                "",
            ]
        linhas += ["</section>", ""]

    # Sumário rápido das paradas do capítulo
    if paradas:
        linhas += [
            '<nav class="eb-stops-toc" aria-label="Percurso deste volume">',
            '  <div class="eb-stops-toc-title">Sumário do percurso</div>',
            '  <ol class="eb-stops-toc-list">',
        ]
        for idx, p in enumerate(paradas, start=1):
            titulo_limpo = limpar_markdown(p["cabecalho_md"]).split("—")[0].strip()
            linhas.append(f'    <li><a href="#parada-{idx}"><span>{idx:02d}.</span> {html.escape(titulo_limpo[:55])}</a></li>')
        linhas += ["  </ol>", "</nav>", ""]

    linhas += [
        "## Percurso de Leitura e Mídia",
        "",
        '<p class="eb-section-lead">Percorra na ordem sugerida. Em cada parada, leia a síntese conceitual, '
        "abra o ensaio completo ou assista à aula correspondente sem sair do capítulo, realize a prática "
        "e marque a caixa quando concluir sua síntese no diário.</p>",
        "",
    ]

    # Lista de tarefas contínua (1. [ ] ...) para 100% de compatibilidade com progresso.js e regex
    for idx, p in enumerate(paradas, start=1):
        marca = "x" if p["feita"] else " "
        linhas.append(f'{idx}. [{marca}] <span id="parada-{idx}" class="eb-stop-anchor"></span>{p["cabecalho_md"]}')
        linhas.append("")

        # Cartões dos conceitos desta parada (tese + leitura rápida expansível)
        for slug_c in p["conceitos"]:
            reg = conceitos_por_slug.get(slug_c)
            txt_c = textos_conceitos.get(slug_c, "")
            if not reg:
                continue
            definicao, explicacao = _resumo_curto_conceito(txt_c)
            trecho_apoio = extrair_secao(txt_c, SECAO_TRECHO)
            importancia = extrair_secao(txt_c, "Por que este conceito importa")

            href_c = url_site(origem_doc, f"conceitos/{reg['arquivo']}")
            linhas.append(f'    <div class="eb-stop-dossier" style="--tema-cor:{cor}">')
            linhas.append('      <div class="eb-dossier-head">')
            linhas.append(
                f'        <span class="eb-dossier-kicker">{"Eixo de debate" if reg.get("tipo") == "eixo" else "Ideia-chave"}</span>'
            )
            linhas.append(
                f'        <a class="eb-dossier-open" href="{href_c}">Abrir ensaio completo →</a>'
            )
            linhas.append("      </div>")
            if definicao:
                linhas.append(f'      <blockquote class="eb-dossier-thesis">{html.escape(definicao)}</blockquote>')
            if explicacao:
                linhas.append("      <details class=\"eb-dossier-excerpt\">")
                linhas.append(f"        <summary>Ler explicação de «{html.escape(reg['conceito'])}» aqui no capítulo</summary>")
                linhas.append(f'        <div class="eb-dossier-body"><p>{html.escape(explicacao)}</p>')
                if trecho_apoio:
                    linhas.append(f'        <p class="eb-dossier-quote"><strong>Na obra:</strong> {html.escape(trecho_apoio)}</p>')
                if importancia:
                    linhas.append(f'        <p class="eb-dossier-why"><strong>Por que importa:</strong> {html.escape(importancia)}</p>')
                linhas.append(
                    f'        <p><a href="{href_c}">Continuar lendo conexões e debates deste conceito →</a></p></div>'
                )
                linhas.append("      </details>")
            linhas.append("    </div>")
            linhas.append("")

        # Atividades e perguntas reflexivas da parada
        if p["extras_md"]:
            linhas.append('    <div class="eb-stop-practice" markdown>')
            for ex in p["extras_md"]:
                linhas.append(f"    - {ex}")
            linhas.append("    </div>")
            linhas.append("")

        # Mídias verificadas desta parada (deduplicadas e em ordem pedagógica)
        midias_parada: list[dict] = []
        vistos_m: set[str] = set()
        for slug_c in p["conceitos"]:
            for m in midias_por_conceito.get(slug_c, []):
                if m["id"] not in vistos_m:
                    vistos_m.add(m["id"])
                    midias_parada.append(m)
        midias_parada = ordenar_midias_pedagogicamente(midias_parada)

        if midias_parada:
            rotulo_qtd = f"{len(midias_parada)} mídia{'s' if len(midias_parada) > 1 else ''} verificada{'s' if len(midias_parada) > 1 else ''}"
            linhas.append('    <details class="eb-stop-media">')
            linhas.append(
                f"      <summary>🎬 Caderno Audiovisual & Leituras desta parada ({rotulo_qtd})</summary>"
            )
            linhas.append('      <div class="eb-media-grid eb-media-grid-compact">')
            for m in midias_parada:
                cartao = renderizar_cartao_midia_html(
                    m,
                    titulos_conceitos=titulos_conceitos,
                    origem_doc=origem_doc,
                    mostrar_ligacoes=False,
                    compacto=True,
                )
                for linha_c in cartao.splitlines():
                    linhas.append("      " + linha_c)
            linhas.append("      </div>")
            linhas.append("    </details>")
            linhas.append("")

    # Obras da Estante ligadas ao volume
    if obras_estante_trilha:
        linhas += [
            "## Livros e Filmes da Estante para este Volume",
            "",
        ]
        vistos_ob = set()
        for ob in obras_estante_trilha:
            if ob["titulo"] in vistos_ob:
                continue
            vistos_ob.add(ob["titulo"])
            linhas.append(
                f'<div class="eb-shelf-callout">'
                f'<div class="eb-shelf-title">📚 {html.escape(ob["titulo"])} '
                f'<span class="eb-shelf-type">({html.escape(ob["tipo"])})</span></div>'
                f'<p>{html.escape(ob["pergunta"])}</p>'
                f"</div>\n"
            )

    # Apêndice metodológico enxuto e recolhível (não polui a leitura, mas preserva 100% do conteúdo e links)
    if como_ia or exploracao or conclusao:
        linhas += [
            '<span id="fechamento"></span>',
            "## Caderno de Método e Fechamento",
            "",
        ]
        if conclusao:
            linhas += [conclusao, ""]
        if exploracao:
            linhas += [
                '<details class="eb-method-box" markdown>',
                "<summary>🧭 Modo Exploração Livre (desvios férteis)</summary>",
                "",
                exploracao,
                "",
                "</details>",
                "",
            ]
        if como_ia:
            linhas += [
                '<details class="eb-method-box" markdown>',
                "<summary>🤖 Como estudar este volume com IA (Tutor & NotebookLM)</summary>",
                "",
                como_ia,
                "",
                "</details>",
                "",
            ]

    linhas.append(_rodape_volume(origem_doc, volume_anterior, volume_proximo))
    return frontmatter_raw + "\n".join(linhas)


def _enriquecer_trilha_rotas(
    corpo: str,
    *,
    origem_doc: str,
    conceitos_por_slug: dict[str, dict],
    textos_conceitos: dict[str, str],
    midias_por_conceito: dict[str, list[dict]],
    titulos_conceitos: dict[str, str],
) -> str:
    """Enriquece trilhas divididas em Rotas (`### Nó A1...`), injetando cartões de tese e mídias em cada módulo."""
    achados = list(REGEX_SECAO_NO.finditer(corpo))
    if not achados:
        return corpo

    saida = [corpo[: achados[0].start()]]
    for i, m in enumerate(achados):
        ini = m.start()
        fim = achados[i + 1].start() if i + 1 < len(achados) else len(corpo)
        trecho = corpo[ini:fim]
        corte_h2 = re.search(r"^##\s+", trecho, re.M)
        pos_corte = ""
        if corte_h2:
            pos_corte = trecho[corte_h2.start() :]
            trecho = trecho[: corte_h2.start()]

        slugs = []
        for s in LINK_CONCEITO_RE.findall(trecho):
            if s not in slugs:
                slugs.append(s)

        midias_mod: list[dict] = []
        vistos_m: set[str] = set()
        for s in slugs:
            for item_m in midias_por_conceito.get(s, []):
                if item_m["id"] not in vistos_m:
                    vistos_m.add(item_m["id"])
                    midias_mod.append(item_m)
        midias_mod = ordenar_midias_pedagogicamente(midias_mod)[:6]

        extra = []
        if slugs:
            extra.append('<div class="eb-route-concepts">')
            for s in slugs[:6]:
                reg = conceitos_por_slug.get(s)
                if not reg:
                    continue
                definicao = reg.get("definicao", "")[:160]
                href_c = url_site(origem_doc, f"conceitos/{reg['arquivo']}")
                extra.append(
                    f'<a class="eb-mini-concept" href="{href_c}">'
                    f'<strong>{html.escape(reg["conceito"])}</strong>'
                    f'<span>{html.escape(definicao)}{"…" if len(reg.get("definicao","")) > 160 else ""}</span>'
                    f"</a>"
                )
            extra.append("</div>")

        if midias_mod:
            extra.append('<details class="eb-stop-media">')
            extra.append(
                f"<summary>🎬 Mídias verificadas para este módulo ({len(midias_mod)} selecionadas)</summary>"
            )
            extra.append('<div class="eb-media-grid eb-media-grid-compact">')
            for item_m in midias_mod:
                extra.append(
                    renderizar_cartao_midia_html(
                        item_m,
                        titulos_conceitos=titulos_conceitos,
                        origem_doc=origem_doc,
                        mostrar_ligacoes=True,
                        compacto=True,
                    )
                )
            extra.append("</div></details>")

        saida.append(trecho.rstrip() + "\n\n" + "\n".join(extra) + "\n\n" + pos_corte)

    return "".join(saida)


def _rodape_volume(origem_doc: str, anterior: dict | None, proximo: dict | None) -> str:
    ant_html = f'<a class="eb-seq-prev" href="{url_site(origem_doc, "trilhas/index.md")}">← Sumário dos Volumes</a>'
    if anterior:
        ant_html = (
            f'<a class="eb-seq-prev" href="{url_site(origem_doc, "trilhas/" + anterior["arquivo"])}">'
            f'← Vol. {anterior["volume_romano"]}: {html.escape(anterior["trilha"].split(":")[0])}</a>'
        )
    prox_html = f'<a class="eb-seq-next" href="{url_site(origem_doc, "conceitos/index.md")}">Explorar Atlas de Conceitos →</a>'
    if proximo:
        prox_html = (
            f'<a class="eb-seq-next" href="{url_site(origem_doc, "trilhas/" + proximo["arquivo"])}">'
            f'Vol. {proximo["volume_romano"]}: {html.escape(proximo["trilha"].split(":")[0])} →</a>'
        )
    return (
        '<nav class="eb-book-pager eb-volume-pager" aria-label="Navegação entre volumes">\n'
        f'  <div class="eb-pager-vol"><span>Continuidade da obra</span><a href="{url_site(origem_doc, "trilhas/index.md")}">Todos os Volumes do Livro</a></div>\n'
        f'  <div class="eb-pager-links">{ant_html}{prox_html}</div>\n'
        "</nav>\n"
    )


def gerar_pagina_midias_interativa(
    itens: list[dict],
    atualizado_em: str = "",
    titulos: dict[str, str] | None = None,
    cobertura: list[dict] | None = None,
    *,
    tem_guia_11: bool = True,
) -> str:
    """Versão interativa de `midias.md` para o site (com busca, filtros por formato/peso e players embutidos)."""
    validos = [i for i in itens if not i.get("_invalido")]
    titulos = titulos or {}

    por_tema: dict[str, list[dict]] = {}
    for item in validos:
        por_tema.setdefault(item.get("tema", ""), []).append(item)

    contagem_tipos = Counter(i["tipo"] for i in validos)
    ordem_temas = (
        "filosofia",
        "psicologia",
        "sociologia",
        "antropologia",
        "historia",
        "geografia",
        "ciencia-politica",
        "economia",
        "integrada",
    )

    linhas = [
        '<header class="eb-book-cover eb-cinemateca-hero">',
        '  <div class="eb-cover-kicker">Cinemateca, Salas de Aula & Artigos Abertos</div>',
        "# Mídias",
        "",
        f'  <p class="eb-cover-subtitle"><strong>{len(validos)} obras audiovisuais e textos abertos</strong> '
        "conferidos um a um e integrados aos capítulos do livro — aulas de graduação, cursos completos, "
        "artigos acadêmicos, documentários, filmes e podcasts.</p>",
        "</header>",
        "",
        '<div class="eb-reader-tip">',
        "  <strong>Regra de leitura:</strong> mídia abre a porta e cria intuição, mas não substitui o texto primário. "
        "Comece pelas <em>Bases universitárias</em> ou pelo <em>Primeiro contato</em>, assista na própria página "
        "e feche cada sessão anotando uma ideia com as suas palavras.",
        "</div>",
        "",
        '<section class="eb-filter-bar" aria-label="Filtrar mídias">',
        '  <input id="eb-media-search" class="humanitas-search" type="search" '
        'placeholder="Buscar aula, professor, canal, filme ou conceito… (ex.: Bourdieu, Kant, UNIVESP, Matrix)" '
        'aria-label="Buscar na biblioteca de mídias">',
        '  <div class="eb-filter-row" id="eb-media-tema-filters">',
        f'    <button type="button" class="humanitas-filter active" data-media-tema="todos">Todos os temas ({len(validos)})</button>',
    ]
    for t in ordem_temas:
        if por_tema.get(t):
            linhas.append(
                f'    <button type="button" class="humanitas-filter" data-media-tema="{t}">'
                f'{html.escape(TEMAS.get(t, t))} ({len(por_tema[t])})</button>'
            )
    linhas += [
        "  </div>",
        '  <div class="eb-filter-row eb-filter-row-secondary" id="eb-media-peso-filters">',
        '    <button type="button" class="eb-pill-filter active" data-media-peso="todos">Todas as camadas</button>',
        '    <button type="button" class="eb-pill-filter" data-media-peso="aula-universitaria">🎓 Base universitária</button>',
        '    <button type="button" class="eb-pill-filter" data-media-peso="curso-livre">📚 Cursos livres</button>',
        '    <button type="button" class="eb-pill-filter" data-media-peso="fonte-academica">📄 Artigos acadêmicos</button>',
        '    <button type="button" class="eb-pill-filter" data-media-peso="divulgacao">💡 Primeiro contato</button>',
        '    <button type="button" class="eb-pill-filter" data-media-peso="obra-de-apoio">🎬 Cinema & obras de apoio</button>',
        "  </div>",
        '  <div id="eb-media-counter" class="eb-filter-counter"></div>',
        "</section>",
        "",
    ]

    outros = [t for t in por_tema if t not in ordem_temas]
    for tema in list(ordem_temas) + sorted(outros):
        do_tema = por_tema.get(tema, [])
        if not do_tema:
            continue
        ordenados = ordenar_midias_pedagogicamente(do_tema)
        cor = CORES_TEMA.get(tema, "#3b4cca")
        linhas += [
            f'<section class="eb-media-theme-section" data-theme-section="{tema}" style="--tema-cor:{cor}">',
            "",
            f"## {TEMAS.get(tema, tema)}",
            "",
            f'<p class="eb-section-lead">{len(ordenados)} indicações verificadas — ordenadas da formação universitária às obras de repertório.</p>',
            "",
            '<div class="eb-media-grid">',
        ]
        for item in ordenados:
            linhas.append(
                renderizar_cartao_midia_html(
                    item,
                    titulos_conceitos=titulos,
                    origem_doc="midias.md",
                    mostrar_ligacoes=True,
                )
            )
        linhas += ["</div>", "", "</section>", ""]

    cobertura = cobertura or []
    if cobertura:
        total_nos = sum(c["nos"] for c in cobertura)
        total_cob = sum(c["cobertos"] for c in cobertura)
        linhas += [
            "## Cobertura audiovisual dos Volumes",
            "",
            f"**{total_cob} de {total_nos} paradas conceituais** dos volumes já contam com mídia verificada em português integrada diretamente no capítulo.",
            "",
            "| Volume | Paradas com mídia | Cobertura |",
            "|---|---|---|",
        ]
        for c in sorted(cobertura, key=lambda item: item["trilha"]):
            cheia = "█" * round(c["pct"] / 10) + "░" * (10 - round(c["pct"] / 10))
            linhas.append(
                f"| [{c['trilha']}](trilhas/{c['arquivo']}) | {c['cobertos']}/{c['nos']} ({c['pct']}%) | `{cheia}` |"
            )
        linhas.append("")

    if atualizado_em:
        ref_guia = (
            "Protocolo editorial no [Guia 11](docs/11-midias-e-videoaulas.md)."
            if tem_guia_11
            else "Protocolo editorial verificado item a item."
        )
        linhas.append(
            f"*Curadoria verificada em {atualizado_em} · {ref_guia}*  \n"
            f"*Formatos no acervo: {', '.join(f'{ROTULO_TIPO.get(k, k)} ({v})' for k, v in sorted(contagem_tipos.items()))}.*\n"
        )
    return "\n".join(linhas)


def transformar_estante_editorial(texto: str) -> str:
    """Enriquece visualmente `estante.md` como uma galeria de livros, cinema e séries no site."""
    if not texto.strip().startswith("# Estante"):
        return texto

    partes_h2 = list(re.finditer(r"^##\s+(.+?)\s*$", texto, re.M))
    if not partes_h2:
        return texto

    abertura = [
        '<header class="eb-book-cover eb-shelf-hero">',
        '  <div class="eb-cover-kicker">Leituras de Fôlego & Cinema Comentado</div>',
        "# Estante de Obras",
        "",
        '  <p class="eb-cover-subtitle">Livros fundamentais, filmes, documentários e séries conectados às paradas '
        "dos volumes — acompanhados de perguntas orientadoras para transformar leitura e sessão em reflexão própria.</p>",
        "</header>",
        "",
    ]

    saida = list(abertura)
    for idx, m2 in enumerate(partes_h2):
        titulo_sec = m2.group(1).strip()
        ini = m2.end()
        fim = partes_h2[idx + 1].start() if idx + 1 < len(partes_h2) else len(texto)
        corpo_sec = texto[ini:fim].strip()

        partes_h3 = list(re.finditer(r"^###\s+(.+?)\s*$", corpo_sec, re.M))
        if not partes_h3:
            saida += [f"## {titulo_sec}", "", corpo_sec, ""]
            continue

        saida += [f"## {titulo_sec}", "", '<div class="eb-shelf-grid" markdown>', ""]
        for j, m3 in enumerate(partes_h3):
            obra_nome = m3.group(1).strip()
            b_ini = m3.end()
            b_fim = partes_h3[j + 1].start() if j + 1 < len(partes_h3) else len(corpo_sec)
            bloco_obra = corpo_sec[b_ini:b_fim].strip()
            icone = "📖" if "Livros" in titulo_sec else ("🎬" if "tela" in titulo_sec else "🌍")
            saida += [
                '<article class="eb-shelf-card" markdown>',
                "",
                f"### {icone} {obra_nome}",
                "",
                bloco_obra,
                "",
                "</article>",
                "",
            ]
        saida += ["</div>", ""]

    return "\n".join(saida)
