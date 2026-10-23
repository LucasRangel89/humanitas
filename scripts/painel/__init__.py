"""Compatibilidade: reexporta a API pública de scripts.painel para os testes."""

from .modelo import (
    RAIZ_PADRAO,
    TEMAS,
    STATUS_VALIDOS,
    NIVEIS_VALIDOS,
    TIPOS_VALIDOS,
    NIVEIS_EVIDENCIA_VALIDOS,
    MARCADOR_TEMAS,
    MARCADOR_PROGRESSO,
    SECOES_OBRIGATORIAS,
    SECAO_TRECHO,
    REGEX_CHECKBOX,
    REGEX_SECAO_NO,
    REGEX_FENCE,
    REGEX_CODIGO_INLINE,
    REGEX_LINK,
    REGEX_WIKILINK,
    REGEX_TITULO,
    REGEX_SECAO,
    PLACEHOLDERS,
    PASTAS_SITE,
    ARQUIVOS_SITE,
    NIVEIS_EVIDENCIA_VALIDOS,
    ErroFrontmatter,
    _ERROS_FRONTMATTER,
    _limpar_erros_frontmatter,
    _registrar_erro_frontmatter,
    ler,
    normalizar,
    parse_frontmatter,
    parse_tags,
    secoes,
    achar_secao,
    extrair_secao,
    titulo_h1,
    limpar_markdown,
    sem_codigo,
    listar_md,
    eh_placeholder,
    rel,
    substituir_bloco,
)

from .indice import (
    coletar_conceitos,
    coletar_livros,
    tema_do_indice_antigo,
    coletar_trechos,
    progresso_trilha,
    coletar_trilhas,
    coletar_diario,
    montar_indice,
    tabela_temas,
    substituir_bloco,
    gravar_indice,
    atualizar_readme_temas,
)

from .progresso import (
    progresso_barra,
    pendencias_da_nota,
    calcular_progresso,
    MARCOS_DECISAO,
    marcos_de_decisao,
    texto_progresso,
    bloco_progresso_readme,
    atualizar_readme_progresso,
)

from .cartoes import cartoes_de, gerar_flashcards

from .grafo import montar_grafo, gravar_grafo, cmd_grafo

from .obras import agrupar_obras, gravar_obras, cmd_obras

from .retencao import calcular_retencao, gravar_retencao, cmd_retencao

from .marcacao import aplicar_progresso

from .auditoria import (
    _links_quebrados,
    _wikilinks,
    _validar_metadados,
    _duplicados,
    auditar,
)

from .afirmacoes import (
    REGEX_AFIRMACOES_PERCENT,
    REGEX_AFIRMACOES_ESTUDOS,
    REGEX_AFIRMACOES_ANO,
    REGEX_AFIRMACOES_SUPERLATIVO,
    _afirmacoes_do_texto,
    coletar_afirmacoes,
    gerar_relatorio_afirmacoes,
    cmd_afirmacoes,
)

from .scaffolding import (
    TIPOS_NOVA,
    ROTULO_H1,
    slug,
    yaml_escalar,
    serializar_frontmatter,
    corpo_do_template,
    desativar_links_quebrados,
    cmd_nova,
    cmd_pendencias,
)

from .site import (
    GLIFO_STATUS,
    _link_nota,
    pagina_dashboard,
    pagina_conceitos,
    pagina_trilhas,
    pagina_eixos,
    _ajustar_links_readme,
    montar_site_src,
    cmd_site,
)

from .cli import (
    cmd_indice,
    cmd_tabela,
    cmd_progresso,
    cmd_flashcards,
    cmd_auditar,
    cmd_tudo,
    COMANDOS,
    main,
)

# Aliases mantidas para compatibilidade com imports antigos
# (alguns testes acessam painel.TIPOS_NOVA etc. via painel.*)
__all__ = [
    "RAIZ_PADRAO", "TEMAS", "STATUS_VALIDOS", "NIVEIS_VALIDOS", "TIPOS_VALIDOS",
    "MARCADOR_TEMAS", "MARCADOR_PROGRESSO", "SECOES_OBRIGATORIAS", "SECAO_TRECHO",
    "REGEX_CHECKBOX", "REGEX_SECAO_NO", "REGEX_FENCE", "REGEX_CODIGO_INLINE",
    "REGEX_LINK", "REGEX_WIKILINK", "REGEX_TITULO", "REGEX_SECAO",
    "PLACEHOLDERS", "PASTAS_SITE", "ARQUIVOS_SITE",
    "ErroFrontmatter", "_ERROS_FRONTMATTER", "ler", "normalizar", "parse_frontmatter",
    "montar_indice", "auditar", "main",
]
