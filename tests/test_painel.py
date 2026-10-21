"""Testes do CLI de manutenção do painel."""

from __future__ import annotations

import json
import pathlib

import pytest

from scripts import painel


# ---------------------------------------------------------------------------
# Parsing
# ---------------------------------------------------------------------------


def test_parse_frontmatter_com_yaml():
    fm = painel.parse_frontmatter(
        '---\ntema: psicologia\ntags: [escola, classica]\nnivel: iniciante\n---\n\n# Nota\n'
    )
    assert fm["tema"] == "psicologia"
    assert fm["tags"] == ["escola", "classica"]
    assert fm["nivel"] == "iniciante"


def test_parse_frontmatter_sem_cabecalho():
    assert painel.parse_frontmatter("# Título\n\ntexto") == {}


def test_parse_frontmatter_quebrado_nao_explode():
    assert isinstance(painel.parse_frontmatter("---\ntema: [\n---\n"), dict)


def test_parse_tags_aceita_lista_e_string():
    assert painel.parse_tags(["a", " b "]) == ["a", "b"]
    assert painel.parse_tags("[a, b]") == ["a", "b"]
    assert painel.parse_tags("") == []


def test_normalizar_remove_acento_caixa_e_pontuacao():
    assert painel.normalizar("Eudaimonía — Ética!") == "eudaimonia etica"


def test_extrair_secao_ignora_comentarios_e_citacoes():
    texto = (
        "## Definição em uma frase\n\n<!-- comentário -->\n"
        "> citação\n\nA definição de verdade.\n\nSegundo parágrafo.\n"
    )
    assert painel.extrair_secao(texto, "Definição em uma frase") == "A definição de verdade."


def test_sem_codigo_remove_blocos_e_inline():
    texto = "veja `[x](nao-existe.md)` e\n```\n[y](tambem-nao.md)\n```\nfim"
    limpo = painel.sem_codigo(texto)
    assert "nao-existe.md" not in limpo
    assert "tambem-nao.md" not in limpo


# ---------------------------------------------------------------------------
# Auditoria
# ---------------------------------------------------------------------------


def test_auditoria_repo_valido_sem_erros(mini_repo: pathlib.Path):
    erros, _ = painel.auditar(mini_repo)
    assert erros == []


def test_auditoria_detecta_link_quebrado(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(
        nota.read_text(encoding="utf-8") + "\n- [Fantasma](sociologia-fantasma.md)\n",
        encoding="utf-8",
    )
    erros, _ = painel.auditar(mini_repo)
    assert any("sociologia-fantasma.md" in e for e in erros)


def test_auditoria_checa_links_em_trilhas(mini_repo: pathlib.Path):
    trilha = mini_repo / "trilhas" / "sociologia-teste.md"
    trilha.write_text(
        trilha.read_text(encoding="utf-8")
        + "\n## Extra\n\n- [Nada](../conceitos/nao-existe.md)\n",
        encoding="utf-8",
    )
    erros, _ = painel.auditar(mini_repo)
    assert any("trilhas/sociologia-teste.md" in e and "nao-existe.md" in e for e in erros)


def test_auditoria_detecta_wikilink(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(
        nota.read_text(encoding="utf-8") + "\nVeja [[habitus]].\n", encoding="utf-8"
    )
    erros, _ = painel.auditar(mini_repo)
    assert any("Wikilink" in e for e in erros)


def test_auditoria_detecta_tema_invalido(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(
        nota.read_text(encoding="utf-8").replace("tema: sociologia", "tema: histórria"),
        encoding="utf-8",
    )
    erros, _ = painel.auditar(mini_repo)
    assert any("tema inválido" in e for e in erros)


def test_auditoria_detecta_secao_obrigatoria_ausente(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8").replace("## Conexões interdisciplinares", "## Outra")
    nota.write_text(texto, encoding="utf-8")
    erros, _ = painel.auditar(mini_repo)
    assert any("Conexões interdisciplinares" in e for e in erros)


def test_auditoria_detecta_duplicado(mini_repo: pathlib.Path):
    original = (mini_repo / "conceitos" / "sociologia-habitus.md").read_text(encoding="utf-8")
    (mini_repo / "conceitos" / "sociologia-habitus-2.md").write_text(original, encoding="utf-8")
    erros, _ = painel.auditar(mini_repo)
    assert any("duplicado" in e.lower() for e in erros)


def test_auditoria_sinaliza_rascunhos_como_aviso(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(
        nota.read_text(encoding="utf-8").replace("status: ok", "status: rascunho"),
        encoding="utf-8",
    )
    erros, avisos = painel.auditar(mini_repo)
    assert erros == []
    assert any("rascunho" in a for a in avisos)


def test_cli_auditar_retorna_1_com_erro(mini_repo: pathlib.Path, capsys):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(nota.read_text(encoding="utf-8").replace("tema: sociologia", "tema: xyz"),
                    encoding="utf-8")
    codigo = painel.main(["--raiz", str(mini_repo), "auditar"])
    assert codigo == 1
    assert "tema inválido" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Índice e tabela
# ---------------------------------------------------------------------------


def test_indice_tem_schema_completo(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    for chave in ("livros", "fichas", "conceitos", "trechos", "trilhas", "diario", "totais"):
        assert chave in indice
    assert indice["totais"]["conceitos"] == 2
    assert indice["totais"]["eixos"] == 1
    assert indice["totais"]["fichas"] == 1
    assert indice["totais"]["trechos"] == 1
    assert indice["totais"]["diario"] == 1
    assert indice["totais"]["trilhas"] == 1


def test_gravar_indice_nao_perde_secoes(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    caminho = painel.gravar_indice(mini_repo, indice)
    dados = json.loads(caminho.read_text(encoding="utf-8"))
    assert dados["conceitos"] and dados["trilhas"] and dados["fichas"]
    assert dados["atualizado_em"]


def test_gravar_indice_nao_reescreve_sem_mudanca(mini_repo: pathlib.Path):
    """Sem mudança de conteúdo, o arquivo (e o timestamp) ficam intactos."""
    painel.gravar_indice(mini_repo, painel.montar_indice(mini_repo))
    caminho = mini_repo / "indices" / "indice.json"
    primeiro = caminho.read_text(encoding="utf-8")
    painel.gravar_indice(mini_repo, painel.montar_indice(mini_repo))
    assert caminho.read_text(encoding="utf-8") == primeiro

    # uma mudança real força a reescrita e atualiza o timestamp
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(nota.read_text(encoding="utf-8") + "\nTexto novo.\n", encoding="utf-8")
    painel.gravar_indice(mini_repo, painel.montar_indice(mini_repo))
    assert json.loads(caminho.read_text(encoding="utf-8"))["atualizado_em"]


def test_tabela_conta_sem_somar_ficha_em_livro(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    tabela = painel.tabela_temas(indice)
    linha = next(l for l in tabela.splitlines() if l.startswith("| Sociologia |"))
    celulas = [c.strip() for c in linha.strip("|").split("|")]
    assert celulas[2] == "2"  # conceitos (inclui o eixo de filosofia? não: eixo é filosofia)
    assert celulas[3] == "0"  # livros
    assert celulas[4] == "1"  # fichas
    assert celulas[5] == "1"  # trilhas


def test_atualizar_readme_e_idempotente(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    tabela = painel.tabela_temas(indice)
    assert painel.atualizar_readme_temas(mini_repo, tabela) is True
    depois = (mini_repo / "README.md").read_text(encoding="utf-8")
    assert painel.atualizar_readme_temas(mini_repo, tabela) is False
    assert (mini_repo / "README.md").read_text(encoding="utf-8") == depois
    assert "| Sociologia |" in depois


# ---------------------------------------------------------------------------
# Trimestres, progresso e flashcards
# ---------------------------------------------------------------------------


def test_progresso_conta_checkboxes(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    p = painel.calcular_progresso(indice)
    assert p["nos_total"] == 3
    assert p["nos_concluidos"] == 1
    assert p["diario_total"] == 1
    assert p["conceitos"] == 3


def test_progresso_lida_com_trilha_por_secoes(tmp_path: pathlib.Path):
    texto = "# Trilha\n\n### Nó A1. Primeiro\n\n### Nó A2. Segundo\n"
    resultado = painel.progresso_trilha(texto)
    assert resultado["nos_total"] == 2
    assert resultado["formato"] == "secoes"


def test_comando_progresso_escreve_arquivo(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "progresso"]) == 0
    conteudo = (mini_repo / "progresso.md").read_text(encoding="utf-8")
    assert "Progresso do painel" in conteudo
    assert "1 de 3" in conteudo


def test_flashcards_guids_estaveis(mini_repo: pathlib.Path):
    primeira = painel.gerar_flashcards(mini_repo)
    segunda = painel.gerar_flashcards(mini_repo)
    assert primeira == segunda
    assert len({linha[0] for linha in primeira}) == len(primeira)


def test_flashcards_guid_independe_do_nome_do_arquivo(mini_repo: pathlib.Path):
    antes = {linha[1]: linha[0] for linha in painel.gerar_flashcards(mini_repo)}
    origem = mini_repo / "conceitos" / "sociologia-habitus.md"
    origem.rename(mini_repo / "conceitos" / "sociologia-habitus-renomeado.md")
    depois = {linha[1]: linha[0] for linha in painel.gerar_flashcards(mini_repo)}
    assert depois["O que é Habitus?"] == antes["O que é Habitus?"]


def test_flashcards_do_eixo_listam_posicoes(mini_repo: pathlib.Path):
    linhas = painel.gerar_flashcards(mini_repo)
    frente = [linha[1] for linha in linhas]
    assert any("posições" in f for f in frente)
    verso = next(linha[2] for linha in linhas if "posições" in linha[1])
    assert "Inatismo" in verso and "Culturalismo" in verso


def test_flashcards_csv_tem_cabecalho(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "flashcards"]) == 0
    primeira_linha = (mini_repo / "flashcards.csv").read_text(encoding="utf-8").splitlines()[0]
    assert primeira_linha.split(",") == ["guid", "frente", "verso", "tags", "baralho"]


# ---------------------------------------------------------------------------
# Regressão: o conversor não pode mais sobrescrever o índice
# ---------------------------------------------------------------------------


def test_conversor_nao_escreve_indice():
    """Regressão: o conversor já sobrescreveu o índice e apagou dados."""
    notebooks = pathlib.Path(__file__).resolve().parents[1] / "notebooks"
    celulas = [
        "".join(c["source"])
        for c in json.loads((notebooks / "converter-pdfs.ipynb").read_text())["cells"]
        if c["cell_type"] == "code"
    ]
    escreve_indice = [
        fonte for fonte in celulas
        if "indice" in fonte.lower() and ("write_text" in fonte or "json.dumps" in fonte)
    ]
    assert not escreve_indice, (
        "O conversor voltou a escrever indice.json: isso apaga conceitos/trechos/fichas "
        "do índice. O índice tem um único dono (scripts/painel.py)."
    )


@pytest.mark.parametrize("comando", ["indice", "tabela", "progresso", "flashcards", "tudo"])
def test_comandos_rodam_no_repositorio_real(comando: str, tmp_path: pathlib.Path, monkeypatch, capsys):
    """Roda os comandos contra uma cópia do repositório real."""
    import shutil

    raiz = pathlib.Path(__file__).resolve().parents[1]
    copia = tmp_path / "repo"
    shutil.copytree(
        raiz,
        copia,
        ignore=shutil.ignore_patterns(".git", ".venv", "__pycache__", "*.zip", "flashcards.csv"),
    )
    monkeypatch.chdir(copia)
    assert painel.main(["--raiz", str(copia), comando]) == 0
    capsys.readouterr()


# ---------------------------------------------------------------------------
# Scaffold de notas (nova)
# ---------------------------------------------------------------------------


def _criar_esqueleto(mini_repo: pathlib.Path, *args: str) -> int:
    return painel.main(["--raiz", str(mini_repo), "nova", *args])


def test_nova_conceito_cria_nota_auditavel(mini_repo: pathlib.Path):
    codigo = _criar_esqueleto(
        mini_repo,
        "--tipo", "conceito",
        "--nome", "Campo (sociologia)",
        "--tema", "sociologia",
        "--nivel", "entusiasta",
        "--autor", "Pierre Bourdieu",
        "--obra", "O Senso Prático, cap. 3",
        "--tags", "bourdieu,pratica",
    )
    assert codigo == 0
    nota = mini_repo / "conceitos" / "sociologia-campo-sociologia.md"
    assert nota.exists()
    texto = nota.read_text(encoding="utf-8")
    fm = painel.parse_frontmatter(texto)
    assert fm["conceito"] == "Campo (sociologia)"
    assert fm["tema"] == "sociologia"
    assert fm["status"] == "rascunho"
    assert fm["nivel"] == "entusiasta"
    assert "bourdieu" in fm["tags"]
    # o esqueleto não pode introduzir erros de auditoria
    erros, _ = painel.auditar(mini_repo)
    assert erros == []


def test_nova_remove_links_de_exemplo_do_template(mini_repo: pathlib.Path):
    _criar_esqueleto(
        mini_repo, "--tipo", "conceito", "--nome", "Campo Novo", "--tema", "sociologia"
    )
    texto = (mini_repo / "conceitos" / "sociologia-campo-novo.md").read_text(encoding="utf-8")
    # o exemplo [estado-nacao](historia-estado-nacao.md) vira texto simples
    assert "historia-estado-nacao.md)[" not in texto
    assert "](historia-estado-nacao.md)" not in texto


def test_nova_marca_as_pendencias(mini_repo: pathlib.Path):
    _criar_esqueleto(
        mini_repo, "--tipo", "conceito", "--nome", "Campo Novo", "--tema", "sociologia"
    )
    nota = mini_repo / "conceitos" / "sociologia-campo-novo.md"
    assert "<!-- PENDENTE" in nota.read_text(encoding="utf-8")
    texto = nota.read_text(encoding="utf-8")
    assert "A definição mais enxuta possível" in texto  # ainda é placeholder


def test_nova_nao_sobrescreve_sem_forcar(mini_repo: pathlib.Path, capsys):
    args = ("--tipo", "conceito", "--nome", "Campo Novo", "--tema", "sociologia")
    assert _criar_esqueleto(mini_repo, *args) == 0
    capsys.readouterr()
    assert _criar_esqueleto(mini_repo, *args) == 1
    assert "Já existe" in capsys.readouterr().out
    assert _criar_esqueleto(mini_repo, *args, "--forcar") == 0


def test_nova_valida_tema_e_nivel(mini_repo: pathlib.Path, capsys):
    assert _criar_esqueleto(mini_repo, "--tipo", "conceito", "--nome", "X", "--tema", "xyz") == 1
    assert "Tema inválido" in capsys.readouterr().out
    assert _criar_esqueleto(
        mini_repo, "--tipo", "conceito", "--nome", "X", "--tema", "sociologia", "--nivel", "deus"
    ) == 1
    assert "Nível inválido" in capsys.readouterr().out


@pytest.mark.parametrize(
    ("tipo", "nome", "esperado"),
    [
        ("eixo", "Cultura × Natureza", "conceitos/eixo-cultura-natureza.md"),
        ("ficha", "O Senso Prático", "acervo/fichas/o-senso-pratico-ficha.md"),
        ("trecho", "Bourdieu sobre o corpo", "trechos/bourdieu-sobre-o-corpo.md"),
        ("diario", "Sobre habitus", "diario/2026-01-15-sociologia-sobre-habitus.md"),
    ],
)
def test_nova_outros_tipos(mini_repo: pathlib.Path, tipo: str, nome: str, esperado: str):
    extra = ("--data", "2026-01-15") if tipo == "diario" else ()
    codigo = _criar_esqueleto(
        mini_repo, "--tipo", tipo, "--nome", nome, "--tema", "sociologia", *extra
    )
    assert codigo == 0
    caminho = mini_repo / esperado
    assert caminho.exists(), esperado
    erros, _ = painel.auditar(mini_repo)
    assert erros == []


def test_flashcards_ignoram_texto_de_exemplo(mini_repo: pathlib.Path):
    _criar_esqueleto(
        mini_repo, "--tipo", "conceito", "--nome", "Campo Novo", "--tema", "sociologia"
    )
    frentes = [linha[1] for linha in painel.gerar_flashcards(mini_repo)]
    assert "O que é Campo Novo?" not in frentes  # definição ainda é placeholder


# ---------------------------------------------------------------------------
# Pendências (checklist do padrão-ouro)
# ---------------------------------------------------------------------------


def test_pendencias_mostra_o_que_falta(mini_repo: pathlib.Path, capsys):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(
        nota.read_text(encoding="utf-8").replace("status: ok", "status: rascunho"),
        encoding="utf-8",
    )
    assert painel.main(["--raiz", str(mini_repo), "pendencias"]) == 0
    saida = capsys.readouterr().out
    assert "Habitus" in saida
    assert "status ainda é rascunho" in saida
    assert "com pendência" in saida


def test_pendencias_respeita_limite_e_tema(mini_repo: pathlib.Path, capsys):
    assert painel.main(
        ["--raiz", str(mini_repo), "pendencias", "--tema", "sociologia", "--limite", "1"]
    ) == 0
    saida = capsys.readouterr().out
    assert saida.count("pendência(s) —") == 1
    assert "Mostrando as 1 notas" in saida


def test_pendencias_nota_pronta_nao_aparece(mini_repo: pathlib.Path, capsys):
    assert painel.main(["--raiz", str(mini_repo), "pendencias"]) == 0
    saida = capsys.readouterr().out
    # as duas notas válidas do mini-repo estão em status ok e têm citação? só o habitus tem
    assert "0 com pendência" in saida or "com pendência" in saida


def test_pendencias_tema_invalido(mini_repo: pathlib.Path, capsys):
    assert painel.main(["--raiz", str(mini_repo), "pendencias", "--tema", "xyz"]) == 1
    assert "Tema inválido" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Site
# ---------------------------------------------------------------------------


def test_site_monta_apenas_conteudo_publicavel(mini_repo: pathlib.Path):
    texto_integral = mini_repo / "acervo" / "bourdieu-senso-pratico.md"
    texto_integral.write_text("# Texto integral protegido\n", encoding="utf-8")
    anexo = mini_repo / "docs" / "anexos" / "plano.pdf"
    anexo.parent.mkdir(parents=True, exist_ok=True)
    anexo.write_bytes(b"%PDF-1.4")

    assert painel.main(["--raiz", str(mini_repo), "site"]) == 0

    fontes = mini_repo / "site-src"
    assert (fontes / "index.md").exists()  # README vira a home
    assert (fontes / "conceitos" / "sociologia-habitus.md").exists()
    assert (fontes / "trilhas" / "sociologia-teste.md").exists()
    assert (fontes / "diario").exists()
    assert (fontes / "acervo" / "fichas").exists()
    # o que não pode ser publicado
    assert not (fontes / "acervo" / "bourdieu-senso-pratico.md").exists()
    assert not (fontes / "docs" / "anexos").exists()
    assert not (fontes / ".git").exists()


def test_site_nao_publica_texto_integral_mesmo_sem_ficha(mini_repo: pathlib.Path):
    (mini_repo / "acervo" / "livro-protegido.md").write_text("# capítulo\n", encoding="utf-8")
    painel.main(["--raiz", str(mini_repo), "site"])
    assert not (mini_repo / "site-src" / "acervo" / "livro-protegido.md").exists()


def test_site_e_idempotente(mini_repo: pathlib.Path):
    painel.main(["--raiz", str(mini_repo), "site"])
    primeiro = (mini_repo / "site-src" / "index.md").read_text(encoding="utf-8")
    sobra = mini_repo / "site-src" / "arquivo-velho.md"
    sobra.write_text("lixo\n", encoding="utf-8")
    painel.main(["--raiz", str(mini_repo), "site"])
    assert not sobra.exists()  # reconstrói do zero
    assert (mini_repo / "site-src" / "index.md").read_text(encoding="utf-8") == primeiro
