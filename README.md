# Humanitas — painel de estudos de ciências humanas

Base de estudos autodidata que concentra, em um só lugar, os tópicos, conceitos e trechos essenciais de obras de ciências humanas: filosofia, sociologia, psicologia, história, ciência política, antropologia e áreas vizinhas.

## O que é este projeto

Um **painel pessoal de estudos**. Ele nasce de uma biblioteca de PDFs didáticos e se organiza em camadas complementares:

1. **Notas de estudo** — conceitos explicados, trechos comentados, eixos de debate e fichas de leitura, escritos com as suas palavras a partir das obras (com apoio de IA para a parte burocrática).
2. **Trilhas** — caminhos ordenados de estudo, com critério de conclusão verificável e diário de bordo.
3. **Índices e progresso** — o mapa do acervo (`indices/indice.json`), a tabela de temas e o `progresso.md`, todos regenerados automaticamente.
4. **Acervo** — o texto integral dos livros convertido para Markdown, que fica **fora do Git** (direitos autorais) e é consultado localmente/Drive.

A lógica: em vez de reler um PDF de 400 páginas para achar uma ideia, você abre a nota do conceito, o trecho comentado ou a ficha do livro — tudo interligado e organizado por tema e por eixo de debate.

## Como navegar

| Pasta / arquivo | O que você encontra |
|---|---|
| `conceitos/` | Notas de conceito — uma ideia central por arquivo — e as notas de **eixo** (grandes questões que atravessam disciplinas) |
| `trilhas/` | Caminhos de aprendizado do básico ao avançado. Já vêm prontas: Psicologia Níveis 1 e 2, Filosofia, Sociologia e a Integrada |
| `trechos/` | Citações literais sempre acompanhadas de comentário pessoal |
| `diario/` | Diário de bordo — a síntese reflexiva de cada sessão (a IA nunca escreve por você) |
| `acervo/` | **Só fichas de leitura** (`acervo/fichas/`) e o manifesto de conversão; o texto integral fica fora do Git |
| `indices/` | `indice.json` — o mapa geral do acervo, gerado automaticamente |
| `progresso.md` | Nós concluídos, notas reescritas, diários, citações — gerado automaticamente |
| `templates/` | Modelos para copiar ao criar nota, eixo, trilha, ficha, trecho ou diário |
| `docs/` | Guias 01–06 (criar repositório, extrair dos PDFs, prompts, atualizar, prioridades de leitura, manutenção/CI) + a análise do projeto |
| `scripts/` | CLI de manutenção (`python -m scripts.painel ...`) |
| `tests/` | Testes automatizados do CLI |
| `.github/workflows/` | CI (testes + auditoria) e atualização automática do painel |
| `notebooks/` | Notebook do Colab que converte PDFs em Markdown |
| `mkdocs.yml` | Configuração do site com busca (`make site`) |

## Estado atual

<!-- PROGRESSO-INICIO -->

| Indicador | Valor |
|---|---|
| Nós de trilha concluídos | 0 de 56 |
| Notas reescritas (`ok`) | 0 de 36 |
| Entradas de diário | 0 |
| Notas com citação de apoio | 0 de 36 |

Detalhes por trilha e por tema em [`progresso.md`](progresso.md).

<!-- PROGRESSO-FIM -->

> A métrica que importa não é quantidade de notas: é **nota reescrita** (`status: ok`) e **entrada de diário**.

## Painel de temas

Mapa dos estudos. A tabela é regenerada automaticamente pelo CLI — não edite à mão.

<!-- PAINEL-TEMAS-INICIO -->

| Tema | Status | Notas de conceito | Livros processados | Fichas | Trilhas |
|---|---|---|---|---|---|
| História | Em breve | 0 | 0 | 0 | 0 |
| Sociologia | Ativo | 14 | 0 | 0 | 1 |
| Filosofia | Ativo | 11 | 0 | 0 | 1 |
| Ciência Política | Em breve | 0 | 0 | 0 | 0 |
| Antropologia | Em breve | 0 | 0 | 0 | 0 |
| Economia | Em breve | 0 | 0 | 0 | 0 |
| Geografia | Em breve | 0 | 0 | 0 | 0 |
| Psicologia | Ativo | 11 | 0 | 0 | 2 |
| Psicologia Social | Em breve | 0 | 0 | 0 | 0 |
| Integrada | Ativo | 0 | 0 | 0 | 1 |

<!-- PAINEL-TEMAS-FIM -->

## Mantendo o painel (3 comandos)

O painel se mantém sozinho: a cada push em `main`, o GitHub Actions regenera o índice, a tabela de temas, o `progresso.md` e o `flashcards.csv`. Para rodar localmente:

```bash
make instalar                 # cria .venv e instala dependências (uma vez)
make auditar                  # links quebrados, metadados, duplicados, seções ausentes
make pendencias               # o que falta em cada nota para virar padrão-ouro
make nova TIPO=conceito NOME="Habitus" TEMA=sociologia   # esqueleto de nota nova
make painel                   # índice + tabela + progresso + flashcards
make site                     # site com busca em http://127.0.0.1:8000
make testar                   # 51 testes
```

Sem `make` (Windows ou pressa):

```bash
python -m scripts.painel tudo
python -m scripts.painel auditar
```

Nada disso instala nada além de Python 3.10+ e duas bibliotecas leves (`PyYAML` e `pytest`).
O guia completo está em [`docs/06-manutencao-e-ci.md`](docs/06-manutencao-e-ci.md).

## Site com busca

O painel vira site com busca em português, tags e navegação automática:

```bash
make site        # monta site-src/ e serve localmente
```

Só entra no site o que pode ser público: notas, eixos, trilhas, diário, trechos,
fichas e guias. Ficam de fora o texto integral do acervo e `docs/anexos/`.
A publicação no GitHub Pages é **manual** (`Actions → "Site — publicar no GitHub
Pages"`) para nada ficar público sem decisão sua — passo a passo no
[Guia 06](docs/06-manutencao-e-ci.md#site-com-busca-mkdocs-material).

## Meta desta semana

Edite esta linha toda semana (nada automático mexe nela): _ex.: nós 1 a 3 da trilha de Filosofia (Teoria das Formas, Eudaimonia, Eixo Mente × Corpo), com quiz e diário_.

## Trilhas prontas para começar

O painel nasce com cinco trilhas semente, montadas a partir dos planos de estudo do autor (arquivados em `docs/anexos/`):

| Trilha | Em uma frase |
|---|---|
| [Psicologia Nível 1](trilhas/psicologia-nivel-1.md) | As seis escolas clássicas navegadas pelos três eixos, terminando na lente sócio-antropológica |
| [Psicologia Nível 2](trilhas/psicologia-nivel-2.md) | Do laboratório à vida: cognição, desenvolvimento, personalidade, saúde mental e psicologia digital |
| [Filosofia Nível 1](trilhas/filosofia-nivel-1.md) | Do mito ao século XX — dos gregos a Rawls, um conceito-fundador por época |
| [Sociologia Nível 1](trilhas/sociologia-nivel-1.md) | Do olhar sociológico de Mills aos clássicos, desigualdade e o mundo digital |
| [Integrada Nível 1](trilhas/integrada-nivel-1.md) | As três lentes juntas (duas rotas): a Confluência Humano-Tecnológica e os três módulos temáticos |

A lista de leituras que sustenta as trilhas está no [Guia 05](docs/05-prioridades-de-leitura.md) — os 10 livros-chave definidos a partir dos planos anexados.

## Como adicionar um livro novo (resumo rápido)

O fluxo completo está em [`docs/02-fluxo-de-extracao.md`](docs/02-fluxo-de-extracao.md). Em resumo:

1. **Organizar** os PDFs por tema no Google Drive (fora do Git).
2. **Converter** com `notebooks/converter-pdfs.ipynb` no Colab (incremental, com manifesto).
3. **Explorar** a obra no NotebookLM com os prompts de [`docs/03-prompts-notebooklm.md`](docs/03-prompts-notebooklm.md).
4. **Anotar** com os modelos de `templates/` — reescrevendo com as suas palavras e, sempre que possível, com citação e página.
5. **Publicar** e deixar o CI regenerar índice, tabela, progresso e flashcards.

## Ferramentas utilizadas

| Ferramenta | Papel no projeto | Custo |
|---|---|---|
| GitHub + Actions | Guarda o painel e regenera índice/progresso a cada push | Gratuito |
| NotebookLM (Google) | Lê os PDFs e ajuda a extrair conceitos, resumos, perguntas e trechos | Gratuito |
| Google Colab | Converte PDFs em Markdown em lote, no navegador | Gratuito |
| Google Drive | Organiza os PDFs e o texto integral convertido (fora do Git) | Gratuito |
| Anki | Revisão espaçada com os flashcards gerados pelo CLI (GUID estável: reimportar não duplica) | Gratuito |
| Obsidian (opcional) | Abre o repositório como "segundo cérebro" local, com grafo de links | Gratuito |
| Assistente de IA (Modo Tutor) | Gera módulos de aprendizado com quiz e pergunta reflexiva (Guia 03) | Gratuito |

## Roteiro (roadmap)

**Concluído**

- [x] Criar o repositório no GitHub
- [x] Escrever as 36 notas semente e as 5 trilhas
- [x] Trocar os notebooks de manutenção por um CLI testável (`scripts/painel.py`)
- [x] Automação no GitHub Actions (testes, auditoria, índice, progresso, flashcards)
- [x] Limpar duplicatas da raiz, criar `.gitignore` (acervo fora do Git) e licenças
- [x] Medir progresso real (`progresso.md`): notas ok, nós concluídos, diários, citações
- [x] Scaffold de notas (`nova`) e checklist do padrão-ouro (`pendencias`)
- [x] Site com busca em português e tags (MkDocs Material)

**Próximos**

- [ ] Reescrever as 5 primeiras notas no padrão-ouro (fonte primária + citação com capítulo/página) e mudar para `status: ok`
- [ ] Escrever a primeira ficha de leitura (Mills, *A Imaginação Sociológica*)
- [ ] Escrever a primeira entrada do diário de bordo
- [ ] Importar os flashcards no Anki e estabelecer a rotina de revisão
- [ ] Converter o primeiro lote de livros-chave (Guia 05)
- [ ] Percorrer a trilha de Psicologia Nível 1 até o nó 12
- [ ] Habilitar o GitHub Pages e publicar o site (Settings → Pages → GitHub Actions)
- [ ] Usar `make nova` e `make pendencias` para fechar as 5 primeiras notas
- [ ] (Futuro) Busca semântica e quiz gerados sobre as **suas** notas, com citação obrigatória

## Direitos autorais e licenças

- **Texto integral de obras**: uso pessoal de estudo, **fora do Git** (o `.gitignore` bloqueia `acervo/*.md`). Se você optar por versionar o texto integral, mantenha o repositório **privado**.
- **Notas, trilhas, eixos, diário e fichas** (produção própria): [CC BY-SA 4.0](LICENSE-CONTEUDO.md) — podem ser compartilhadas com atribuição.
- **Código** (`scripts/`, `tests/`, workflows, notebooks): [MIT](LICENSE).
- **`docs/anexos/`** (planos de estudo, grade curricular, `.docx`): materiais de terceiros, não cobertos pelas licenças acima.

Análise crítica do projeto (pontos fortes, riscos, correções e rumos): [`docs/analise-do-projeto.md`](docs/analise-do-projeto.md).
