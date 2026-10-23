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
| `trilhas/` | Trilhas de aprendizado — caminhos ordenados do básico ao avançado (Modo Trilha). Já vêm prontas: Psicologia Níveis 1 e 2, Filosofia, Sociologia e a Integrada (as três lentes juntas) |
| `diario/` | Diário de bordo — sínteses reflexivas escritas por você ao fechar cada módulo de estudo |
| `indices/` | `indice.json` — o mapa geral do acervo processado |
| `templates/` | Modelos prontos para copiar ao criar uma nota nova |
| `docs/` | Guias passo a passo (01 a 09): criar o repositório, extrair conteúdo dos PDFs, usar prompts no NotebookLM, atualizar tudo, priorizar leituras, manter o CI e planejar a expansão para outras humanidades |
| `notebooks/` | Notebooks do Google Colab (sem digitar código): `converter-pdfs` transforma PDFs em Markdown |

## Painel de temas

Este é o mapa dos estudos. Conforme o acervo for processado, os itens abaixo viram links clicáveis para as notas de cada tema. Esta tabela é regenerada automaticamente por `make painel` — não edite à mão. Rode `make painel` e commite; o CI cobra se estiver desatualizada.

<!-- PAINEL-TEMAS-INICIO -->

| Tema | Status | Notas de conceito | Livros processados | Fichas | Trilhas |
|---|---|---|---|---|---|
| História | Ativo | 7 | 0 | 0 | 1 |
| Sociologia | Ativo | 20 | 0 | 0 | 1 |
| Filosofia | Ativo | 15 | 0 | 0 | 1 |
| Antropologia | Ativo | 7 | 0 | 0 | 1 |
| Psicologia | Ativo | 15 | 0 | 0 | 2 |
| Integrada | Ativo | 0 | 0 | 0 | 1 |

> **Planejados (sem conteúdo ainda):** Ciência Política, Economia, Geografia, Psicologia Social. Critério de entrada e ordem de estudo no Guia 09 (`docs/09-mapa-das-humanidades.md`).

<!-- PAINEL-TEMAS-FIM -->

Os temas marcados como "Em breve" já fazem parte da missão do painel — não são uma
novidade, são a parte do mapa que ainda não foi estudada. O plano de expansão (quais
humanidades entram, com que critério, em que ordem e por quê) está no
[Guia 09](docs/09-mapa-das-humanidades.md).

## Meta desta semana

Edite esta linha toda semana (o atualizador do painel não mexe nela): _ex.: nós 1 a 3 da trilha de Filosofia (Teoria das Formas, Eudaimonia, Eixo Mente × Corpo), com quiz e diário_.

## Trilhas prontas para começar

O painel nasce com sete trilhas semente: cinco montadas a partir dos planos de estudo anexados pelo autor (arquivados em `docs/anexos/`) e duas abertas pela expansão para as demais humanidades (Guia 09):

| Trilha | Em uma frase |
|---|---|
| [Psicologia Nível 1](trilhas/psicologia-nivel-1.md) | As seis escolas clássicas navegadas pelos três eixos, terminando na lente sócio-antropológica |
| [Psicologia Nível 2](trilhas/psicologia-nivel-2.md) | Do laboratório à vida: cognição, desenvolvimento, personalidade, saúde mental e psicologia digital |
| [Filosofia Nível 1](trilhas/filosofia-nivel-1.md) | Do mito ao século XX — dos gregos a Rawls, um conceito-fundador por época |
| [Sociologia Nível 1](trilhas/sociologia-nivel-1.md) | Do olhar sociológico de Mills aos clássicos, desigualdade e o mundo digital |
| [Integrada Nível 1](trilhas/integrada-nivel-1.md) | As três lentes juntas (três rotas): a Confluência Humano-Tecnológica, os três módulos temáticos e o curso completo de 5 módulos "Mente, Sociedade e Existência" |
| [Antropologia Nível 1](trilhas/antropologia-nivel-1.md) | Estranhar o familiar: da alteridade ao eixo Natureza × Cultura, passando pelo método etnográfico |
| [História Nível 1](trilhas/historia-nivel-1.md) | Do documento ao tempo longo: o ofício do historiador aplicado à formação do Brasil |

A lista de leituras que sustenta as trilhas está no [Guia 05](docs/05-prioridades-de-leitura.md) — os 10 livros-chave definidos a partir dos planos anexados. As leituras de Antropologia e História estão no [Guia 09](docs/09-mapa-das-humanidades.md) (§4.1).

## Como adicionar um livro novo (resumo rápido)

O fluxo completo está explicado em `docs/02-fluxo-de-extracao.md`, mas em resumo são cinco passos:

1. **Converter** o PDF em Markdown usando o notebook `notebooks/converter-pdfs.ipynb` (Google Colab, funciona no navegador).
2. **Explorar** a obra no NotebookLM usando os prompts prontos de `docs/03-prompts-notebooklm.md`.
3. **Anotar** os resultados usando os modelos da pasta `templates/`.
4. **Publicar** os arquivos aqui no GitHub (guia em `docs/01-criar-repositorio-no-github.md` e `docs/04-atualizar-o-github.md`).
5. **Regenerar** o índice, a tabela de temas e os flashcards com `make painel` e commitar — o CI cobra se estiver desatualizado.

## Ferramentas utilizadas

| Ferramenta | Papel no projeto | Custo |
|---|---|---|
| GitHub | Guarda e exibe todo o painel (é o "site" do projeto) | Gratuito |
| NotebookLM (Google) | Lê os PDFs e ajuda a extrair conceitos, resumos, perguntas e trechos | Gratuito |
| Google Colab | Converte PDFs em Markdown em lote e mantém o painel atualizado, no navegador, sem instalar nada | Gratuito |
| Google Drive | Organiza os PDFs originais por tema | Gratuito |
| Anki | Revisão espaçada dos conceitos por flashcards, gerados por `make painel` | Gratuito |
| Assistente de IA (GLM, Gemini, Claude) | Modo Tutor: gera módulos de aprendizado com resumo, fontes, conexões e quiz (Guia 03) | Gratuito |

## Roteiro (roadmap)

O progresso atualizado está em [`progresso.md`](progresso.md) (gerado automaticamente) e o plano de trabalho vigente no [Guia 07](docs/07-rumos-e-proximos-passos.md).

## Nota sobre direitos autorais

O acervo convertido destina-se a uso pessoal de estudo. Por isso, a recomendação deste projeto é manter o repositório **privado** enquanto ele contiver texto integral de obras protegidas. As notas de conceito e os comentários pessoais são produções próprias e podem ser compartilhados livremente, caso um dia você queira tornar o painel público.
