# indices/

O mapa geral do acervo processado.

- `indice.json` é o mapa do acervo: livros convertidos, notas de conceito e trechos, com tema, origem e contagens.
- Ele é gerado automaticamente pelo notebook `notebooks/atualizador-do-painel.ipynb`, que lê o repositório inteiro (o `notebooks/converter-pdfs.ipynb` também o cria para o primeiro lote convertido).
- Sempre que adicionar livros ou notas novas, rode o atualizador — o índice só é confiável quando regenerado, nunca editado à mão.
- A tabela "Painel de temas" do `README.md` é a versão legível deste índice, e também é regenerada pelo atualizador.
