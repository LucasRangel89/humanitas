# Guia 04 — Atualizar o GitHub no dia a dia

Este guia cobre as quatro operações de manutenção do painel, todas feitas pelo navegador, sem instalar nada. É a rotina do dia a dia depois que o repositório já existe.

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
3. Ajuste o nome (a barra `/` no nome cria ou muda a pasta, por exemplo mover de `acervo/livro.md` para `acervo/fichas/livro.md`).
4. Confirme com **Commit changes**.

## Excluir um arquivo

1. Abra o arquivo.
2. Clique no ícone de **lixeira** à direita (Delete this file).
3. Confirme com **Commit changes**. O arquivo sai do repositório, mas continua recuperável pelo histórico de versões.

## Rotina mensal sugerida

Uma vez por mês, reserve 20 minutos para a manutenção do painel:

- Atualize a tabela **Painel de temas** no `README.md` com as contagens novas (notas e livros por tema).
- Atualize o `indice.json` na pasta `indices/` — ou regenere-o rodando o notebook de conversão, que produz o índice automaticamente.
- Marque no **Roteiro (roadmap)** do README os itens concluídos e escolha o tema foco do mês seguinte.
- Se algo saiu do lugar, use **History** para entender o que mudou — nada se perde no GitHub.

## Nomes e convenções para não se perder

Mantenha o padrão desde o início e o painel se organiza sozinho:

- Livros em `acervo/`: `autor-titulo.md` (minúsculas, hífens, sem acentos).
- Conceitos em `conceitos/`: `tema-conceito.md`, por exemplo `historia-estado-nacao.md`.
- Trechos em `trechos/`: `autor-trecho-curto.md`, por exemplo `carr-fatos-e-interpretacoes.md`.

Se um dia as pastas ficarem grandes demais, é só criar subpastas por tema dentro de `conceitos/` e `trechos/` — a estrutura do projeto já foi desenhada para crescer assim.
