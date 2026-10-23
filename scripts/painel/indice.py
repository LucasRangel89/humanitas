from __future__ import annotations

import datetime as dt
import json
import pathlib
import re
from collections import Counter

from .modelo import (
    RAIZ_PADRAO, TEMAS, SECOES_OBRIGATORIAS, SECAO_TRECHO, MARCADOR_TEMAS, MARCADOR_PROGRESSO, REGEX_CHECKBOX, REGEX_SECAO_NO,
    ErroFrontmatter, _limpar_erros_frontmatter, _registrar_erro_frontmatter,
    ler, parse_frontmatter, parse_tags, secoes, achar_secao, extrair_secao, titulo_h1, listar_md, rel, eh_placeholder,
    limpar_markdown, sem_codigo, normalizar, substituir_bloco,
)

from .progresso import pendencias_da_nota

# ---------------------------------------------------------------------------
# Coleta de dados
# ---------------------------------------------------------------------------


def coletar_conceitos(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "conceitos", recursivo=True):
        texto = ler(arq)
        try:
            fm = parse_frontmatter(texto)
        except ErroFrontmatter as exc:
            _registrar_erro_frontmatter(rel(arq, raiz), str(exc))
            continue
        if not texto.lstrip().startswith("---"):
            _registrar_erro_frontmatter(rel(arq, raiz), "Arquivo sem frontmatter (esperado cabeçalho YAML entre '---').")
            continue
        tipo = str(fm.get("tipo") or ("eixo" if fm.get("eixo") else "conceito")).strip()
        nome = (
            fm.get("conceito")
            or fm.get("eixo")
            or titulo_h1(texto)
        )
        nome = re.sub(r"^(Conceito|Eixo)\s*[—–-]\s*", "", str(nome or "")).strip()
        definicao = extrair_secao(texto, "Definição em uma frase") or extrair_secao(
            texto, "A questão em uma frase"
        )
        faltando = [
            secao
            for secao in SECOES_OBRIGATORIAS.get(tipo, [])
            if not achar_secao(texto, secao).strip()
        ]
        registros.append(
            {
                "arquivo": arq.name,
                "caminho": rel(arq, raiz),
                "conceito": nome,
                "tipo": tipo,
                "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
                "nivel": str(fm.get("nivel") or "").strip().lower(),
                "status": str(fm.get("status") or "").strip().lower(),
                "obra_origem": str(fm.get("obra_origem") or "").strip(),
                "autor_origem": str(fm.get("autor_origem") or "").strip(),
                "fonte_verificada": str(fm.get("fonte_verificada") or "").strip().lower(),
                "tradicao": str(fm.get("tradicao") or "").strip(),
                "nivel_evidencia": str(fm.get("nivel_evidencia") or "").strip().lower() if fm.get("nivel_evidencia") else "",
                "contestado_por": fm.get("contestado_por") if isinstance(fm.get("contestado_por"), list) else ([fm.get("contestado_por")] if fm.get("contestado_por") else []),
                "eixos": fm.get("eixos") if isinstance(fm.get("eixos"), list) else ([fm.get("eixos")] if fm.get("eixos") else []),
                "relacoes": fm.get("relacoes") if isinstance(fm.get("relacoes"), list) else ([fm.get("relacoes")] if fm.get("relacoes") else []),
                "definicao": definicao,
                "tags": parse_tags(fm.get("tags")),
                "secoes_faltando": faltando,
                "tem_trecho": bool(achar_secao(texto, SECAO_TRECHO).strip()),
                "_texto": texto,
            }
        )
    return registros


def coletar_livros(raiz: pathlib.Path, tema_antigo: dict | None = None) -> tuple[list[dict], list[dict]]:
    tema_antigo = tema_antigo or {}
    livros, fichas = [], []
    for arq in listar_md(raiz / "acervo", recursivo=True):
        texto = ler(arq)
        try:
            fm = parse_frontmatter(texto)
        except ErroFrontmatter as exc:
            _registrar_erro_frontmatter(rel(arq, raiz), str(exc))
            continue
        if texto.lstrip().startswith("---") and not fm:
            # arquivo com frontmatter vazio — considerar erro apenas se for ficha
            pass
        tema = str(fm.get("tema") or "").strip().lower()
        if not tema:
            tema = tema_antigo.get(arq.name, "sem-tema")
        registro = {
            "arquivo": arq.name,
            "caminho": rel(arq, raiz),
            "tema": tema or "sem-tema",
            "palavras": len(texto.split()),
        }
        ficha = arq.name.lower().endswith("-ficha.md") or fm.get("tipo") == "ficha-de-leitura"
        if ficha:
            registro.update(
                {
                    "obra": str(fm.get("obra") or "").strip(),
                    "autor": str(fm.get("autor") or "").strip(),
                    "ano": fm.get("ano"),
                    "status": str(fm.get("status") or "").strip().lower(),
                }
            )
            fichas.append(registro)
        else:
            registro["titulo"] = str(fm.get("obra") or arq.stem.replace("-", " "))
            livros.append(registro)
    return livros, fichas


def tema_do_indice_antigo(raiz: pathlib.Path) -> dict:
    caminho = raiz / "indices" / "indice.json"
    if not caminho.exists():
        return {}
    try:
        antigo = json.loads(ler(caminho))
    except Exception:
        return {}
    mapa = {}
    for chave in ("livros", "fichas"):
        for item in antigo.get(chave, []) or []:
            if isinstance(item, dict) and item.get("arquivo"):
                tema = (item.get("tema") or "").strip().lower()
                if tema:
                    mapa[item["arquivo"]] = tema
    return mapa


def coletar_trechos(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "trechos", recursivo=True):
        texto = ler(arq)
        try:
            fm = parse_frontmatter(texto)
        except ErroFrontmatter as exc:
            _registrar_erro_frontmatter(rel(arq, raiz), str(exc))
            continue
        if not texto.lstrip().startswith("---"):
            _registrar_erro_frontmatter(rel(arq, raiz), "Arquivo sem frontmatter (esperado cabeçalho YAML entre '---').")
            continue
        registros.append(
            {
                "arquivo": arq.name,
                "caminho": rel(arq, raiz),
                "titulo": titulo_h1(texto),
                "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
                "obra": str(fm.get("obra") or "").strip(),
                "autor": str(fm.get("autor") or "").strip(),
                "capitulo": str(fm.get("capitulo") or "").strip(),
                "pagina": str(fm.get("pagina") or "").strip(),
            }
        )
    return registros


def progresso_trilha(texto: str) -> dict:
    """Conta nós por checkbox; se não houver, usa os títulos `### Nó ...`."""
    itens = REGEX_CHECKBOX.findall(texto)
    if itens:
        total = len(itens)
        nos = [limpar_markdown(txt).strip() for _, txt in itens]
        feitos = sum(1 for marca, _ in itens if marca.strip().lower() == "x")
        proximo = next(
            (limpar_markdown(txt).strip() for marca, txt in itens if marca.strip() != "x"),
            "",
        )
        formato = "checkbox"
    else:
        secoes_no = REGEX_SECAO_NO.findall(texto)
        nos = [limpar_markdown(txt).strip() for txt in secoes_no]
        total, feitos = len(secoes_no), 0
        proximo = limpar_markdown(secoes_no[0]).strip() if secoes_no else ""
        formato = "secoes"
    return {
        "nos": nos,
        "nos_total": total,
        "nos_concluidos": feitos,
        "formato": formato,
        "proximo_no": proximo,
    }


def coletar_trilhas(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "trilhas", recursivo=True):
        texto = ler(arq)
        try:
            fm = parse_frontmatter(texto)
        except ErroFrontmatter as exc:
            _registrar_erro_frontmatter(rel(arq, raiz), str(exc))
            continue
        if not texto.lstrip().startswith("---"):
            _registrar_erro_frontmatter(rel(arq, raiz), "Arquivo sem frontmatter (esperado cabeçalho YAML entre '---').")
            continue
        registro = {
            "arquivo": arq.name,
            "caminho": rel(arq, raiz),
            "trilha": str(fm.get("trilha") or titulo_h1(texto)).strip(),
            "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
            "nivel": str(fm.get("nivel") or "").strip().lower(),
            "status": str(fm.get("status") or "").strip().lower(),
            "objetivo": extrair_secao(texto, "Objetivo da trilha"),
        }
        registro.update(progresso_trilha(texto))
        registros.append(registro)
    return registros


def coletar_diario(raiz: pathlib.Path) -> list[dict]:
    registros = []
    for arq in listar_md(raiz / "diario", recursivo=True):
        texto = ler(arq)
        try:
            fm = parse_frontmatter(texto)
        except ErroFrontmatter as exc:
            _registrar_erro_frontmatter(rel(arq, raiz), str(exc))
            continue
        if not texto.lstrip().startswith("---"):
            _registrar_erro_frontmatter(rel(arq, raiz), "Arquivo sem frontmatter (esperado cabeçalho YAML entre '---').")
            continue
        data = fm.get("data")
        if isinstance(data, (dt.date, dt.datetime)):
            data = data.isoformat()
        registros.append(
            {
                "arquivo": arq.name,
                "caminho": rel(arq, raiz),
                "data": str(data or "").strip(),
                "tema": str(fm.get("tema") or "sem-tema").strip().lower(),
                "origem": str(fm.get("origem") or "").strip(),
                "titulo": titulo_h1(texto),
            }
        )
    return registros


def montar_indice(raiz: pathlib.Path) -> dict:
    _limpar_erros_frontmatter()
    tema_antigo = tema_do_indice_antigo(raiz)
    livros, fichas = coletar_livros(raiz, tema_antigo)
    conceitos = coletar_conceitos(raiz)
    trechos = coletar_trechos(raiz)
    trilhas = coletar_trilhas(raiz)
    diario = coletar_diario(raiz)

    for registro in conceitos:
        registro["pendencias"] = pendencias_da_nota(registro)
        registro.pop("_texto", None)

    indice = {
        "projeto": "humanitas",
        "descricao": (
            "Mapa geral do painel. Gerado por `python -m scripts.painel indice` "
            "— não edite à mão."
        ),
        "atualizado_em": dt.datetime.now().isoformat(timespec="seconds"),
        "totais": {
            "livros": len(livros),
            "fichas": len(fichas),
            "conceitos": sum(1 for c in conceitos if c["tipo"] == "conceito"),
            "eixos": sum(1 for c in conceitos if c["tipo"] == "eixo"),
            "trechos": len(trechos),
            "trilhas": len(trilhas),
            "diario": len(diario),
        },
        "livros": livros,
        "fichas": fichas,
        "conceitos": conceitos,
        "trechos": trechos,
        "trilhas": trilhas,
        "diario": diario,
    }
    return indice


# ---------------------------------------------------------------------------
# Geração de tabelas e artefatos
# ---------------------------------------------------------------------------


def tabela_temas(indice: dict) -> str:
    """Tabela de temas do README, com a "regra do zero" do Guia 09.

    Tema sem nenhum conteúdo (nota, livro, ficha ou trilha) não ocupa linha na
    vitrine: ele aparece no rodapé como planejado. Assim a tabela é um retrato
    honesto do que está sendo estudado, e não uma lista de promessas.
    """
    conceitos = Counter(c.get("tema", "sem-tema") for c in indice["conceitos"])
    livros = Counter(l.get("tema", "sem-tema") for l in indice["livros"])
    fichas = Counter(f.get("tema", "sem-tema") for f in indice["fichas"])
    trilhas = Counter(t.get("tema", "sem-tema") for t in indice.get("trilhas", []))

    temas = dict(TEMAS)
    for chave in sorted(set(conceitos) | set(livros) | set(fichas) | set(trilhas)):
        temas.setdefault(chave, chave.replace("-", " ").title())

    linhas = [
        "| Tema | Status | Notas de conceito | Livros processados | Fichas | Trilhas |",
        "|---|---|---|---|---|---|",
    ]
    planejados: list[str] = []
    for chave, nome in temas.items():
        nc, nl, nf = conceitos.get(chave, 0), livros.get(chave, 0), fichas.get(chave, 0)
        nt = trilhas.get(chave, 0)
        if (nc + nl + nf + nt) == 0:
            planejados.append(nome)
            continue
        linhas.append(f"| {nome} | Ativo | {nc} | {nl} | {nf} | {nt} |")

    if planejados:
        linhas.append("")
        linhas.append(
            "> **Planejados (sem conteúdo ainda):** "
            + ", ".join(planejados)
            + ". Critério de entrada e ordem de estudo no Guia 09 "
            "(`docs/09-mapa-das-humanidades.md`)."
        )
    return "\n".join(linhas)


def substituir_bloco(texto: str, marcadores: tuple[str, str], bloco: str) -> str:
    inicio, fim = marcadores
    if inicio not in texto or fim not in texto:
        return texto
    pre = texto.split(inicio)[0]
    pos = texto.split(fim, 1)[1]
    return f"{pre}{inicio}\n\n{bloco}\n\n{fim}{pos}"


def gravar_indice(raiz: pathlib.Path, indice: dict) -> pathlib.Path:
    """Grava o índice; se nada além do timestamp mudou, mantém o arquivo intacto.

    Isso é o que permite ao CI rodar `indice` e conferir com `git diff --exit-code`
    sem falhar só porque o relógio andou.
    """
    caminho = raiz / "indices" / "indice.json"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    comparavel = {k: v for k, v in indice.items() if k != "atualizado_em"}
    if caminho.exists():
        try:
            anterior = json.loads(ler(caminho))
            anterior_comparavel = {k: v for k, v in anterior.items() if k != "atualizado_em"}
            if anterior_comparavel == comparavel:
                return caminho
        except Exception:
            pass
    caminho.write_text(
        json.dumps(indice, ensure_ascii=False, indent=2, default=str) + "\n",
        encoding="utf-8",
    )
    return caminho


def atualizar_readme_temas(raiz: pathlib.Path, tabela: str) -> bool:
    readme = raiz / "README.md"
    if not readme.exists():
        return False
    texto = ler(readme)
    novo = substituir_bloco(texto, MARCADOR_TEMAS, tabela)
    if novo == texto:
        return False
    readme.write_text(novo, encoding="utf-8")
    return True


