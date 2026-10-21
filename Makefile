# Atalhos de manutenção do painel (Windows: use `python -m scripts.painel ...`).
.PHONY: ajuda instalar testar auditar painel limpar

ajuda:
	@echo "make instalar  - cria .venv e instala as dependências"
	@echo "make testar    - roda os testes"
	@echo "make auditar   - audita links, metadados e duplicados"
	@echo "make painel    - regenera índice, tabela, progresso e flashcards"
	@echo "make limpar    - remove caches locais"

instalar:
	python3 -m venv .venv
	./.venv/bin/pip install -r requirements.txt

testar:
	./.venv/bin/python -m pytest tests -q

auditar:
	./.venv/bin/python -m scripts.painel auditar

painel:
	./.venv/bin/python -m scripts.painel tudo
	@echo "Pronto: README.md, indices/indice.json, progresso.md e flashcards.csv atualizados."

limpar:
	rm -rf .pytest_cache __pycache__ scripts/__pycache__ tests/__pycache__ flashcards.csv
