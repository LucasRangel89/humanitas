# conceitos/

A unidade fundamental do painel: uma nota de conceito por arquivo, sempre com a explicação reescrita com as suas palavras.

- Use o modelo `templates/template-conceito.md` para criar cada nota.
- Nome dos arquivos: `tema-conceito.md`, por exemplo `historia-estado-nacao.md` ou `sociologia-habitus.md`.
- Notas com `tipo: eixo` no cabeçalho são notas-bússola: grandes questões que atravessam disciplinas (veja `templates/template-eixo.md`). Elas vivem aqui junto dos conceitos comuns.
- O campo `nivel` (iniciante, entusiasta, avancado) registra para quem a nota foi escrita — o Modo Tutor e as trilhas usam esse campo.
- As notas marcadas como `status: rascunho` são sementes a reescrever com suas palavras; ao reescrever, mude o status para `ok`.
- Quando o número de notas crescer, organize em subpastas por tema: `conceitos/historia/`, `conceitos/sociologia/` e assim por diante.
- Conceitos relacionados devem se linkar com links Markdown padrão: `[texto](nome-do-arquivo.md)`, apontando para o nome exato do arquivo. Assim o link funciona como clique no GitHub e como conexão no Obsidian. A sintaxe `[[nome-da-nota]]` não vira link no GitHub — evite. O notebook `atualizador-do-painel.ipynb` audita esses links e avisa se algum estiver quebrado.
