# notebooks/

Notebooks do Google Colab — só os que ainda têm função.

| Notebook | Papel | Precisa do Colab? |
|---|---|---|
| [`converter-pdfs.ipynb`](converter-pdfs.ipynb) | Converte PDFs em Markdown e gera o `manifesto.json` (só reconverte o que mudou). Não gera mais índice. | Sim (upload/Drive) |

## O que saiu daqui

O antigo `atualizador-do-painel.ipynb` foi **substituído pelo CLI** [`scripts/painel.py`](../scripts/painel.py),
porque o ciclo antigo (baixar ZIP → subir no Colab → executar → baixar ZIP → arrastar arquivos)
tinha quatro pontos de falha e podia apagar dados do índice.

Hoje a manutenção é automática: a cada push em `main`, o workflow
[`painel.yml`](../.github/workflows/painel.yml) regenera `indices/indice.json`,
a tabela do README, `progresso.md` e `flashcards.csv` (este último fica como artefato
do workflow). Se quiser rodar na sua máquina:

```bash
python -m scripts.painel tudo    # índice + tabela + progresso + flashcards
python -m scripts.painel auditar # verifica links, metadados e duplicados
```

Veja [`docs/06-manutencao-e-ci.md`](../docs/06-manutencao-e-ci.md).
