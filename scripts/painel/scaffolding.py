from __future__ import annotations

import datetime as dt
import pathlib
import re

from .modelo import TEMAS, NIVEIS_VALIDOS, NIVEIS_EVIDENCIA_VALIDOS, ler, normalizar, parse_tags, listar_md, rel
from .indice import coletar_conceitos
from .progresso import pendencias_da_nota

# tipo -> (template, pasta-destino, campos extras)
TIPOS_NOVA = {
    "conceito": ("template-conceito.md", "conceitos", ("autor", "obra", "nivel")),
    "eixo": ("template-eixo.md", "conceitos", ("autor", "nivel")),
    "ficha": ("template-livro.md", "acervo/fichas", ("autor", "obra", "ano")),
    "trecho": ("template-trecho.md", "trechos", ("autor", "obra", "capitulo", "pagina")),
    "diario": ("template-diario.md", "diario", ("origem", "data")),
}

ROTULO_H1 = {
    "conceito": "Nome do conceito",
    "eixo": "Nome da grande questão",
    "ficha": "Título da obra",
    "trecho": "tema curto do trecho",
    "diario": "tema curto da reflexão",
}


def slug(texto: str) -> str:
    """Nome de arquivo compatível com o GitHub: sem acento, minúsculo, com hífens."""
    return re.sub(r"-+", "-", normalizar(texto).replace(" ", "-")).strip("-")


def yaml_escalar(valor) -> str:
    if isinstance(valor, (list, tuple)):
        return "[" + ", ".join(str(v) for v in valor) + "]"
    if isinstance(valor, int):
        return str(valor)
    return '"' + str(valor).replace('"', '\\"') + '"'


def serializar_frontmatter(dados: dict) -> str:
    linhas = ["---"]
    for chave, valor in dados.items():
        linhas.append(f"{chave}: {yaml_escalar(valor)}")
    linhas.append("---")
    return "\n".join(linhas) + "\n"


def corpo_do_template(caminho: pathlib.Path) -> str:
    """Corpo do template, sem cabeçalho e sem os blocos de instrução."""
    texto = ler(caminho)
    if texto.lstrip().startswith("---"):
        partes = texto.lstrip().split("---", 2)
        if len(partes) >= 3:
            texto = partes[2]
    texto = re.sub(r"<!--.*?-->", "", texto, flags=re.S)
    return texto.strip("\n")


def desativar_links_quebrados(texto: str, raiz: pathlib.Path, pasta: pathlib.Path) -> str:
    """Troca exemplos de link do template (que não existem) por texto simples."""

    def trocar(match: re.Match) -> str:
        rotulo, alvo = match.group(1), match.group(2)
        if alvo.startswith(("http://", "https://", "#", "mailto:")):
            return match.group(0)
        caminho = alvo.split("#")[0].strip()
        if not caminho.lower().endswith(".md"):
            return match.group(0)
        if (pasta / caminho).exists() or (raiz / caminho).exists():
            return match.group(0)
        return rotulo

    return re.sub(r"\[([^\]]+)\]\(([^)\s]+)\)", trocar, texto)


def cmd_nova(raiz: pathlib.Path, **opcoes) -> int:
    tipo = (opcoes.get("tipo") or "").strip().lower()
    if tipo not in TIPOS_NOVA:
        print(f"Tipo inválido: {tipo!r}. Use um de: {', '.join(TIPOS_NOVA)}.")
        return 1

    nome = (opcoes.get("nome") or "").strip()
    if not nome:
        print("Informe o nome com --nome (ex.: --nome \"Habitus\").")
        return 1

    tema = (opcoes.get("tema") or "").strip().lower()
    if tema not in TEMAS:
        print(f"Tema inválido: {tema!r}. Use um de: {', '.join(sorted(TEMAS))}.")
        return 1

    template, pasta_nome, _ = TIPOS_NOVA[tipo]
    origem = raiz / "templates" / template
    if not origem.exists():
        print(f"Template não encontrado: {rel(origem, raiz)}.")
        return 1

    nivel = (opcoes.get("nivel") or "iniciante").strip().lower()
    if nivel not in NIVEIS_VALIDOS:
        print(f"Nível inválido: {nivel!r}. Use um de: {', '.join(sorted(NIVEIS_VALIDOS))}.")
        return 1

    autor = (opcoes.get("autor") or "").strip()
    obra = (opcoes.get("obra") or "").strip()
    data = (opcoes.get("data") or dt.date.today().isoformat()).strip()
    tags = parse_tags(opcoes.get("tags") or f"{tema}")
    if tema not in tags:
        tags = [tema, *tags]

    fonte_verificada = (opcoes.get("fonte_verificada") or "nao").strip().lower()
    if fonte_verificada not in ("sim", "nao"):
        fonte_verificada = "nao"
    # PR3 novos campos
    tradicao = (opcoes.get("tradicao") or "").strip()
    nivel_evidencia = (opcoes.get("nivel_evidencia") or "teorica").strip().lower()
    if nivel_evidencia not in NIVEIS_EVIDENCIA_VALIDOS:
        nivel_evidencia = "teorica"
    def _parse_lista(valor):
        if not valor:
            return []
        if isinstance(valor, list):
            return valor
        return [s.strip() for s in str(valor).split(",") if s.strip()]
    contestado_por = _parse_lista(opcoes.get("contestado_por"))
    eixos = _parse_lista(opcoes.get("eixos"))
    relacoes = _parse_lista(opcoes.get("relacoes"))
    frente = {
        "conceito": {
            "conceito": nome,
            "obra_origem": obra,
            "autor_origem": autor,
            "tema": tema,
            "tipo": "conceito",
            "nivel": nivel,
            "fonte_verificada": fonte_verificada,
            "tradicao": tradicao,
            "nivel_evidencia": nivel_evidencia,
            "contestado_por": contestado_por,
            "eixos": eixos,
            "relacoes": relacoes,
            "status": "rascunho",
            "tags": tags,
        },
        "eixo": {
            "eixo": nome,
            "tema": tema,
            "tipo": "eixo",
            "nivel": nivel,
            "fonte_verificada": fonte_verificada,
            "tradicao": tradicao,
            "nivel_evidencia": nivel_evidencia,
            "contestado_por": contestado_por,
            "eixos": eixos,
            "relacoes": relacoes,
            "status": "rascunho",
            "tags": ["eixo", *tags],
        },
        "ficha": {
            "obra": obra or nome,
            "autor": autor,
            "ano": opcoes.get("ano") or "",
            "tema": tema,
            "tipo": "ficha-de-leitura",
            "status": "em-andamento",
            "tags": tags,
        },
        "trecho": {
            "obra": obra or nome,
            "autor": autor,
            "capitulo": opcoes.get("capitulo") or "",
            "pagina": opcoes.get("pagina") or "",
            "tema": tema,
            "tipo": "trecho",
            "tags": tags,
        },
        "diario": {
            "data": data,
            "tema": tema,
            "origem": opcoes.get("origem") or nome,
            "tipo": "diario",
            "tags": ["diario", *tags],
        },
    }[tipo]

    ident = slug(nome)
    if tipo == "conceito":
        arquivo = f"{tema}-{ident}.md"
    elif tipo == "eixo":
        arquivo = f"eixo-{ident}.md"
    elif tipo == "ficha":
        arquivo = f"{ident}-ficha.md"
    elif tipo == "diario":
        arquivo = f"{data}-{tema}-{ident}.md"
    else:
        arquivo = f"{ident}.md"

    pasta = raiz / pasta_nome
    destino = pasta / arquivo
    if destino.exists() and not opcoes.get("forcar"):
        print(f"Já existe: {rel(destino, raiz)}. Use --forcar para sobrescrever.")
        return 1

    corpo = corpo_do_template(origem)
    corpo = corpo.replace(ROTULO_H1[tipo], nome)
    corpo = desativar_links_quebrados(corpo, raiz, pasta)
    pendente = (
        "<!-- PENDENTE (padrão-ouro): preencha as seções e depois rode\n"
        f"     `python -m scripts.painel pendencias --tema {tema}`.\n"
        "     Ao terminar, mude o status para ok. -->\n"
    )
    conteudo = serializar_frontmatter(frente) + "\n" + pendente + corpo + "\n"

    pasta.mkdir(parents=True, exist_ok=True)
    destino.write_text(conteudo, encoding="utf-8")
    print(f"Criado: {rel(destino, raiz)}")
    print()
    print("Próximos passos:")
    print(f"  1. preencha as seções (sem consultar a IA enquanto escreve)")
    print(f"  2. python -m scripts.painel pendencias --tema {tema}")
    print(f"  3. ao terminar, troque status: rascunho -> ok")
    return 0


def cmd_pendencias(raiz: pathlib.Path, **opcoes) -> int:
    """Checklist do padrão-ouro: o que falta em cada nota para virar `ok`."""
    registros = coletar_conceitos(raiz)
    tema = (opcoes.get("tema") or "").strip().lower()
    limite = opcoes.get("limite")
    mostrar_prontas = bool(opcoes.get("prontas"))

    if tema:
        if tema not in TEMAS:
            print(f"Tema inválido: {tema!r}. Use um de: {', '.join(sorted(TEMAS))}.")
            return 1
        registros = [r for r in registros if r["tema"] == tema]

    blocos, prontas = [], []
    for registro in registros:
        faltas = pendencias_da_nota(registro)
        if not faltas:
            prontas.append(registro)
            continue
        blocos.append((len(faltas), registro, faltas))

    blocos.sort(key=lambda item: (-item[0], item[2][0]))
    if limite:
        blocos = blocos[:limite]

    print("# Pendências para o padrão-ouro")
    if tema:
        print(f"# tema: {TEMAS[tema]}")
    print()

    if not blocos:
        print("Nenhuma pendência: as notas filtradas estão no padrão-ouro.")
    for quantidade, registro, faltas in blocos:
        print(f"{quantidade} pendência(s) — {registro['conceito']} ({rel(raiz / 'conceitos' / registro['arquivo'], raiz)})")
        for falta in faltas:
            print(f"    - {falta}")
        print()

    if mostrar_prontas and prontas:
        print("Já no padrão-ouro:")
        for registro in prontas:
            print(f"    ok  {registro['conceito']} ({registro['arquivo']})")
        print()

    total = len(registros)
    print(
        f"Resumo: {total} nota(s) analisada(s), {len(prontas)} pronta(s), "
        f"{total - len(prontas)} com pendência."
    )
    if limite and total - len(prontas) > limite:
        print(f"Mostrando as {limite} notas com mais pendências (use --limite para ver mais).")
    return 0


# ---------------------------------------------------------------------------
