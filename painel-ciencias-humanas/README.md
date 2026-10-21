# Painel de Estudos — Ciências Humanas

Base de estudos autodidata que concentra, em um só lugar, os tópicos, conceitos e trechos essenciais de obras didáticas de ciências humanas: história, sociologia, filosofia, ciência política, antropologia e áreas vizinhas.

## O que é este projeto

Este repositório funciona como um **painel pessoal de estudos**. Ele nasce de uma biblioteca de PDFs de obras didáticas e se organiza em três camadas complementares:

1. **Acervo** — o conteúdo dos livros convertido para Markdown, um formato de texto simples que pode ser lido em qualquer navegador, pesquisado com Ctrl+F e que nunca "quebra" como um PDF.
2. **Notas de estudo** — conceitos explicados, trechos marcantes e fichas de leitura, produzidos com apoio de inteligência artificial (NotebookLM) a partir do acervo, e organizados em modelos padronizados.
3. **Índices** — um mapa em formato JSON que lista tudo o que já foi processado, servindo de sumário geral do painel.

A lógica do projeto é simples: em vez de reler um PDF de 400 páginas para achar uma ideia, você abre a nota do conceito, o trecho comentado ou a ficha do livro — tudo interligado e organizado por tema.

## Como navegar

| Pasta | O que você encontra |
|---|---|
| `acervo/` | Um arquivo Markdown por livro convertido (texto integral da obra) |
| `conceitos/` | Notas de conceito — uma ideia central por arquivo, com explicação e trecho de apoio |
| `trechos/` | Citações e passagens guardadas, sempre acompanhadas de um comentário pessoal |
| `indices/` | `indice.json` — o mapa geral do acervo processado |
| `templates/` | Modelos prontos para copiar ao criar uma nota nova |
| `docs/` | Guias passo a passo: criar o repositório, extrair conteúdo dos PDFs, atualizar tudo |
| `notebooks/` | Notebooks do Google Colab (sem digitar código): `converter-pdfs` transforma PDFs em Markdown; `atualizador-do-painel` regenera o índice, a tabela de temas, os flashcards e audita o repositório |

## Painel de temas

Este é o mapa dos estudos. Conforme o acervo for processado, os itens abaixo viram links clicáveis para as notas de cada tema. Esta tabela é regenerada automaticamente pelo notebook `atualizador-do-painel.ipynb` — não edite à mão.

<!-- PAINEL-TEMAS-INICIO -->

| Tema | Status | Notas de conceito | Livros processados |
|---|---|---|---|
| História | Em breve | 0 | 0 |
| Sociologia | Em breve | 0 | 0 |
| Filosofia | Em breve | 0 | 0 |
| Ciência Política | Em breve | 0 | 0 |
| Antropologia | Em breve | 0 | 0 |
| Economia | Em breve | 0 | 0 |
| Geografia | Em breve | 0 | 0 |
| Psicologia Social | Em breve | 0 | 0 |

<!-- PAINEL-TEMAS-FIM -->

## Como adicionar um livro novo (resumo rápido)

O fluxo completo está explicado em `docs/02-fluxo-de-extracao.md`, mas em resumo são cinco passos:

1. **Converter** o PDF em Markdown usando o notebook `notebooks/converter-pdfs.ipynb` (Google Colab, funciona no navegador).
2. **Explorar** a obra no NotebookLM usando os prompts prontos de `docs/03-prompts-notebooklm.md`.
3. **Anotar** os resultados usando os modelos da pasta `templates/`.
4. **Publicar** os arquivos aqui no GitHub (guia em `docs/01-criar-repositorio-no-github.md` e `docs/04-atualizar-o-github.md`).
5. **Regenerar** o índice, a tabela de temas e os flashcards com o notebook `notebooks/atualizador-do-painel.ipynb`.

## Ferramentas utilizadas

| Ferramenta | Papel no projeto | Custo |
|---|---|---|
| GitHub | Guarda e exibe todo o painel (é o "site" do projeto) | Gratuito |
| NotebookLM (Google) | Lê os PDFs e ajuda a extrair conceitos, resumos, perguntas e trechos | Gratuito |
| Google Colab | Converte PDFs em Markdown em lote e mantém o painel atualizado, no navegador, sem instalar nada | Gratuito |
| Google Drive | Organiza os PDFs originais por tema | Gratuito |
| Anki | Revisão espaçada dos conceitos por flashcards, gerados pelo notebook atualizador | Gratuito |

## Roteiro (roadmap)

- [ ] Criar o repositório no GitHub
- [ ] Organizar os PDFs por tema no Google Drive
- [ ] Converter os 10 livros-chave do primeiro lote (estratégia híbrida — ver Guia 02)
- [ ] Criar as primeiras 20 notas de conceito
- [ ] Preencher a primeira ficha de leitura completa
- [ ] Importar os primeiros flashcards no Anki e estabelecer a rotina de revisão
- [ ] Rodar o notebook atualizador do painel pela primeira vez
- [ ] Processar 50 livros e atualizar o painel de temas
- [ ] (Futuro) Transformar este painel em um site interativo com busca

## Nota sobre direitos autorais

O acervo convertido destina-se a uso pessoal de estudo. Por isso, a recomendação deste projeto é manter o repositório **privado** enquanto ele contiver texto integral de obras protegidas. As notas de conceito e os comentários pessoais são produções próprias e podem ser compartilhados livremente, caso um dia você queira tornar o painel público.
