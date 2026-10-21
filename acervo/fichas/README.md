# acervo/fichas/

As fichas de leitura — a **única parte do acervo que entra no Git**, porque é produção própria.

- Um arquivo por obra, nomeado `autor-titulo-ficha.md` (minúsculas, sem acentos).
- Modelo: [`templates/template-livro.md`](../../templates/template-livro.md).
- O sufixo `-ficha.md` não é decorativo: é por ele que o CLI reconhece uma ficha
  (e não texto integral) e a inclui no índice, na tabela de temas e no progresso.
- O texto integral do livro **não** vai para cá: fica no Drive/máquina local e o
  `.gitignore` bloqueia `acervo/*.md`. Veja [`acervo/README.md`](../README.md).

A ficha é onde a obra inteira aparece condensada: contexto, problema, tese,
resumo por capítulos, conceitos-chave, trechos, críticas e a sua avaliação.
É também o lugar natural para registrar os **conceitos que ainda viram nota**.
