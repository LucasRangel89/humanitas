"""Biblioteca de mídias: videoaulas, artigos, resenhas e outras obras de apoio.

A fonte única é `midias/biblioteca.yml` (curadoria humana, com data e método de
verificação). Deste arquivo saem dois artefatos gerados:

- `midias.md` — página pública, agrupada por tema, que vai para o repositório e
  para o site;
- `indices/midias.json` — versão para máquina (contagens e links).

Regra de ouro: mídia é **apoio**, nunca fonte. Nenhuma entrada entra sem ter
sido aberta e conferida — por isso `verificado_em` e `verificado_como` são
obrigatórios e a auditoria cobra os dois.
"""

from __future__ import annotations

import json
import pathlib
import re

import yaml

from .modelo import TEMAS

TIPOS_MIDIA = (
    "videoaula",
    "curso",
    "podcast",
    "documentario",
    "filme",
    "artigo",
    "resenha",
    "verbete",
)

PESOS = (
    "aula-universitaria",
    "curso-livre",
    "divulgacao",
    "fonte-academica",
    "obra-de-apoio",
)

# Como o título e o autor foram conferidos.
#   oembed            -> API de oEmbed do YouTube (devolve título e canal oficiais)
#   pagina            -> página aberta e lida
#   material-do-autor -> veio dos planos/anexos do próprio autor, sem URL
ORIGENS_VERIFICACAO = ("oembed", "pagina", "material-do-autor")

# Tipos que precisam de URL pública; os demais precisam dizer onde encontrar.
COM_URL = {"videoaula", "curso", "artigo", "resenha", "verbete"}
SEM_URL = {"filme", "podcast", "documentario"}

CAMPOS_OBRIGATORIOS = ("id", "tipo", "titulo", "autor", "tema", "verificado_em", "verificado_como")

# Idioma da mídia. O projeto é em português: `pt` é o padrão e é o único que
# conta para a cobertura das trilhas. `en` e `es` entram só como apoio onde o
# material em português é fraco ou inexistente (ver Guia 11, §2).
IDIOMAS = ("pt", "en", "es")

# Situação das legendas, do ponto de vista de quem vai assistir.
#   pt              -> há legenda em português, revisada ou publicada pela fonte
#   pt-auto         -> legenda automática do YouTube traduzida para português
#                      (texto de máquina, com erros previsíveis)
#   es / en         -> legenda em espanhol/inglês
#   nenhuma         -> não há legenda
#   nao-verificado  -> não consegui confirmar; a nota diz o que se sabe
LEGENDAS = ("pt", "pt-auto", "es", "en", "nenhuma", "nao-verificado")

ARQUIVO = pathlib.Path("midias") / "biblioteca.yml"
SAIDA_MD = pathlib.Path("midias.md")
SAIDA_JSON = pathlib.Path("indices") / "midias.json"

DATA_ISO = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ID_VALIDO = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


# ---------------------------------------------------------------------------
# Leitura e validação
# ---------------------------------------------------------------------------


def carregar(raiz: pathlib.Path) -> tuple[list[dict], str, list[str]]:
    """Lê a biblioteca. Devolve (itens, atualizado_em, erros)."""
    caminho = raiz / ARQUIVO
    if not caminho.exists():
        return [], "", []
    try:
        dados = yaml.safe_load(caminho.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:  # YAML inválido
        return [], "", [f"{ARQUIVO}: YAML inválido ({exc})."]

    itens = dados.get("itens") or []
    if not isinstance(itens, list):
        return [], "", [f"{ARQUIVO}: `itens` deveria ser uma lista."]
    limpos = []
    for bruto in itens:
        if not isinstance(bruto, dict):
            limpos.append({"_invalido": True})
            continue
        item = dict(bruto)
        item["conceitos"] = [str(c).strip() for c in (item.get("conceitos") or []) if str(c).strip()]
        item["id"] = str(item.get("id") or "").strip()
        item["tipo"] = str(item.get("tipo") or "").strip()
        item["peso"] = str(item.get("peso") or "").strip()
        item["tema"] = str(item.get("tema") or "").strip()
        item["url"] = str(item.get("url") or "").strip()
        item["onde"] = str(item.get("onde") or "").strip()
        item["verificado_como"] = str(item.get("verificado_como") or "").strip()
        item["verificado_em"] = str(item.get("verificado_em") or "").strip()
        item["idioma"] = str(item.get("idioma") or "pt").strip()
        item["legendas"] = str(item.get("legendas") or "").strip()
        limpos.append(item)
    return limpos, str(dados.get("atualizado_em") or "").strip(), []


def validar(
    itens: list[dict],
    conceitos_existentes: set[str],
    *,
    atualizado_em: str = "",
) -> tuple[list[str], list[str]]:
    """Erros que bloqueiam e avisos informativos da biblioteca de mídias."""
    erros: list[str] = []
    avisos: list[str] = []
    vistos_id: dict[str, int] = {}
    vistos_url: dict[str, str] = {}
    legendas_pendentes: list[str] = []
    legendas_automaticas: list[str] = []

    if atualizado_em and not DATA_ISO.match(atualizado_em):
        erros.append(f"{ARQUIVO}: `atualizado_em` deve ser AAAA-MM-DD (tem {atualizado_em!r}).")

    for i, item in enumerate(itens, start=1):
        if item.get("_invalido"):
            erros.append(f"{ARQUIVO}: entrada #{i} não é um mapa YAML.")
            continue
        rotulo = item.get("id") or f"#{i}"
        for campo in CAMPOS_OBRIGATORIOS:
            if not item.get(campo):
                erros.append(f"{ARQUIVO}: {rotulo} sem campo obrigatório `{campo}`.")
        if item.get("id") and not ID_VALIDO.match(item["id"]):
            erros.append(f"{ARQUIVO}: id fora do padrão (minúsculas e hífens): {item['id']!r}.")
        if item.get("id"):
            if item["id"] in vistos_id:
                erros.append(f"{ARQUIVO}: id duplicado: {item['id']}.")
            vistos_id[item["id"]] = i
        if item.get("tipo") and item["tipo"] not in TIPOS_MIDIA:
            erros.append(
                f"{ARQUIVO}: {rotulo} tem tipo inválido ({item['tipo']!r}); "
                f"use um de {', '.join(TIPOS_MIDIA)}."
            )
        if item.get("peso") and item["peso"] not in PESOS:
            erros.append(
                f"{ARQUIVO}: {rotulo} tem peso inválido ({item['peso']!r}); "
                f"use um de {', '.join(PESOS)}."
            )
        if item.get("tema") and item["tema"] not in TEMAS:
            erros.append(f"{ARQUIVO}: {rotulo} tem tema inválido ({item['tema']!r}).")
        if item.get("verificado_como") and item["verificado_como"] not in ORIGENS_VERIFICACAO:
            erros.append(
                f"{ARQUIVO}: {rotulo} tem verificado_como inválido "
                f"({item['verificado_como']!r}); use um de {', '.join(ORIGENS_VERIFICACAO)}."
            )
        if item.get("idioma") and item["idioma"] not in IDIOMAS:
            erros.append(
                f"{ARQUIVO}: {rotulo} tem idioma inválido ({item['idioma']!r}); "
                f"use um de {', '.join(IDIOMAS)}."
            )
        if item.get("legendas") and item["legendas"] not in LEGENDAS:
            erros.append(
                f"{ARQUIVO}: {rotulo} tem legendas inválido ({item['legendas']!r}); "
                f"use um de {', '.join(LEGENDAS)}."
            )
        if item.get("idioma", "pt") != "pt":
            if not item.get("legendas"):
                erros.append(
                    f"{ARQUIVO}: {rotulo} está em {item['idioma']} e precisa declarar "
                    "`legendas` (pt, es, en, nenhuma ou nao-verificado)."
                )
            elif item["legendas"] == "pt-auto":
                # Tradução de máquina: aceita por decisão do projeto, mas nunca
                # silenciosa — a auditoria conta quantas são.
                legendas_automaticas.append(rotulo)
            elif item["legendas"] == "nao-verificado":
                # Um aviso por biblioteca, não por item: a dúvida é a mesma para
                # todas as mídias daquele idioma, e uma linha por item afogaria
                # os outros avisos da auditoria.
                legendas_pendentes.append(f"{rotulo} ({item['idioma']})")
        if item.get("verificado_em") and not DATA_ISO.match(item["verificado_em"]):
            erros.append(
                f"{ARQUIVO}: {rotulo} tem verificado_em fora do padrão AAAA-MM-DD "
                f"({item['verificado_em']!r})."
            )

        tipo = item.get("tipo")
        if tipo in COM_URL:
            url = item.get("url", "")
            if not url:
                erros.append(f"{ARQUIVO}: {rotulo} ({tipo}) precisa de `url`.")
            elif not url.startswith("https://"):
                erros.append(f"{ARQUIVO}: {rotulo} tem url que não é https ({url}).")
            if url:
                if url in vistos_url:
                    erros.append(
                        f"{ARQUIVO}: url repetida em {rotulo} e {vistos_url[url]} ({url})."
                    )
                vistos_url[url] = rotulo
            if item.get("verificado_como") == "material-do-autor":
                erros.append(
                    f"{ARQUIVO}: {rotulo} ({tipo}) tem URL e não pode ser marcado como "
                    "material-do-autor — confira a página e use `oembed` ou `pagina`."
                )
        if tipo in SEM_URL and not item.get("url") and not item.get("onde"):
            erros.append(f"{ARQUIVO}: {rotulo} ({tipo}) precisa de `url` ou de `onde`.")

        for conceito in item.get("conceitos", []):
            if conceito not in conceitos_existentes:
                erros.append(
                    f"{ARQUIVO}: {rotulo} aponta para conceito inexistente: {conceito}."
                )
        if not item.get("conceitos") and tipo not in SEM_URL:
            avisos.append(
                f"{ARQUIVO}: {rotulo} não está ligado a nenhuma nota (campo `conceitos`)."
            )

    if itens and not any(i.get("verificado_em") for i in itens if not i.get("_invalido")):
        erros.append(f"{ARQUIVO}: nenhuma entrada tem `verificado_em`.")

    if legendas_automaticas:
        avisos.append(
            f"{ARQUIVO}: {len(legendas_automaticas)} mídia(s) com legenda automática "
            "em português (tradução de máquina, não revisada): "
            f"{', '.join(legendas_automaticas)}."
        )

    if legendas_pendentes:
        avisos.append(
            f"{ARQUIVO}: {len(legendas_pendentes)} mídia(s) em outro idioma com "
            "`legendas: nao-verificado` — confira no player antes de tratar como "
            f"apoio principal ({', '.join(legendas_pendentes)})."
        )

    return erros, avisos


# ---------------------------------------------------------------------------
# Renderização
# ---------------------------------------------------------------------------

ROTULO_TIPO = {
    "videoaula": "videoaula",
    "curso": "curso",
    "podcast": "podcast",
    "documentario": "documentário",
    "filme": "filme",
    "artigo": "artigo",
    "resenha": "resenha",
    "verbete": "verbete",
}

ROTULO_PESO = {
    "aula-universitaria": "aula universitária",
    "curso-livre": "curso livre",
    "divulgacao": "divulgação",
    "fonte-academica": "fonte acadêmica",
    "obra-de-apoio": "obra de apoio",
}

ROTULO_VERIFICACAO = {
    "oembed": "título e canal conferidos na API do YouTube",
    "pagina": "página aberta e conferida",
    "material-do-autor": "veio dos planos/anexos do autor (sem URL)",
}

ORDEM_TEMAS = ("psicologia", "filosofia", "sociologia", "antropologia", "historia",
               "geografia", "ciencia-politica", "economia", "integrada")


def _data_br(iso: str) -> str:
    if DATA_ISO.match(iso or ""):
        ano, mes, dia = iso.split("-")
        return f"{dia}/{mes}/{ano}"
    return iso or "—"


def _escapar(texto: str) -> str:
    return str(texto).replace("|", r"\|").strip()


def _celula_titulo(item: dict) -> str:
    titulo = _escapar(item.get("titulo", ""))
    url = item.get("url", "")
    if url:
        return f"[{titulo}]({url})"
    onde = item.get("onde", "")
    if onde:
        return f"{titulo} — *{_escapar(onde)}*"
    return titulo


ROTULO_IDIOMA = {"en": "inglês", "es": "espanhol"}


def _marca_idioma(item: dict) -> str:
    """Selo de idioma/legenda; vazio quando a mídia é em português."""
    idioma = item.get("idioma", "pt")
    if idioma == "pt":
        return ""
    rotulo = ROTULO_IDIOMA.get(idioma, idioma)
    legenda = item.get("legendas", "")
    if legenda == "pt":
        volta = f"{rotulo}, legenda em português"
    elif legenda == "pt-auto":
        volta = f"{rotulo}, legenda automática em português"
    elif legenda in ("es", "en"):
        volta = f"{rotulo}, legenda em {ROTULO_IDIOMA.get(legenda, legenda)}"
    elif legenda == "nenhuma":
        volta = f"{rotulo}, sem legenda"
    else:
        volta = f"{rotulo}, legenda não conferida"
    return f"**{volta}**"


def _celula_quem(item: dict) -> str:
    partes = [item.get("autor", "")]
    if item.get("canal"):
        partes.append(f"canal {item['canal']}")
    elif item.get("veiculo"):
        partes.append(item["veiculo"])
    marca = _marca_idioma(item)
    if marca:
        partes.append(marca)
    return _escapar(" · ".join(p for p in partes if p))


def titulos_dos_conceitos(raiz: pathlib.Path) -> dict[str, str]:
    """slug do arquivo -> nome legível da nota (fallback: slug humanizado)."""
    titulos: dict[str, str] = {}
    pasta = raiz / "conceitos"
    if not pasta.exists():
        return titulos
    for arquivo in sorted(pasta.glob("*.md")):
        if arquivo.name == "README.md":
            continue
        texto = arquivo.read_text(encoding="utf-8")
        nome = ""
        for linha in texto.splitlines():
            if linha.startswith("# "):
                nome = linha[2:].strip()
                break
        for prefixo in ("Conceito — ", "Eixo — ", "Ficha — ", "Trecho — ", "Diário — "):
            nome = nome.removeprefix(prefixo)
        titulos[arquivo.stem] = nome or arquivo.stem.replace("-", " ")
    return titulos


def _celula_ligacao(item: dict, titulos: dict[str, str] | None = None) -> str:
    if not item.get("conceitos"):
        return "—"
    titulos = titulos or {}
    partes = []
    for conceito in item["conceitos"]:
        nome = titulos.get(conceito) or conceito.replace("-", " ")
        partes.append(f"[{_escapar(nome)}](conceitos/{conceito}.md)")
    return " · ".join(partes)


LINK_CONCEITO = re.compile(r"\]\((?:\.\./)?conceitos/([a-z0-9-]+)\.md")


def cobertura_trilhas(raiz: pathlib.Path, itens: list[dict]) -> list[dict]:
    """Para cada trilha, quantos nós já têm pelo menos uma mídia ligada.

    O nó é contado como coberto quando o link daquele nó aponta para uma nota
    que aparece em algum `conceitos` da biblioteca. Nó sem link (ex.: "Síntese
    no diário") não entra na conta: não é conteúdo que vídeo resolva.

    `cobertos` conta **só mídia em português** — é o placar do projeto.
    `cobertos_amplo` conta também espanhol e inglês: serve para medir apoio
    extra, nunca para inflar a cobertura em português.
    """
    validos = [item for item in itens if not item.get("_invalido")]
    com_midia = {c for item in validos if item.get("idioma", "pt") == "pt"
                 for c in item.get("conceitos", [])}
    com_midia_amplo = {c for item in validos for c in item.get("conceitos", [])}
    pasta = raiz / "trilhas"
    if not pasta.exists():
        return []
    saida = []
    for arquivo in sorted(pasta.glob("*.md")):
        if arquivo.name == "README.md":
            continue
        texto = arquivo.read_text(encoding="utf-8")
        nome = arquivo.stem.replace("-", " ")
        acha_nome = re.search(r"^trilha:\s*\"?(.+?)\"?\s*$", texto, re.M)
        if acha_nome:
            nome = acha_nome.group(1).strip()
            # "Antropologia — Nível 1: estranhar o familiar" -> "Antropologia — Nível 1"
            nome = nome.split(":")[0].strip()
        corpo = texto.split("\n---\n", 1)[-1] if texto.startswith("---") else texto
        # cada linha de nó com link é um nó; slugs únicos por linha
        nos = []
        for linha in corpo.splitlines():
            if not re.match(r"^\s*(?:\d+\.|[-*])\s", linha):
                continue
            achados = LINK_CONCEITO.findall(linha)
            if achados:
                nos.append(achados)
        if not nos:
            continue
        cobertos = sum(1 for slugs in nos if any(s in com_midia for s in slugs))
        cobertos_amplo = sum(1 for slugs in nos if any(s in com_midia_amplo for s in slugs))
        saida.append(
            {
                "arquivo": arquivo.name,
                "trilha": nome,
                "nos": len(nos),
                "cobertos": cobertos,
                "pct": round(cobertos * 100 / len(nos)) if nos else 0,
                "cobertos_amplo": cobertos_amplo,
            }
        )
    return saida


def gerar_markdown(
    itens: list[dict],
    atualizado_em: str = "",
    titulos: dict[str, str] | None = None,
    cobertura: list[dict] | None = None,
) -> str:
    """Monta a página `midias.md` (determinística: sem data de geração)."""
    validos = [i for i in itens if not i.get("_invalido")]
    por_tema: dict[str, list[dict]] = {}
    for item in validos:
        por_tema.setdefault(item.get("tema", ""), []).append(item)

    tipos: dict[str, int] = {}
    for item in validos:
        tipos[item["tipo"]] = tipos.get(item["tipo"], 0) + 1
    canais: dict[str, int] = {}
    for item in validos:
        nome = item.get("canal")
        if nome:
            canais[nome] = canais.get(nome, 0) + 1

    linhas = [
        '<div class="humanitas-hero" markdown>',
        "",
        "# Mídias",
        "",
        f"**{len(validos)} indicações** conferidas uma a uma — videoaulas, cursos, "
        "artigos, resenhas, filmes e podcasts, ligados às notas e às trilhas.",
        "",
        "Cada link foi aberto antes de entrar aqui: o título e o canal são os da fonte, "
        "e a data de conferência está na tabela. Se um vídeo sair do ar, corrija em "
        "[`midias/biblioteca.yml`](https://github.com/LucasRangel89/humanitas/blob/main/midias/biblioteca.yml).",
        "",
        "</div>",
        "",
        "## Antes de assistir: mídia é apoio, não fonte",
        "",
        "- **Vídeo não substitui obra.** A seção *Trecho de apoio* da nota exige "
        "citação com capítulo e página — isso só sai do texto.",
        "- **Regra dos 20 minutos**: assista com o caderno aberto e pare para escrever "
        "uma frase com as suas palavras. Se não sair frase, o vídeo não entrou.",
        "- **Aula universitária primeiro, divulgação depois.** As linhas marcadas como "
        "*aula universitária* são de graduação e pós; as de *divulgação* servem para "
        "o primeiro contato e para revisar.",
        "- **Ao terminar, escolha um nó da trilha** e marque na página da trilha. "
        "Mídia sem nota e sem diário é entretenimento — bom, mas não é estudo.",
        "",
        "## Sumário",
        "",
        "| Tema | Indicações | Onde começar |",
        "|---|---|---|",
    ]

    for tema in ORDEM_TEMAS:
        do_tema = por_tema.get(tema, [])
        if not do_tema:
            continue
        # a primeira aula universitária é o melhor ponto de entrada
        entrada = next(
            (i for i in do_tema if i.get("peso") == "aula-universitaria"),
            do_tema[0],
        )
        url_entrada = entrada.get("url") or f"#{tema}"
        titulo_entrada = _escapar(entrada["titulo"]).replace("[", r"\[").replace("]", r"\]")
        linhas.append(
            f"| [{TEMAS.get(tema, tema)}](#{tema}) | {len(do_tema)} "
            f"| [{titulo_entrada}]({url_entrada}) |"
        )
    outros = [t for t in por_tema if t not in ORDEM_TEMAS]
    linhas += ["", "## Indicações por tema", ""]

    for tema in list(ORDEM_TEMAS) + sorted(outros):
        do_tema = por_tema.get(tema, [])
        if not do_tema:
            continue
        linhas += [
            f"### {TEMAS.get(tema, tema)}",
            "",
            "| Tipo | Título | Quem publica | Por que assistir | Liga a |",
            "|---|---|---|---|---|",
        ]
        for item in do_tema:
            tipo = ROTULO_TIPO.get(item.get("tipo", ""), item.get("tipo", ""))
            peso = ROTULO_PESO.get(item.get("peso", ""), "")
            marca = f"{tipo} · {peso}" if peso else tipo
            linhas.append(
                f"| {_escapar(marca)} | {_celula_titulo(item)} | {_celula_quem(item)} "
                f"| {_escapar(item.get('nota', ''))} | {_celula_ligacao(item, titulos)} |"
            )
        linhas.append("")

    cobertura = cobertura or []
    if cobertura:
        total_nos = sum(c["nos"] for c in cobertura)
        total_cob = sum(c["cobertos"] for c in cobertura)
        linhas += [
            "## Cobertura das trilhas",
            "",
            f"**{total_cob} de {total_nos} nós com link** já têm pelo menos uma mídia "
            "**em português** ligada. Ficam fora da conta os nós sem link (síntese no "
            "diário) e as trilhas cujos nós não apontam para notas (a Integrada, por "
            "exemplo).",
            "",
            "| Trilha | Nós com mídia | |",
            "|---|---|---|",
        ]
        for c in sorted(cobertura, key=lambda c: (c["pct"], c["arquivo"])):
            nome = c.get("trilha") or c["arquivo"].removesuffix(".md").replace("-", " ")
            cheia = "█" * round(c["pct"] / 10) + "░" * (10 - round(c["pct"] / 10))
            linhas.append(
                f"| {_escapar(nome)} | {c['cobertos']}/{c['nos']} ({c['pct']}%) | `{cheia}` |"
            )
        total_amplo = sum(c.get("cobertos_amplo", c["cobertos"]) for c in cobertura)
        if total_amplo > total_cob:
            linhas += [
                f"Contando também as indicações em espanhol e inglês, "
                f"**{total_amplo} de {total_nos}** nós têm alguma mídia. Essa segunda "
                "contagem mede apoio extra, não substitui a de português.",
                "",
            ]
        linhas.append("")

    if canais:
        linhas += [
            "## Canais que valem assinar",
            "",
            "Nomes exatamente como aparecem no YouTube para os itens acima. "
            "Artigos e periódicos aparecem nas tabelas por tema.",
            "",
            "| Canal | Indicações aqui |",
            "|---|---|",
        ]
        for nome, qtd in sorted(canais.items(), key=lambda par: (-par[1], par[0])):
            linhas.append(f"| {_escapar(nome)} | {qtd} |")
        linhas.append("")

    linhas += [
        "## Como esta lista é mantida",
        "",
        "1. Toda mídia nasce em `midias/biblioteca.yml`, com `tipo`, `peso`, `tema`, "
        "os `conceitos` que ela ajuda a estudar e a data de verificação.",
        "2. `make painel` gera esta página e `indices/midias.json`.",
        "3. A auditoria recusa entrada sem verificação, com URL repetida, com tema "
        "inválido ou apontando para nota que não existe.",
        "4. O protocolo completo (como conferir, o que entra e o que nunca entra) "
        "está no [Guia 11](docs/11-midias-e-videoaulas.md).",
        "",
    ]
    if atualizado_em:
        linhas += [
            f"*Última curadoria: {_data_br(atualizado_em)} · "
            f"{len(validos)} indicações em {len([t for t in por_tema if por_tema[t]])} temas.*",
            "",
        ]
    return "\n".join(linhas)


def montar_json(
    itens: list[dict], atualizado_em: str = "", cobertura: list[dict] | None = None
) -> dict:
    validos = [i for i in itens if not i.get("_invalido")]
    por_tipo: dict[str, int] = {}
    por_tema: dict[str, int] = {}
    por_verificacao: dict[str, int] = {}
    por_idioma: dict[str, int] = {}
    for item in validos:
        por_tipo[item["tipo"]] = por_tipo.get(item["tipo"], 0) + 1
        por_tema[item["tema"]] = por_tema.get(item["tema"], 0) + 1
        por_verificacao[item["verificado_como"]] = por_verificacao.get(item["verificado_como"], 0) + 1
        idioma = item.get("idioma", "pt")
        por_idioma[idioma] = por_idioma.get(idioma, 0) + 1
    return {
        "versao": 1,
        "atualizado_em": atualizado_em,
        "totais": {
            "itens": len(validos),
            "por_tipo": dict(sorted(por_tipo.items())),
            "por_tema": dict(sorted(por_tema.items())),
            "por_verificacao": dict(sorted(por_verificacao.items())),
            "por_idioma": dict(sorted(por_idioma.items())),
        },
        "cobertura_trilhas": cobertura or [],
        "itens": [
            {
                "id": i["id"],
                "tipo": i["tipo"],
                "peso": i["peso"],
                "titulo": i.get("titulo", ""),
                "autor": i.get("autor", ""),
                "canal": i.get("canal", ""),
                "veiculo": i.get("veiculo", ""),
                "url": i.get("url", ""),
                "onde": i.get("onde", ""),
                "tema": i["tema"],
                "conceitos": i.get("conceitos", []),
                "nota": i.get("nota", ""),
                "verificado_em": i["verificado_em"],
                "verificado_como": i["verificado_como"],
                "idioma": i.get("idioma", "pt"),
                "legendas": i.get("legendas", ""),
            }
            for i in validos
        ],
    }


def gravar(raiz: pathlib.Path) -> tuple[pathlib.Path, pathlib.Path, int]:
    """Regrava `midias.md` e `indices/midias.json`. Devolve (md, json, nº de itens)."""
    itens, atualizado_em, _erros = carregar(raiz)
    cobertura = cobertura_trilhas(raiz, itens)
    texto = gerar_markdown(itens, atualizado_em, titulos_dos_conceitos(raiz), cobertura)
    destino_md = raiz / SAIDA_MD
    destino_md.write_text(texto, encoding="utf-8")

    destino_json = raiz / SAIDA_JSON
    destino_json.parent.mkdir(parents=True, exist_ok=True)
    destino_json.write_text(
        json.dumps(
            montar_json(itens, atualizado_em, cobertura), ensure_ascii=False, indent=1
        ) + "\n",
        encoding="utf-8",
    )
    return destino_md, destino_json, len([i for i in itens if not i.get("_invalido")])


def verificar(raiz: pathlib.Path) -> tuple[list[str], list[str]]:
    """Validação usada pela auditoria (erros bloqueiam o CI)."""
    itens, atualizado_em, erros_leitura = carregar(raiz)
    if erros_leitura:
        return erros_leitura, []
    if not itens and not (raiz / ARQUIVO).exists():
        return [], []
    conceitos = {
        p.stem for p in (raiz / "conceitos").glob("*.md") if p.name != "README.md"
    } if (raiz / "conceitos").exists() else set()
    erros, avisos = validar(itens, conceitos, atualizado_em=atualizado_em)

    destino = raiz / SAIDA_MD
    esperado = gerar_markdown(
        itens, atualizado_em, titulos_dos_conceitos(raiz), cobertura_trilhas(raiz, itens)
    )
    if destino.exists() and destino.read_text(encoding="utf-8") != esperado:
        erros.append(
            f"{SAIDA_MD} está desatualizado — rode `python -m scripts.painel midias`."
        )
    elif itens and not destino.exists():
        avisos.append(f"{SAIDA_MD} ainda não foi gerado — rode `make painel`.")
    return erros, avisos
