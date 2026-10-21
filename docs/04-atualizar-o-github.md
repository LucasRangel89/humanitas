# Guia 04 — Atualizar o GitHub no dia a dia

Este guia cobre as operações do dia a dia: adicionar, editar, renomear e excluir arquivos pelo navegador — e como o índice e o progresso se mantêm atualizados sozinhos. Continua sem instalar nada; a manutenção automática está no [Guia 06](06-manutencao-e-ci.md).

## Adicionar arquivos novos (notas, fichas, livros convertidos)

1. Abra a página do repositório no GitHub.
2. Clique em **Add file > Upload files**.
3. Arraste os arquivos (ou uma pasta inteira, usando Chrome/Edge) para a área de upload.
4. Escreva uma mensagem curta descrevendo o que está entrando, por exemplo: "notas de conceitos de A Ética Protestante" — e clique em **Commit changes**.

Dica: se os arquivos precisam entrar dentro de uma pasta específica (por exemplo, novos conceitos em `conceitos/`), arraste a pasta correspondente, ou renomeie os arquivos no seu computador com o caminho no nome antes de subir. O jeito mais simples é arrastar a pasta inteira, que mantém o destino.

## Editar um arquivo que já existe

1. Navegue até o arquivo e clique nele.
2. Clique no ícone de **lápis** (Edit this file) no canto direito.
3. Faça a alteração. À esquerda há uma aba **Preview** para conferir a formatação antes de salvar.
4. Clique em **Commit changes** e confirme. O GitHub guarda o histórico: em **History** você vê todas as versões anteriores do arquivo e pode restaurar qualquer uma se se arrepender.

## Renomear ou mover um arquivo

1. Abra o arquivo e clique no ícone de **lápis** para editar.
2. Na barra acima do texto, clique no nome do arquivo: ele se transforma em campo editável.
3. Ajuste o nome (a barra `/` no nome cria ou muda a pasta, por exemplo mover de `acervo/livro.md` para `acervo/fichas/livro-ficha.md`).
4. Confirme com **Commit changes**.

## Excluir um arquivo

1. Abra o arquivo.
2. Clique no ícone de **lixeira** à direita (Delete this file).
3. Confirme com **Commit changes**. O arquivo sai do repositório, mas continua recuperável pelo histórico de versões.

## Rotina: o painel se atualiza sozinho

Depois da limpeza do projeto, **você não precisa mais rodar notebook nenhum** para manter o índice. O fluxo é:

1. Você escreve/edita notas (no GitHub ou na sua máquina) e faz commit.
2. O **CI** roda os testes e a auditoria: link quebrado, `tema` inválido, seção obrigatória ausente ou conceito duplicado deixam o pull request vermelho.
3. Ao entrar em `main`, o workflow **Painel** regenera `indices/indice.json`, a tabela de temas do `README.md`, o `progresso.md` e o `flashcards.csv`, e commita os três primeiros com a mensagem `chore: regenera índice, tabela de temas e progresso [skip ci]`.
4. Para revisar no Anki: **Actions → run mais recente do "Painel" → Artifacts → flashcards**.

Se preferir rodar na sua máquina (Python 3.10+):

```bash
make instalar     # uma vez
make auditar      # links, metadados, duplicados
make painel       # índice + tabela + progresso + flashcards
```

O passo a passo detalhado está no [Guia 06](06-manutencao-e-ci.md).

## O que subir e o que não subir

| Arquivo | Entra no Git? | Por quê |
|---|---|---|
| `conceitos/`, `trilhas/`, `diario/`, `trechos/` | Sim | produção própria (CC BY-SA 4.0) |
| `acervo/fichas/*-ficha.md` | Sim | produção própria |
| `acervo/*.md` (texto integral), PDFs | **Não** | direitos autorais; `.gitignore` bloqueia |
| `indices/indice.json`, `progresso.md`, tabela do README | Sim (automático) | gerados pelo CI |
| `flashcards.csv` | Não (artefato) | gerado; baixe em Actions → Artifacts |

## Nomes e convenções para não se perder

Mantenha o padrão desde o início e o painel se organiza sozinho:

- Fichas em `acervo/fichas/`: `autor-titulo-ficha.md`. O texto integral (`acervo/autor-titulo.md`) fica fora do Git.
- Conceitos em `conceitos/`: `tema-conceito.md`.
- Diário em `diario/`: `AAAA-MM-DD-tema-assunto.md`.
- Trechos em `trechos/`: `autor-trecho-curto.md`, por exemplo `carr-fatos-e-interpretacoes.md`.

Se um dia as pastas ficarem grandes demais, crie subpastas por tema: o CLI lê `conceitos/`, `trilhas/`, `diario/` e `trechos/` recursivamente e registra o caminho completo no índice. Mantenha os links relativos ao arquivo (ex.: `../sociologia-cultura.md`) — a auditoria confere cada um.
