# Guia 07 — Rumos: o que fazer depois da fundação

Este guia é o plano de voo do projeto depois da limpeza e da automação.
O diagnóstico completo (pontos fortes, riscos e evidências) está em
[`analise-do-projeto.md`](analise-do-projeto.md).

## Princípio

> O projeto não precisa de mais notas. Precisa de **notas reescritas**, de
> **citações verificáveis** e de **diário**. Tudo o mais é infraestrutura.

A métrica-norte é `notas com status: ok + entradas de diário`, visível em
[`progresso.md`](../progresso.md). Número de PDFs convertidos não é progresso.

## Fase 1 — Fechar o ciclo de estudo (agora, ~2 semanas)

O objetivo é provar que o método funciona em **uma** nota, com qualidade de padrão-ouro,
e só depois escalar.

1. **Escolher a obra da vez**: Mills, *A Imaginação Sociológica* (livro nº 1 do
   [Guia 05](05-prioridades-de-leitura.md); cobre os nós 1 e 12 de Sociologia e dois da Integrada).
2. **Escrever a ficha de leitura** em `acervo/fichas/mills-imaginacao-sociologica-ficha.md`
   usando o `template-livro.md`.
3. **Reescrever 5 notas** sem consultar a IA enquanto escreve (compare depois):
   - `sociologia-imaginacao-sociologica.md`
   - `eixo-conflito-coesao.md`
   - `sociologia-fato-social.md`
   - `sociologia-alienacao.md`
   - `sociologia-racionalizacao.md`
4. **Padrão-ouro de cada nota** (é o que muda o `status` para `ok`):
   - definição em uma frase que caiba num cartão;
   - explicação com as suas palavras + **um exemplo brasileiro**;
   - citação literal com **capítulo e página** (ou "sem citação — fonte secundária");
   - pelo menos uma conexão interdisciplinar com o *porquê*;
   - posição no(s) eixo(s) correspondente(s).
5. **Escrever a primeira entrada do diário** em `diario/AAAA-MM-DD-sociologia-imaginacao.md`.
6. Rodar `make auditar` e conferir o `progresso.md`: 5 notas `ok`, 1 ficha, 1 diário.

## Fase 2 — Jardim público (30–60 dias)

Transformar o painel em site com busca, mantendo o acervo fora do Git.

```yaml
# mkdocs.yml
site_name: Humanitas
theme:
  name: material
  language: pt-BR
  features: [navigation.sections, navigation.indexes, search.suggest, content.tags]
plugins:
  - search:
      lang: pt
  - tags
markdown_extensions: [admonition, tables, toc, pymdownx.superfences]
nav:
  - Início: README.md
  - Progresso: progresso.md
  - Trilhas:
      - Psicologia 1: trilhas/psicologia-nivel-1.md
      - Psicologia 2: trilhas/psicologia-nivel-2.md
      - Filosofia: trilhas/filosofia-nivel-1.md
      - Sociologia: trilhas/sociologia-nivel-1.md
      - Integrada: trilhas/integrada-nivel-1.md
  - Conceitos: conceitos/
```

Passos: `pip install mkdocs-material` → `mkdocs serve` local → `mkdocs gh-deploy`.
Publicar **somente** `conceitos/`, `trilhas/`, `diario/`, `trechos/` e `acervo/fichas/`.
A `LICENSE-CONTEUDO.md` (CC BY-SA) é o que torna essa publicação legítima.

Métrica de saída da fase: 20 notas `ok`, 8 entradas de diário, 1 trilha em 30%.

## Fase 3 — Escolher **um** caminho (90 dias)

Só depois de ter conteúdo, escolha **um** com base no sinal que o uso der:

| Caminho | Quando escolher | Primeiro passo |
|---|---|---|
| **A. Aprofundar o painel** (recomendado) | Você usa o site quase todo dia | Fechar 2 trilhas e converter 3 livros-chave |
| **B. Ferramenta para outras pessoas** | Você quer que o pipeline sirva a outros | Empacotar o CLI (`pipx`), documentar em inglês, exemplos |
| **C. Curso / produto** | Você já concluiu 2–3 trilhas e sabe o que funciona | Transformar uma trilha em curso com quiz e progresso |
| **D. Tutor com IA (RAG)** | O gargalo é revisar, não escrever | SQLite FTS5 + embeddings locais, resposta sempre com citação do arquivo |

### Regras para o caminho D (IA de consulta), se for por ele

- A resposta **deve citar** a nota e a seção; nunca gerar conteúdo sem fonte no painel.
- A IA pode gerar **perguntas** e localizar trechos — nunca escrever o diário.
- Preferir busca local (FTS5/Pagefind) antes de qualquer LLM: 90% do valor, custo zero.

## O que não fazer

- Converter os 100+ PDFs "para depois".
- Construir gamificação/XP antes de ter notas reescritas: gamificar rascunhos de IA gamifica o vazio.
- Versionar texto integral em repositório público.
- Criar notas novas antes de fechar as lacunas (citação, exemplo, eixo) das existentes.
- Deixar o diário ser gerado por IA — é o único ativo que não pode ser terceirizado.

## Backlog priorizado

| Prioridade | Item | Esforço |
|---|---|---|
| P1 | 5 notas padrão-ouro + 1 ficha + 1 diário | 1–2 semanas |
| P1 | Habilitar branch protection exigindo o CI verde em `main` | 10 min |
| P2 | Site MkDocs com busca, tags e deploy no Pages | 2 dias |
| P2 | Conversor por capítulo (arquivos menores, melhor busca) | 1 dia |
| P2 | `pydantic` para validar o schema das notas + `pre-commit` | meio dia |
| P3 | Grafo de conexões, quiz automático, RAG local | semanas |

## Como medir (sem autoengano)

```bash
python -m scripts.painel progresso && sed -n '1,25p' progresso.md
```

| Métrica | Hoje | 30 dias | 90 dias |
|---|---|---|---|
| Notas `ok` | 0 | 10 | 25 |
| Diários | 0 | 4 | 12 |
| Fichas | 0 | 1 | 3 |
| Nós de trilha | 0/56 | 6 | 15 |
| Notas com citação + página | 0 | 10 | 25 |
| Erros de auditoria | 0 | 0 | 0 |
