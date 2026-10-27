# Atalhos de manutenção do painel (Windows: use `python -m scripts.painel ...`).
.PHONY: ajuda instalar testar auditar painel pendencias nova site progresso midias limpar

ajuda:
	@echo "make instalar  - cria .venv e instala as dependências"
	@echo "make testar    - roda os testes"
	@echo "make auditar   - audita links, metadados e duplicados"
	@echo "make painel    - regenera índice, tabela, progresso e flashcards"
	@echo "make pendencias- lista o que falta em cada nota (padrão-ouro)"
	@echo "make nova TIPO=conceito NOME='Habitus' TEMA=sociologia"
	@echo "                 - cria uma nota a partir do template"
	@echo "make site      - monta e serve o site com busca em http://127.0.0.1:8000"
	@echo "make midias    - regenera a biblioteca de mídias (midias.md)"
	@echo "make aplicar-progresso ARQUIVO=progresso.json"
	@echo "                 - grava no repositório o progresso marcado no site"
	@echo "make limpar    - remove caches e artefatos locais"

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

pendencias:
	./.venv/bin/python -m scripts.painel pendencias

# make nova TIPO=conceito NOME="Habitus" TEMA=sociologia
nova:
	./.venv/bin/python -m scripts.painel nova --tipo "$(TIPO)" --nome "$(NOME)" --tema "$(TEMA)"

midias:
	./.venv/bin/python -m scripts.painel midias

# make aplicar-progresso ARQUIVO=progresso.json  (o JSON sai do botão "Exportar" no site)
aplicar-progresso:
	./.venv/bin/python -m scripts.painel aplicar-progresso --arquivo "$(ARQUIVO)"

site:
	./.venv/bin/pip install -q -r requirements-docs.txt
	./.venv/bin/python -m scripts.painel site
	./.venv/bin/mkdocs serve

limpar:
	rm -rf .pytest_cache __pycache__ scripts/__pycache__ tests/__pycache__ \
		flashcards.csv site site-src
