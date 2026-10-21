# acervo/

Esta pasta guarda o material das obras — mas **só as fichas de leitura entram no Git**.

## O que é versionado

- `acervo/fichas/` — as fichas de leitura (modelo `templates/template-livro.md`),
  nomeadas `autor-titulo-ficha.md`. São produção própria e podem ser compartilhadas.
- `acervo/manifesto.json` — controle de quais PDFs já foram convertidos e o hash de
  cada um (permite reconverter só o que mudou).
- Este `README.md`.

## O que NÃO é versionado

- O **texto integral** convertido (`acervo/autor-titulo.md`) e os PDFs originais.
  O `.gitignore` já bloqueia esses arquivos. Motivo: direitos autorais — o texto
  integral é para uso pessoal de estudo e fica no Google Drive.

## Como converter

1. Use o notebook [`notebooks/converter-pdfs.ipynb`](../notebooks/converter-pdfs.ipynb)
   (Colab), com os PDFs organizados por tema no Drive (`Estudos-PDFs/<tema>/`).
2. Guarde os `.md` gerados onde preferir (Drive ou máquina local) — **não** no Git.
3. As notas de conceito, eixos, trechos e fichas é que entram no repositório.

O índice é regenerado pelo CLI/GitHub Actions e lê o tema das fichas; para o texto
integral, o tema vem do `manifesto.json`.

Passo a passo completo: [`docs/02-fluxo-de-extracao.md`](../docs/02-fluxo-de-extracao.md).
