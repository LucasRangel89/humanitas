# Guia 06 — Manutenção: o CLI do painel e o CI

Este guia substitui a parte do Guia 04 que dependia do notebook `atualizador-do-painel.ipynb`.
Hoje a manutenção do painel tem **um único dono**: o CLI `scripts/painel.py`. Ele é
testável, roda no GitHub Actions e não depende de Colab, zip nem upload manual.

## O que o CLI faz

```bash
python -m scripts.painel indice      # regenera indices/indice.json (schema completo)
python -m scripts.painel tabela      # regenera a tabela "Painel de temas" do README
python -m scripts.painel progresso   # regenera progresso.md + bloco de progresso do README
python -m scripts.painel flashcards  # gera flashcards.csv com GUID estável (Anki)
python -m scripts.painel auditar     # links, metadados, duplicados, órfãs, seções ausentes
python -m scripts.painel tudo        # índice + tabela + progresso + flashcards
```

Opções:

- `--raiz CAMINHO` — aponta para outro repositório (útil em teste).
- `--estrito` — no comando `auditar`, tratar avisos como erro.

### O que a auditoria verifica

| Categoria | Bloqueia o CI? |
|---|---|
| Link relativo quebrado (em `conceitos/`, `trechos/`, `trilhas/`, `diario/`, `acervo/`, `docs/` e `README.md`) | Sim |
| Wikilink `[[assim]]` (não vira link no GitHub) | Sim |
| `tema`, `tipo`, `nivel` ou `status` inválido/ausente | Sim |
| Seção obrigatória ausente ou vazia | Sim |
| Nota sem definição em uma frase (flashcard sairia vazio) | Sim |
| Conceitos duplicados (mesmo nome) | Sim |
| Conceitos parecidos (≥ 90% de similaridade) | Não (aviso) |
| Notas não citadas em nenhuma trilha | Não (aviso) |
| Notas sem `Trecho de apoio` (padrão-ouro pede citação com página) | Não (aviso) |
| Notas com fonte secundária (guia/planos) | Não (aviso) |
| Arquivos em `acervo/` (risco de direitos autorais) | Não (aviso) |

Os *avisos* são o retrato da dívida de estudo: quantidade de rascunhos, citações
faltando e fontes secundárias a substituir. Eles não quebram o build, mas aparecem
na saída do CI e no `progresso.md`.

## O índice tem um único dono

O `indices/indice.json` **só** é escrito pelo CLI. O notebook de conversão de PDFs
não escreve mais índice — essa era a origem de um bug real: o conversor gravava um
índice contendo apenas `livros` e, ao subir para `indices/`, apagava `conceitos`,
`trechos` e `fichas`. Há um teste de regressão que impede o retorno do problema:

```bash
python -m pytest tests -q -k conversor
```

## Automação no GitHub Actions

Dois workflows:

| Workflow | Quando roda | O que faz |
|---|---|---|
| `.github/workflows/ci.yml` | Todo push e pull request | Roda os testes, a auditoria e confere se índice/progresso/tabela estão atualizados |
| `.github/workflows/painel.yml` | Push em `main` (pastas de conteúdo) ou manual | Regenera índice, tabela, progresso e flashcards; commita os três primeiros; publica `flashcards.csv` como artefato |

Fluxo diário, na prática:

1. Você escreve/edita notas e dá commit.
2. O CI roda os testes e a auditoria (se algo quebrar, o PR fica vermelho).
3. Ao entrar em `main`, o painel regenera os artefatos e commita sozinho
   (`chore: regenera índice, tabela de temas e progresso [skip ci]`).
4. Você baixa o `flashcards.csv` em **Actions → último run do "Painel" → Artifacts**.

## Rodando na sua máquina

Requisitos: Python 3.10+ (o CI usa 3.12).

```bash
make instalar      # cria .venv e instala requirements.txt
make testar
make auditar
make painel
```

Sem `make`:

```bash
python3 -m venv .venv
./.venv/bin/pip install -r requirements.txt
./.venv/bin/python -m pytest tests -q
./.venv/bin/python -m scripts.painel tudo
```

## Flashcards no Anki

O CSV gerado tem cinco colunas: `guid`, `frente`, `verso`, `tags`, `baralho`.

- **O `guid` é estável** (derivado do nome do conceito, não do arquivo): reimportar
  atualiza o cartão em vez de duplicar.
- **Baralho**: `Humanitas::<Tema>`.
- **Tags**: `humanitas`, o tema e até três tags da nota.
- **Tipos de cartão**: definição (todos), aplicação (conceitos com "Exemplos que ilustram")
  e posicionamento no eixo (eixos, a partir da tabela "Posições no debate").

No Anki: **Arquivo → Importar**, marque a coluna 1 como *GUID*, a 2 como *Frente*,
a 3 como *Verso*, a 4 como *Tags* e a 5 como *Baralho*. Recomenda-se o agendador
**FSRS** (nativo nas versões recentes).

## Convenções de conteúdo validadas pelo CI

- `tema`: um de `historia`, `sociologia`, `filosofia`, `ciencia-politica`,
  `antropologia`, `economia`, `geografia`, `psicologia`, `psicologia-social`, `integrada`.
- `status`: `rascunho`, `ok`, `arquivada` (notas) ou `em-andamento`, `concluida`,
  `pausada` (trilhas).
- `nivel`: `iniciante`, `entusiasta`, `avancado`.
- Seções obrigatórias: veja `SECOES_OBRIGATORIAS` em `scripts/painel.py` e a
  checklist no `templates/template-conceito.md`.

## Estrutura do CLI

```
scripts/painel.py
├── parsing (frontmatter, seções, normalização)
├── coleta (conceitos, livros, fichas, trechos, trilhas, diário)
├── geração (índice, tabela de temas, progresso, flashcards)
├── auditoria (links, metadados, duplicados, órfãs)
└── comandos (indice, tabela, progresso, flashcards, auditar, tudo)
tests/
├── conftest.py   (mini-repositório válido como fixture)
└── test_painel.py (33 testes: parsing, auditoria, índice, progresso, flashcards)
```
