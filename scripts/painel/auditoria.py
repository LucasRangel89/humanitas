from __future__ import annotations

import difflib
import pathlib
import re

from .modelo import TEMAS, NIVEIS_EVIDENCIA_VALIDOS, TIPOS_VALIDOS, STATUS_VALIDOS, NIVEIS_VALIDOS, SECOES_OBRIGATORIAS, SECAO_TRECHO, REGEX_LINK, REGEX_WIKILINK, _ERROS_FRONTMATTER, _limpar_erros_frontmatter, _registrar_erro_frontmatter, ler, normalizar, listar_md, rel, achar_secao, secoes, sem_codigo, extrair_secao, parse_tags
from .indice import coletar_conceitos, coletar_trilhas, coletar_diario, coletar_trechos, coletar_livros, tema_do_indice_antigo, coletar_conceitos
from .midias import verificar as _verificar_midias

# ---------------------------------------------------------------------------
# Auditoria
# ---------------------------------------------------------------------------


def _links_quebrados(raiz: pathlib.Path, arquivos: list[pathlib.Path]) -> list[str]:
    problemas = []
    for arq in arquivos:
        texto = sem_codigo(ler(arq))
        for alvo in REGEX_LINK.findall(texto):
            if alvo.startswith(("http://", "https://", "mailto:", "#")):
                continue
            caminho = alvo.split("#")[0].strip()
            if not caminho or not caminho.lower().endswith(".md"):
                continue
            if (arq.parent / caminho).exists() or (raiz / caminho).exists():
                continue
            problemas.append(
                f"Link quebrado em {rel(arq, raiz)}: ({alvo})"
            )
    return problemas


def _wikilinks(raiz: pathlib.Path, arquivos: list[pathlib.Path]) -> list[str]:
    problemas = []
    for arq in arquivos:
        for achado in REGEX_WIKILINK.findall(sem_codigo(ler(arq))):
            problemas.append(
                f"Wikilink (não vira link no GitHub) em {rel(arq, raiz)}: {achado}"
            )
    return problemas


def _validar_metadados(conceitos: list[dict], trilhas: list[dict], diario: list[dict], trechos: list[dict]) -> list[str]:
    erros = []
    for c in conceitos:
        onde = f"conceitos/{c['arquivo']}"
        if c["tema"] == "sem-tema" or c["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({c['tema']!r})")
        if c["tipo"] not in TIPOS_VALIDOS:
            erros.append(f"{onde}: tipo inválido ({c['tipo']!r})")
        if c["status"] and c["status"] not in STATUS_VALIDOS:
            erros.append(f"{onde}: status inválido ({c['status']!r})")
        if not c["status"]:
            erros.append(f"{onde}: campo obrigatório ausente: status")
        if c["nivel"] and c["nivel"] not in NIVEIS_VALIDOS:
            erros.append(f"{onde}: nivel inválido ({c['nivel']!r})")
        if not c["nivel"]:
            erros.append(f"{onde}: campo obrigatório ausente: nivel")
        if not c["conceito"]:
            erros.append(f"{onde}: nome do conceito ausente (frontmatter ou título)")
        if not c["definicao"]:
            erros.append(f"{onde}: sem definição em uma frase (flashcard ficaria vazio)")
        for secao in c["secoes_faltando"]:
            erros.append(f"{onde}: seção obrigatória ausente ou vazia: '{secao}'")
        # fonte_verificada obrigatório em conceito e eixo
        fv = c.get("fonte_verificada", "")
        if fv not in ("sim", "nao"):
            erros.append(f"{onde}: campo obrigatório ausente ou inválido: fonte_verificada (use 'sim' ou 'nao')")
        # PR3: campos enriquecidos opcionais
        if c.get("tradicao") is not None and c.get("tradicao") != "":
            if not str(c["tradicao"]).strip():
                erros.append(f"{onde}: `tradicao` não pode ser vazia.")
        if c.get("nivel_evidencia"):
            ne = str(c["nivel_evidencia"]).strip().lower()
            if ne not in NIVEIS_EVIDENCIA_VALIDOS:
                erros.append(f"{onde}: `nivel_evidencia` deve ser um de alta|media|baixa|teorica|empirica|forte|moderada|fraca (tem `{ne}`).")
        if c.get("contestado_por") is not None and c.get("contestado_por") != "":
            cp = c["contestado_por"]
            if isinstance(cp, str):
                # se veio como string do frontmatter, tenta parse_tags-like
                cp = [cp]
            if not isinstance(cp, list) or not all(isinstance(x, str) and x.strip() for x in cp):
                erros.append(f"{onde}: `contestado_por` deve ser lista de strings.")
        if c.get("eixos") is not None and c.get("eixos") != "":
            ex = c["eixos"]
            if isinstance(ex, str):
                ex = [ex]
            if not isinstance(ex, list) or not all(isinstance(x, str) and x.strip() for x in ex):
                erros.append(f"{onde}: `eixos` deve ser lista de strings.")
        if c.get("relacoes") is not None and c.get("relacoes") != "":
            rels = c["relacoes"]
            if isinstance(rels, str):
                rels = [rels]
            if not isinstance(rels, list):
                erros.append(f"{onde}: `relacoes` deve ser lista.")
            else:
                for item in rels:
                    if isinstance(item, dict):
                        if "alvo" not in item or not str(item["alvo"]).strip():
                            erros.append(f"{onde}: cada `relacoes` precisa ter `alvo`.")
                    elif not isinstance(item, str) or not item.strip():
                        erros.append(f"{onde}: `relacoes` deve ser lista de strings ou objetos com `alvo`.")

        # regras para notas ok (apenas conceitos exigem citação com capítulo/página)
        if c["status"] == "ok":
            if c.get("tipo") == "conceito":
                trecho = achar_secao(c.get("_texto", ""), SECAO_TRECHO)
                tem_frase_secundaria = "sem citação" in trecho.lower() and "fonte secundária" in trecho.lower()
                tem_cap_pag = bool(re.search(r"(cap\.|capítulo|capitulo|p\.|página|pagina)\s*\d+", trecho, re.I))
                if not trecho.strip():
                    erros.append(f"{onde}: nota com status ok exige seção '{SECAO_TRECHO}' preenchida")
                elif not (tem_frase_secundaria or tem_cap_pag):
                    erros.append(
                        f"{onde}: nota com status ok exige citação com capítulo/página em '{SECAO_TRECHO}' ou a frase 'Sem citação — fonte secundária'"
                    )
            if not fv:
                erros.append(f"{onde}: nota com status ok exige campo fonte_verificada")
    for t in trilhas:
        onde = f"trilhas/{t['arquivo']}"
        if t["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({t['tema']!r})")
        if t["status"] and t["status"] not in STATUS_VALIDOS:
            erros.append(f"{onde}: status inválido ({t['status']!r})")
        if not t["status"]:
            erros.append(f"{onde}: campo obrigatório ausente: status")
    for d in diario:
        onde = f"diario/{d['arquivo']}"
        if not d["data"]:
            erros.append(f"{onde}: campo obrigatório ausente: data")
        if d["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({d['tema']!r})")
    for t in trechos:
        onde = f"trechos/{t['arquivo']}"
        if not t["obra"]:
            erros.append(f"{onde}: campo obrigatório ausente: obra")
        if t["tema"] not in TEMAS:
            erros.append(f"{onde}: tema inválido ou ausente ({t['tema']!r})")
    return erros


def _duplicados(conceitos: list[dict]) -> tuple[list[str], list[str]]:
    erros, avisos = [], []
    nomes = [(c["arquivo"], normalizar(c["conceito"])) for c in conceitos]
    for i in range(len(nomes)):
        arq_a, nome_a = nomes[i]
        if not nome_a:
            continue
        for j in range(i + 1, len(nomes)):
            arq_b, nome_b = nomes[j]
            if not nome_b:
                continue
            if nome_a == nome_b:
                erros.append(
                    f"Conceito duplicado: conceitos/{arq_a} e conceitos/{arq_b} "
                    f"(\"{conceitos[i]['conceito']}\") — junte as duas notas."
                )
            elif difflib.SequenceMatcher(None, nome_a, nome_b).ratio() >= 0.9:
                avisos.append(
                    f"Conceitos parecidos: \"{conceitos[i]['conceito']}\" ({arq_a}) e "
                    f"\"{conceitos[j]['conceito']}\" ({arq_b}) — são o mesmo conceito?"
                )
    return erros, avisos


def auditar(raiz: pathlib.Path) -> tuple[list[str], list[str]]:
    """Devolve (erros, avisos). Erros bloqueiam o CI."""
    _limpar_erros_frontmatter()
    erros, avisos = [], []

    pastas = ["conceitos", "trechos", "trilhas", "diario", "acervo", "docs"]
    arquivos = []
    for nome in pastas:
        arquivos.extend(listar_md(raiz / nome, recursivo=(nome == "acervo")))
    if (raiz / "README.md").exists():
        arquivos.append(raiz / "README.md")

    erros.extend(_links_quebrados(raiz, arquivos))
    erros.extend(_wikilinks(raiz, arquivos))

    # biblioteca de mídias (videoaulas, artigos, filmes): verificação obrigatória
    erros_midias, avisos_midias = _verificar_midias(raiz)
    erros.extend(erros_midias)
    avisos.extend(avisos_midias)

    conceitos = coletar_conceitos(raiz)
    trilhas = coletar_trilhas(raiz)
    diario = coletar_diario(raiz)
    trechos = coletar_trechos(raiz)

    # erros de frontmatter capturados durante a coleta
    erros.extend(list(_ERROS_FRONTMATTER))

    erros.extend(_validar_metadados(conceitos, trilhas, diario, trechos))
    duplicados_erros, duplicados_avisos = _duplicados(conceitos)
    erros.extend(duplicados_erros)
    avisos.extend(duplicados_avisos)

    # notas não citadas em nenhuma trilha
    texto_trilhas = "\n".join(ler(p) for p in listar_md(raiz / "trilhas"))
    orfas = [c["arquivo"] for c in conceitos if c["arquivo"] not in texto_trilhas]
    if orfas:
        avisos.append(
            "Notas não citadas em nenhuma trilha (podem ser exploração livre): "
            + ", ".join(orfas)
        )

    # notas sem citação de apoio (informativo, não bloqueia)
    sem_trecho = [c["arquivo"] for c in conceitos if not c["tem_trecho"]]
    if sem_trecho:
        avisos.append(
            f"{len(sem_trecho)} nota(s) sem seção '{SECAO_TRECHO}' preenchida "
            "(o padrão-ouro pede citação com capítulo/página)."
        )

    # fontes secundárias declaradas
    secundarias = [
        c["arquivo"]
        for c in conceitos
        if re.search(r"guia de estudos|planos de estudo|anexo|wikip", c["obra_origem"], re.I)
    ]
    if secundarias:
        avisos.append(
            f"{len(secundarias)} nota(s) declaram fonte secundária (guia/planos) — "
            "priorize substituir por obra primária ao reescrever."
        )

    # aviso: nota ok com fonte_verificada nao e fonte secundária
    ok_nao_secundaria = [
        c["arquivo"]
        for c in conceitos
        if c.get("status") == "ok"
        and c.get("fonte_verificada") == "nao"
        and re.search(r"guia de estudos|planos de estudo|anexo|wikip", c.get("obra_origem", ""), re.I)
    ]
    if ok_nao_secundaria:
        avisos.append(
            f"{len(ok_nao_secundaria)} nota(s) com status ok ainda com fonte_verificada: nao e fonte secundária — "
            "verifique a obra primária e atualize para 'sim'."
        )

    # texto integral versionado (risco de direitos autorais)
    livros = [p for p in listar_md(raiz / "acervo", recursivo=True)]
    if livros:
        avisos.append(
            f"{len(livros)} arquivo(s) em acervo/ — confirme que o repositório é "
            "privado ou que o texto integral está fora do Git (.gitignore)."
        )

    # rascunhos
    rascunhos = sum(1 for c in conceitos if c["status"] == "rascunho")
    if rascunhos:
        avisos.append(f"{rascunhos} nota(s) ainda em `status: rascunho` para reescrever.")

    return erros, avisos


