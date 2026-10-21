# conceitos/

A unidade fundamental do painel: uma nota de conceito por arquivo, sempre com a explicação reescrita com as suas palavras.

- Use o modelo `templates/template-conceito.md` para criar cada nota.
- Nome dos arquivos: `tema-conceito.md`, por exemplo `historia-estado-nacao.md` ou `sociologia-habitus.md`.
- Quando o número de notas crescer, organize em subpastas por tema: `conceitos/historia/`, `conceitos/sociologia/` e assim por diante.
- Conceitos relacionados devem se linkar com links Markdown padrão: `[texto](nome-do-arquivo.md)`, apontando para o nome exato do arquivo. Assim o link funciona como clique no GitHub e como conexão no Obsidian. A sintaxe `[[nome-da-nota]]` não vira link no GitHub — evite. O notebook `atualizador-do-painel.ipynb` audita esses links e avisa se algum estiver quebrado.
