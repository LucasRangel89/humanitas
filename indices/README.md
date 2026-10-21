# indices/

O mapa geral do acervo processado.

- `indice.json` é o mapa do painel: livros, fichas, conceitos, eixos, trechos, trilhas e diário, com tema, origem, caminho e contagens.
- Ele é gerado automaticamente pelo CLI `scripts/painel.py` (comando `indice`), que lê o repositório inteiro — localmente ou no GitHub Actions. O notebook de conversão **não** escreve mais índice: isso já apagou dados no passado e hoje há teste de regressão.
- **Nunca edite o `indice.json` à mão.** Rode `python -m scripts.painel indice` (ou `make painel`) e commite o resultado; no CI isso acontece sozinho a cada push em `main`.
- A tabela "Painel de temas" do `README.md` e o `progresso.md` são as versões legíveis deste índice, também regeneradas pelo CLI.

Estrutura do arquivo:

```json
{
  "projeto": "humanitas",
  "atualizado_em": "2026-10-21T19:30:00",
  "totais": { "livros": 0, "fichas": 0, "conceitos": 31, "eixos": 5,
              "trechos": 0, "trilhas": 5, "diario": 0 },
  "livros": [], "fichas": [], "conceitos": [], "trechos": [], "trilhas": [], "diario": []
}
```
