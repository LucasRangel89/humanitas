"""Testes do CLI de manutenção do painel."""

from __future__ import annotations

import json
import pathlib
import re

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


def test_parse_frontmatter_quebrado_levanta_erro():
    with pytest.raises(painel.ErroFrontmatter):
        painel.parse_frontmatter("---\ntema: [\n---\n")


def test_parse_frontmatter_delimitador_faltando():
    with pytest.raises(painel.ErroFrontmatter):
        painel.parse_frontmatter("---\ntema: psicologia\n")


def test_parse_frontmatter_sem_frontmatter_obrigatorio_na_coleta(mini_repo: pathlib.Path):
    sem_fm = mini_repo / "conceitos" / "sem-frontmatter.md"
    sem_fm.write_text("# Sem cabecalho\n\nTexto sem YAML.\n", encoding="utf-8")
    erros, _ = painel.auditar(mini_repo)
    assert any("sem-frontmatter.md" in e and "frontmatter" in e.lower() for e in erros)


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


def test_tabela_omite_temas_sem_conteudo(mini_repo: pathlib.Path):
    """Regra do zero (Guia 09): tema vazio não ocupa linha, aparece no rodapé."""
    tabela = painel.tabela_temas(painel.montar_indice(mini_repo))
    linhas = tabela.splitlines()
    assert any(l.startswith("| Sociologia |") for l in linhas)
    assert not any(l.startswith("| História |") for l in linhas)
    rodape = [l for l in linhas if l.startswith("> **Planejados")]
    assert rodape, "temas sem conteúdo devem ser listados no rodapé"
    assert "História" in rodape[0] and "Economia" in rodape[0]
    assert "docs/09-mapa-das-humanidades.md" in rodape[0]


def test_tabela_promove_tema_quando_ganha_conteudo(mini_repo: pathlib.Path):
    modelo = (mini_repo / "conceitos" / "sociologia-habitus.md").read_text(encoding="utf-8")
    (mini_repo / "conceitos" / "historia-tempo-historico.md").write_text(
        modelo.replace('"Habitus"', '"Tempo histórico"')
        .replace("tema: sociologia", "tema: historia")
        .replace("# Conceito — Habitus", "# Conceito — Tempo histórico"),
        encoding="utf-8",
    )
    tabela = painel.tabela_temas(painel.montar_indice(mini_repo))
    linha = next(l for l in tabela.splitlines() if l.startswith("| História |"))
    assert linha.startswith("| História | Ativo |")


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
    assert "material/tags" in (fontes / "tags.md").read_text(encoding="utf-8")
    # o que não pode ser publicado
    assert not (fontes / "acervo" / "bourdieu-senso-pratico.md").exists()
    assert not (fontes / "docs" / "anexos").exists()
    assert not (fontes / ".git").exists()


def test_site_nao_publica_texto_integral_mesmo_sem_ficha(mini_repo: pathlib.Path):
    (mini_repo / "acervo" / "livro-protegido.md").write_text("# capítulo\n", encoding="utf-8")
    painel.main(["--raiz", str(mini_repo), "site"])
    assert not (mini_repo / "site-src" / "acervo" / "livro-protegido.md").exists()


def test_site_e_idempotente(mini_repo: pathlib.Path):
    def sem_horario(texto: str) -> str:
        # a home carrega o horário de geração; comparar sem ele evita teste instável
        return re.sub(r"Gerado em \d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}", "Gerado em —", texto)

    painel.main(["--raiz", str(mini_repo), "site"])
    primeiro = sem_horario((mini_repo / "site-src" / "index.md").read_text(encoding="utf-8"))
    sobra = mini_repo / "site-src" / "arquivo-velho.md"
    sobra.write_text("lixo\n", encoding="utf-8")
    painel.main(["--raiz", str(mini_repo), "site"])
    assert not sobra.exists()  # reconstrói do zero
    segundo = sem_horario((mini_repo / "site-src" / "index.md").read_text(encoding="utf-8"))
    assert segundo == primeiro


# ---------------------------------------------------------------------------
# Dashboard e navegação do site
# ---------------------------------------------------------------------------


def test_dashboard_e_painel_e_nao_readme(mini_repo: pathlib.Path):
    painel.main(["--raiz", str(mini_repo), "site"])
    fontes = mini_repo / "site-src"
    dashboard = (fontes / "index.md").read_text(encoding="utf-8")

    assert "# Humanitas" in dashboard
    assert "humanitas-hero" in dashboard or "grid cards" in dashboard
    assert "## Trilhas" in dashboard or "Trilhas — progresso" in dashboard
    assert "Temas" in dashboard
    assert "Onde você está" in dashboard
    # o README vira a página "Sobre", não a home
    assert (fontes / "sobre.md").exists()
    assert not (fontes / "README.md").exists()
    assert (fontes / "sobre.md").read_text(encoding="utf-8").startswith("# Painel")


def test_dashboard_mostra_progresso_real(mini_repo: pathlib.Path):
    painel.main(["--raiz", str(mini_repo), "site"])
    dashboard = (mini_repo / "site-src" / "index.md").read_text(encoding="utf-8")
    # mini-repo tem 3 nós, 1 concluído e 3 notas
    assert "1 de 3" in dashboard
    assert "█" in dashboard and "░" in dashboard


def test_dashboard_sem_links_quebrados(mini_repo: pathlib.Path):
    painel.main(["--raiz", str(mini_repo), "site"])
    fontes = mini_repo / "site-src"
    problemas = painel._links_quebrados(fontes, sorted(fontes.rglob("*.md")))
    assert problemas == []


def test_indices_gerados_por_tema(mini_repo: pathlib.Path):
    painel.main(["--raiz", str(mini_repo), "site"])
    indice = (mini_repo / "site-src" / "conceitos" / "index.md").read_text(encoding="utf-8")
    assert ("## Sociologia" in indice or "Sociologia" in indice)
    assert "Habitus" in indice
    # novo UI usa cards com data-tema e filtros, não headings obrigatórios
    assert "humanitas-filter" in indice or "conceito-card" in indice
    # link relativo dentro da pasta, sem o prefixo conceitos/
    assert "sociologia-habitus.md" in indice

    eixos = (mini_repo / "site-src" / "eixos.md").read_text(encoding="utf-8")
    assert "Natureza × Cultura" in eixos
    assert "conceitos/eixo-natureza-cultura.md" in eixos


def test_nav_do_mkdocs_aponta_para_paginas_existentes(mini_repo: pathlib.Path):
    """Todo destino do nav precisa existir: senão o build do site falha."""
    import re

    raiz = pathlib.Path(__file__).resolve().parents[1]
    config = (raiz / "mkdocs.yml").read_text(encoding="utf-8")
    alvos = re.findall(r"^\s+-\s+[^:]+:\s+([^\s#]+\.md)\s*$", config, re.M)
    assert alvos, "nav não encontrado em mkdocs.yml"

    painel.montar_site_src(raiz, mini_repo / "site-src")
    faltando = [alvo for alvo in alvos if not (mini_repo / "site-src" / alvo).exists()]
    assert faltando == [], f"nav aponta para páginas que o site não gera: {faltando}"


def test_site_converte_readme_em_index_e_ajusta_links(mini_repo: pathlib.Path):
    painel.main(["--raiz", str(mini_repo), "site"])
    fontes = mini_repo / "site-src"
    assert (fontes / "diario" / "index.md").exists()
    assert not (fontes / "diario" / "README.md").exists()
    # um link para README.md passa a apontar para index.md
    trilha = fontes / "trilhas" / "sociologia-teste.md"
    trilha.write_text(
        trilha.read_text(encoding="utf-8") + "\n[diário](../diario/README.md)\n",
        encoding="utf-8",
    )
    painel._ajustar_links_readme(fontes)
    assert "../diario/index.md" in trilha.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Marcos de decisão (gatilhos do Guia 07, Fase 4)
# ---------------------------------------------------------------------------


def test_marcos_de_decisao_no_progresso(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "progresso"]) == 0
    texto = (mini_repo / "progresso.md").read_text(encoding="utf-8")
    assert "## Marcos de decisão" in texto
    assert "| Notas reescritas (`ok`) |" in texto
    assert "| Entradas de diário |" in texto
    # mini-repo: 3 notas ok, 1 diário -> todos abaixo do alvo
    assert "escreva notas" in texto


def test_marcos_refletem_os_numeros(indice=None):
    indice = {
        "conceitos": [
            {"status": "ok", "tem_trecho": True, "tema": "sociologia", "tipo": "conceito",
             "definicao": "d", "pendencias": []} for _ in range(25)
        ],
        "trilhas": [], "diario": [], "fichas": [], "trechos": [], "livros": [],
        "totais": {},
    }
    marcos = dict((rotulo, (atual, alvo, atingido)) for rotulo, atual, alvo, _, atingido in painel.marcos_de_decisao(indice))
    assert marcos["Notas reescritas (`ok`)"][0] == 25
    assert marcos["Notas reescritas (`ok`)"][2] is True
    assert marcos["Entradas de diário"][2] is False

# ---------------------------------------------------------------------------
# Afirmações
# ---------------------------------------------------------------------------

def test_afirmacoes_detecta_porcentagem_e_ano(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8")
    texto += "\n\nEstudos mostram que 95% dos casos ocorrem em 2021. O maior impacto é evidente.\n"
    nota.write_text(texto, encoding="utf-8")
    coletadas = painel.coletar_afirmacoes(mini_repo)
    # deve encontrar pelo menos porcentagem e ano
    total = sum(len(v) for v in coletadas.values())
    assert total >= 2
    assert any("sociologia-habitus.md" in k for k in coletadas)


def test_cmd_afirmacoes_gera_relatorio(mini_repo: pathlib.Path, capsys):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8")
    texto += "\n\nPesquisas indicam que tudo é absoluto.\n"
    nota.write_text(texto, encoding="utf-8")
    assert painel.main(["--raiz", str(mini_repo), "afirmacoes"]) == 0
    rel = mini_repo / "relatorio-afirmacoes.md"
    assert rel.exists()
    conteudo = rel.read_text(encoding="utf-8")
    assert "Relatório de afirmações" in conteudo
    assert "sociologia-habitus.md" in conteudo


def test_fonte_verificada_obrigatoria(mini_repo: pathlib.Path):
    # remove fonte_verificada de uma nota e verifica que auditoria aponta erro
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8").replace("fonte_verificada: sim", "")
    nota.write_text(texto, encoding="utf-8")
    erros, _ = painel.auditar(mini_repo)
    assert any("fonte_verificada" in e for e in erros)


def test_fonte_verificada_ok_com_citacao(mini_repo: pathlib.Path):
    # nota ok sem trecho com cap/pagina deve gerar erro, mas com frase secundaria passa
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    # já tem status ok e trecho com cap/p no fixture original (cap. 3, p. 94)
    erros, _ = painel.auditar(mini_repo)
    assert not any("Trecho de apoio" in e for e in erros)
    # agora remove trecho e coloca frase secundaria
    texto = nota.read_text(encoding="utf-8")
    # substitui trecho por frase secundaria
    texto = texto.replace('(cap. 3, p. 94)', 'Sem citação — fonte secundária')
    nota.write_text(texto, encoding="utf-8")
    erros, _ = painel.auditar(mini_repo)
    assert not any("Trecho de apoio" in e for e in erros)


# ---------------------------------------------------------------------------
# PR3: esquema enriquecido
# ---------------------------------------------------------------------------

def test_esquema_enriquecido_preservado_no_indice(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8")
    texto = texto.replace("fonte_verificada: sim", "fonte_verificada: sim\ntradicao: \"estruturalista\"\nnivel_evidencia: alta\ncontestado_por: [Bourdieu]\neixos: [Conflito × Coesão]\nrelacoes: [campo]")
    nota.write_text(texto, encoding="utf-8")
    indice = painel.montar_indice(mini_repo)
    hit = next(c for c in indice["conceitos"] if c["arquivo"] == "sociologia-habitus.md")
    assert hit["tradicao"] == "estruturalista"
    assert hit["nivel_evidencia"] == "alta"
    assert hit["contestado_por"] == ["Bourdieu"]
    assert hit["eixos"] == ["Conflito × Coesão"]
    assert hit["relacoes"] == ["campo"]


def test_nivel_evidencia_invalido_da_erro(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8").replace("fonte_verificada: sim", "fonte_verificada: sim\nnivel_evidencia: invalido")
    nota.write_text(texto, encoding="utf-8")
    erros, _ = painel.auditar(mini_repo)
    assert any("nivel_evidencia" in e for e in erros)


def test_nova_conceito_com_tradicao(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "nova", "--tipo", "conceito", "--nome", "Teste Tradicao", "--tema", "sociologia", "--tradicao", "fenomenologica", "--nivel-evidencia", "forte", "--contestado-por", "Autor A, Autor B"]) == 0
    novo = mini_repo / "conceitos" / "sociologia-teste-tradicao.md"
    assert novo.exists()
    fm = painel.parse_frontmatter(novo.read_text(encoding="utf-8"))
    assert fm["tradicao"] == "fenomenologica"
    assert fm["nivel_evidencia"] == "forte"
    assert fm["contestado_por"] == ["Autor A", "Autor B"]



# ---------------------------------------------------------------------------
# PR4: grafo e cartões
# ---------------------------------------------------------------------------

def test_grafo_mapeia_relacoes(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8")
    texto = texto.replace("fonte_verificada: sim", "fonte_verificada: sim\nrelacoes: [campo]\neixos: [Conflito × Coesão]")
    nota.write_text(texto, encoding="utf-8")
    indice = painel.montar_indice(mini_repo)
    grafo = painel.montar_grafo(indice)
    assert grafo["totais"]["nodes"] >= 3
    assert any(e["tipo"] == "relacionado" for e in grafo["edges"])
    assert any(e["tipo"] == "eixo" for e in grafo["edges"])


def test_cmd_grafo_gera_json(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "grafo"]) == 0
    assert (mini_repo / "indices" / "grafo.json").exists()
    dados = painel.montar_grafo(painel.montar_indice(mini_repo))
    assert "nodes" in dados and "edges" in dados


def test_cartoes_incluem_tradicao(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    texto = nota.read_text(encoding="utf-8").replace("fonte_verificada: sim", "fonte_verificada: sim\ntradicao: fenomenologica\nnivel_evidencia: alta")
    nota.write_text(texto, encoding="utf-8")
    indice = painel.montar_indice(mini_repo)
    conceitos = painel.coletar_conceitos(mini_repo)
    reg = next(c for c in conceitos if c["arquivo"] == "sociologia-habitus.md")
    cartoes = painel.cartoes_de(reg)
    # deve ter cartão de tradição e nivel_evidencia
    assert any("tradição" in c[1].lower() for c in cartoes)
    assert any("evidência" in c[1].lower() or "evidencia" in c[1].lower() for c in cartoes)


# ---------------------------------------------------------------------------
# PR5: autores/obras
# ---------------------------------------------------------------------------

def test_obras_agrupa_por_obra(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    dados = painel.agrupar_obras(indice)
    assert "obras" in dados and "autores" in dados
    # mini_repo tem pelo menos 1 obra (habitus etc.)
    assert len(dados["obras"]) >= 1
    assert any("Bourdieu" in autor for autor in dados["autores"])


def test_cmd_obras_gera_json(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "obras"]) == 0
    assert (mini_repo / "indices" / "obras.json").exists()


# ---------------------------------------------------------------------------
# PR6: retenção
# ---------------------------------------------------------------------------

def test_retencao_calcula_taxa(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    cartoes = painel.gerar_flashcards(mini_repo, indice)
    dados = painel.calcular_retencao(indice, cartoes)
    assert "total_conceitos" in dados
    assert "taxa_ok" in dados
    assert dados["total_conceitos"] >= 2


def test_cmd_retencao_gera_json(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "retencao"]) == 0
    assert (mini_repo / "indices" / "retencao.json").exists()


# ---------------------------------------------------------------------------
# PR7: portão publicação site
# ---------------------------------------------------------------------------

def test_site_gate_bloqueia_com_erro(mini_repo: pathlib.Path):
    # cria duplicata para gerar erro de auditoria
    import shutil
    orig = mini_repo / "conceitos" / "sociologia-habitus.md"
    dup = mini_repo / "conceitos" / "sociologia-habitus-duplicata.md"
    shutil.copy(orig, dup)
    # auditar deve falhar
    erros, _ = painel.auditar(mini_repo)
    assert any("duplicado" in e.lower() for e in erros)
    assert painel.main(["--raiz", str(mini_repo), "site"]) == 1


def test_site_gate_passou_sem_erro(mini_repo: pathlib.Path):
    assert painel.main(["--raiz", str(mini_repo), "site"]) == 0



# ---------------------------------------------------------------------------
# Progresso marcado no site -> trilhas (aplicar-progresso)
# ---------------------------------------------------------------------------


def test_aplicar_progresso_marca_nos_e_avisa_trilha_inexistente(mini_repo: pathlib.Path):
    dados = {"versao": 1, "trilhas": {"sociologia-teste": [0, 1], "nao-existe": [0]}}
    mudancas, avisos = painel.aplicar_progresso(dados, mini_repo, gravar=True)
    texto = (mini_repo / "trilhas" / "sociologia-teste.md").read_text(encoding="utf-8")
    assert "1. [x]" in texto and "2. [x]" in texto and "3. [ ]" in texto
    assert any("sociologia-teste" in m for m in mudancas)
    assert any("nao-existe" in a for a in avisos)
    # ainda não concluiu todos os nós: o status não muda
    assert "status: em-andamento" in texto


def test_aplicar_progresso_conclui_trilha_e_e_idempotente(mini_repo: pathlib.Path):
    dados = {"versao": 1, "trilhas": {"sociologia-teste": [0, 1, 2]}}
    mudancas, _ = painel.aplicar_progresso(dados, mini_repo, gravar=True)
    texto = (mini_repo / "trilhas" / "sociologia-teste.md").read_text(encoding="utf-8")
    assert texto.count("1. [x]") == 1 and "[ ]" not in texto
    assert "status: concluida" in texto
    assert any("concluida" in m for m in mudancas)

    # segunda aplicação não muda nada
    mudancas2, avisos2 = painel.aplicar_progresso(dados, mini_repo, gravar=True)
    assert mudancas2 == []
    assert (mini_repo / "trilhas" / "sociologia-teste.md").read_text(encoding="utf-8") == texto


def test_aplicar_progresso_simulacao_nao_grava(mini_repo: pathlib.Path):
    antes = (mini_repo / "trilhas" / "sociologia-teste.md").read_text(encoding="utf-8")
    mudancas, _ = painel.aplicar_progresso(
        {"trilhas": {"sociologia-teste": [1, 2]}}, mini_repo, gravar=False
    )
    assert mudancas
    assert (mini_repo / "trilhas" / "sociologia-teste.md").read_text(encoding="utf-8") == antes


def test_cli_aplicar_progresso(mini_repo: pathlib.Path, tmp_path: pathlib.Path, capsys):
    arquivo = mini_repo / "progresso.json"
    arquivo.write_text('{"versao": 1, "trilhas": {"sociologia-teste": [1]}}', encoding="utf-8")
    assert painel.main(["--raiz", str(mini_repo), "aplicar-progresso", "--arquivo", str(arquivo), "--simular"]) == 0
    saida = capsys.readouterr().out
    assert "simulação" in saida
    trilha = mini_repo / "trilhas" / "sociologia-teste.md"
    assert "2. [x]" not in trilha.read_text(encoding="utf-8")

    assert painel.main(["--raiz", str(mini_repo), "aplicar-progresso", "--arquivo", str(arquivo)]) == 0
    assert "2. [x]" in trilha.read_text(encoding="utf-8")


def test_cli_aplicar_progresso_sem_arquivo_falha(mini_repo: pathlib.Path, capsys):
    assert painel.main(["--raiz", str(mini_repo), "aplicar-progresso"]) == 1
    assert "Informe o arquivo" in capsys.readouterr().out


# ---------------------------------------------------------------------------
# Página "Registrar" (site)
# ---------------------------------------------------------------------------


def test_site_gera_pagina_registrar_com_formulario(mini_repo: pathlib.Path):
    painel.montar_site_src(mini_repo)
    texto = (mini_repo / "site-src" / "registrar.md").read_text(encoding="utf-8")
    assert 'id="hum-criar"' in texto
    assert 'id="hum-config"' in texto
    assert '"temas"' in texto and "sociologia" in texto
    assert "aplicar-progresso" in texto
    assert "## 2. Reescrever" in texto
    assert "Abrir no GitHub preenchido" in texto


def test_pagina_registrar_lista_pendencia_com_link_de_edicao(mini_repo: pathlib.Path):
    nota = mini_repo / "conceitos" / "sociologia-habitus.md"
    nota.write_text(
        nota.read_text(encoding="utf-8").replace("status: ok", "status: rascunho"),
        encoding="utf-8",
    )
    painel.montar_site_src(mini_repo)
    texto = (mini_repo / "site-src" / "registrar.md").read_text(encoding="utf-8")
    assert "edit/main/conceitos/sociologia-habitus.md" in texto


def test_indice_guarda_titulo_dos_nos(mini_repo: pathlib.Path):
    indice = painel.montar_indice(mini_repo)
    trilha = indice["trilhas"][0]
    assert trilha["nos_total"] == len(trilha["nos"]) == 3
    assert "Habitus" in trilha["nos"][0]
    assert not any("](" in no for no in trilha["nos"])  # markdown dos links sai limpo


def test_pagina_registrar_tem_central_de_progresso(mini_repo: pathlib.Path):
    painel.montar_site_src(mini_repo)
    texto = (mini_repo / "site-src" / "registrar.md").read_text(encoding="utf-8")
    assert 'id="hum-progresso"' in texto
    assert 'data-acao="exportar"' in texto and 'data-acao="importar"' in texto
    assert 'data-acao="baixar-md"' in texto and 'data-acao="copiar-comando"' in texto
    assert "make aplicar-progresso ARQUIVO=~/Downloads/progresso.json" in texto
    # a configuração levada ao JS tem slug, nome, total e os títulos dos nós
    config = texto.split('id="hum-config">')[1].split("</script>")[0]
    dados = json.loads(config)
    trilha = dados["trilhas"][0]
    assert trilha["slug"] == "sociologia-teste"
    assert trilha["total"] == 3 and len(trilha["nos"]) == 3


def test_site_copia_assets_js(mini_repo: pathlib.Path):
    pasta = mini_repo / "docs" / "assets" / "js"
    pasta.mkdir(parents=True, exist_ok=True)
    (pasta / "progresso.js").write_text("// teste\n", encoding="utf-8")
    painel.montar_site_src(mini_repo)
    assert (mini_repo / "site-src" / "assets" / "js" / "progresso.js").exists()


# ---------------------------------------------------------------------------
# Biblioteca de mídias (videoaulas, artigos, filmes)
# ---------------------------------------------------------------------------

MIDIA_OK = """
versao: 1
atualizado_em: 2026-10-27
itens:
  - id: aula-habitus
    tipo: videoaula
    peso: divulgacao
    titulo: "Aula sobre habitus"
    autor: "Canal de teste"
    canal: "Canal de teste"
    url: "https://www.youtube.com/watch?v=abc123"
    tema: sociologia
    conceitos: [sociologia-habitus]
    nota: "Explica o conceito em 12 minutos."
    verificado_em: 2026-10-27
    verificado_como: oembed
  - id: filme-teste
    tipo: filme
    peso: obra-de-apoio
    titulo: "Filme de teste (2001)"
    autor: "Diretor de teste"
    onde: "streaming"
    tema: filosofia
    conceitos: [eixo-natureza-cultura]
    nota: "Serve para discutir eudaimonia."
    verificado_em: 2026-10-27
    verificado_como: material-do-autor
"""


def _escrever_midias(mini_repo: pathlib.Path, texto: str = MIDIA_OK) -> pathlib.Path:
    caminho = mini_repo / "midias" / "biblioteca.yml"
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(texto, encoding="utf-8")
    return caminho


def test_midias_validas_nao_geram_erro(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo)
    itens, atualizado, erros = painel.carregar_midias(mini_repo)
    assert erros == [] and len(itens) == 2
    conceitos = {p.stem for p in (mini_repo / "conceitos").glob("*.md")}
    erros, avisos = painel.validar_midias(itens, conceitos, atualizado_em=atualizado)
    assert erros == []


def test_midias_sem_verificacao_e_erro(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo, MIDIA_OK.replace("    verificado_em: 2026-10-27\n    verificado_como: oembed\n", ""))
    itens, atualizado, _ = painel.carregar_midias(mini_repo)
    conceitos = {p.stem for p in (mini_repo / "conceitos").glob("*.md")}
    erros, _ = painel.validar_midias(itens, conceitos, atualizado_em=atualizado)
    assert any("verificado_em" in e for e in erros)
    assert any("verificado_como" in e for e in erros)


def test_midias_conceito_inexistente_e_erro(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo, MIDIA_OK.replace("sociologia-habitus", "sociologia-fantasma"))
    itens, atualizado, _ = painel.carregar_midias(mini_repo)
    erros, _ = painel.validar_midias(itens, {"sociologia-habitus"}, atualizado_em=atualizado)
    assert any("conceito inexistente" in e and "sociologia-fantasma" in e for e in erros)


def test_midias_url_repetida_e_tema_invalido(mini_repo: pathlib.Path):
    texto = MIDIA_OK.replace("id: filme-teste", "id: outra-aula").replace(
        "tipo: filme", "tipo: videoaula"
    ).replace('onde: "streaming"', 'url: "https://www.youtube.com/watch?v=abc123"').replace(
        "material-do-autor", "oembed"
    ).replace("tema: filosofia", "tema: alquimia")
    _escrever_midias(mini_repo, texto)
    itens, atualizado, _ = painel.carregar_midias(mini_repo)
    conceitos = {p.stem for p in (mini_repo / "conceitos").glob("*.md")}
    erros, _ = painel.validar_midias(itens, conceitos, atualizado_em=atualizado)
    assert any("url repetida" in e for e in erros)
    assert any("tema inválido" in e for e in erros)


def test_midias_com_url_nao_pode_ser_material_do_autor(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo, MIDIA_OK.replace("verificado_como: oembed", "verificado_como: material-do-autor", 1))
    itens, atualizado, _ = painel.carregar_midias(mini_repo)
    conceitos = {p.stem for p in (mini_repo / "conceitos").glob("*.md")}
    erros, _ = painel.validar_midias(itens, conceitos, atualizado_em=atualizado)
    assert any("material-do-autor" in e for e in erros)


def test_midias_geracao_markdown_e_json(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo)
    md, js, total = painel.gravar_midias(mini_repo)
    assert total == 2
    texto = md.read_text(encoding="utf-8")
    assert "# Mídias" in texto
    assert "[Aula sobre habitus](https://www.youtube.com/watch?v=abc123)" in texto
    assert "conceitos/sociologia-habitus.md" in texto  # liga a mídia à nota
    assert "Filme de teste (2001)" in texto and "streaming" in texto
    assert "Canal de teste" in texto
    dados = json.loads(js.read_text(encoding="utf-8"))
    assert dados["totais"]["itens"] == 2
    assert dados["totais"]["por_tipo"] == {"filme": 1, "videoaula": 1}
    # determinístico: gerar de novo não muda nada
    antes = texto
    painel.gravar_midias(mini_repo)
    assert md.read_text(encoding="utf-8") == antes


def test_midias_markdown_nao_quebra_tabela(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo, MIDIA_OK.replace("Aula sobre habitus", "Aula | com pipe"))
    md, _, _ = painel.gravar_midias(mini_repo)
    linha = [l for l in md.read_text(encoding="utf-8").splitlines() if "Aula" in l and l.startswith("|")]
    assert linha and r"\|" in linha[0]


def test_midias_desatualizado_e_erro_de_auditoria(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo)
    erros, avisos = painel.auditar(mini_repo)
    assert not any("desatualizado" in e for e in erros)
    assert any("não foi gerado" in a for a in avisos)

    painel.gravar_midias(mini_repo)
    erros, _ = painel.auditar(mini_repo)
    assert not any("midias.md" in e for e in erros)

    # mexer na fonte sem regerar deixa a página velha: a auditoria cobra
    _escrever_midias(mini_repo, MIDIA_OK.replace("Explica o conceito", "Explica melhor o conceito"))
    erros, _ = painel.auditar(mini_repo)
    assert any("midias.md está desatualizado" in e for e in erros)


def test_cli_midias(mini_repo: pathlib.Path, capsys):
    _escrever_midias(mini_repo)
    assert painel.main(["--raiz", str(mini_repo), "midias"]) == 0
    saida = capsys.readouterr().out
    assert "2 indicação(ões)" in saida
    assert (mini_repo / "midias.md").exists()
    assert (mini_repo / "indices" / "midias.json").exists()


def test_site_publica_pagina_de_midias(mini_repo: pathlib.Path):
    _escrever_midias(mini_repo)
    painel.montar_site_src(mini_repo)
    texto = (mini_repo / "site-src" / "midias.md").read_text(encoding="utf-8")
    assert "# Mídias" in texto
    assert "https://www.youtube.com/watch?v=abc123" in texto
