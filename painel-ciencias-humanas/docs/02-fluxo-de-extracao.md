# Guia 02 — Fluxo de extração: dos PDFs ao painel de estudos

Este é o guia central do projeto. Ele responde à pergunta que originou tudo: **como transformar uma estante de PDFs didáticos em um painel de conceitos, trechos e ideias organizadas?** O fluxo foi desenhado para quem não programa: todas as etapas acontecem no navegador, e as partes repetitivas ficam por conta de ferramentas gratuitas do Google.

## Visão geral do fluxo

O caminho de um livro, da estante ao painel, tem cinco etapas:

1. **Organizar** — os PDFs ficam agrupados por tema no Google Drive, com nomes padronizados.
2. **Converter** — um notebook do Google Colab transforma os PDFs em Markdown em lote (isto é, vários de uma vez, sozinho).
3. **Explorar** — o NotebookLM lê as obras e, com os prompts prontos do Guia 03, devolve conceitos, resumos, trechos e perguntas de estudo.
4. **Anotar** — você copia esses resultados para os modelos da pasta `templates/`, adicionando o seu comentário pessoal (a parte mais valiosa).
5. **Publicar** — os arquivos sobem para o GitHub e entram no índice do painel.

Uma observação importante sobre a divisão do trabalho: a IA não substitui a sua leitura — ela elimina a parte burocrática (achar a página, reescrever, formatar). O que sobra para você é o que realmente fixa o aprendizado: decidir o que importa e comentar com as próprias palavras.

## Etapa 0 — Organizar os PDFs no Google Drive

Antes de qualquer conversão, vale dez minutos de arrumação que economizam horas depois.

1. No Google Drive, crie uma pasta principal, por exemplo `Estudos-PDFs`.
2. Dentro dela, crie uma subpasta por tema: `historia`, `sociologia`, `filosofia`, `ciencia-politica` e assim por diante.
3. Distribua os PDFs nessas subpastas.
4. Padronize os nomes dos arquivos no formato **`Autor - Titulo.pdf`**, sem acentos. Exemplos: `carr - o que e historia.pdf`, `bourdieu - a reproducao.pdf`. O nome do arquivo é o que aparecerá no índice do painel, então capriche.

Se a coleção for grande (o seu caso, com mais de cem PDFs), não tente arrumar tudo antes de começar. Organize apenas o primeiro lote de 5 a 10 livros e já siga para as próximas etapas — o resto da arrumação acontece em paralelo, lote a lote.

## Etapa 1 — Converter os PDFs em Markdown (Google Colab)

Por que converter, e não usar os PDFs diretamente? Porque o Markdown é o formato que o GitHub exibe de forma bonita, que se pesquisa inteiro com Ctrl+F, que se abre em qualquer aparelho e que nunca fica desalinhado. É a base de tudo o que vem depois.

A conversão usa o arquivo `notebooks/converter-pdfs.ipynb` deste repositório, no **Google Colab** — um ambiente que roda código no navegador do Google, sem instalar nada no seu computador. O modo de usar é simples:

1. Acesse `colab.research.google.com` e faça login com sua conta Google.
2. Clique em **Arquivo > Fazer upload de notebook** e selecione `notebooks/converter-pdfs.ipynb`.
3. Leia as células (os "blocos" do notebook): cada uma tem uma explicação em português antes do código.
4. Execute as células em ordem, clicando no botão de play à esquerda de cada uma. Não é preciso digitar nem editar código, exceto em um ponto único e sinalizado: o endereço da pasta do Drive.
5. No final, o notebook gera um arquivo zip com todos os Markdowns e um `indice.json` pronto.

Duas maneiras de entregar os PDFs ao notebook (o próprio notebook oferece as duas):

- **Opção A — Enviar do computador:** aparece uma janela para selecionar os arquivos. Funciona bem para até uns 20 PDFs.
- **Opção B — Ler do Google Drive (recomendada para 100+):** o notebook pede permissão para acessar seu Drive, e você só informa o nome da pasta `Estudos-PDFs`. Aí ele processa tudo de uma vez, incluindo subpastas por tema.

O que fazer com os problemas mais comuns está no final deste guia (seção "PDFs escaneados").

## Etapa 2 — Explorar as obras no NotebookLM

O **NotebookLM** (em `notebooklm.google.com`) é a ferramenta de leitura assistida do Google. Você entrega fontes (os PDFs) e conversa com elas: pede resumos, conceitos, comparações, perguntas — sempre com resposta ancorada no texto das fontes, com referência ao trecho original. Isso reduz muito o risco de invenção, que é a grande fraude das IAs de chat comuns.

Maneiras de explorar o acervo com ele:

- **Um caderno por tema.** Crie um caderno "História", outro "Sociologia" etc. O plano gratuito permite até 50 fontes por caderno, o que cobre bem um tema por vez.
- **Um livro por vez dentro do tema.** Para os prompts de ficha e de conceitos, selecione apenas o livro em questão como fonte ativa, para não misturar as respostas.
- **Vários livros juntos para comparações.** Este é o superpoder do NotebookLM: com duas ou mais obras selecionadas, é possível pedir "compare o que as fontes dizem sobre X" — algo impossível de fazer com um PDF isolado.
- **Prompts prontos.** O `docs/03-prompts-notebooklm.md` traz dez prompts testados e prontos para copiar e colar, cobrindo ficha de leitura, conceitos, trechos essenciais, perguntas, glossário e críticas.
- **Recursos extras que valem muito:** o **Mapa Mental** (a IA desenha a estrutura de ideias do livro) e o **Resumo em áudio** (gera uma conversa em podcast sobre a obra, ótima para revisar andando ou dirigindo).

O resultado de cada prompt é copiado para os templates da etapa seguinte. Não tente guardar tudo: o critério é "isto me ajudaria a lembrar dessa ideia daqui a dois anos?".

## Etapa 3 — Produzir as notas (a parte mais importante)

Aqui o material bruto vira conhecimento organizado, usando três modelos da pasta `templates/`:

- **`template-livro.md`** — a ficha de leitura: tese central, resumo por capítulos, conceitos-chave e perguntas. Um arquivo por livro, salvo em `acervo/fichas/` (ou no próprio `acervo/`, ao lado do texto integral).
- **`template-conceito.md`** — a unidade fundamental do painel. Um conceito por arquivo, com definição em uma frase, explicação com suas palavras, trecho de apoio e conceitos relacionados. Salvo em `conceitos/`.
- **`template-trecho.md`** — para citações literais que você quer guardar, sempre com o comentário "por que guardei este trecho". Salvo em `trechos/`.

Duas regras de ouro desta etapa:

1. **Reescreva com suas palavras.** Copiar e colar a resposta da IA não gera aprendizado; parafrasear sim. O campo de comentário pessoal é o coração de cada nota.
2. **Um conceito, um arquivo.** É tentador fazer um único arquivo gigante por livro, mas notas pequenas e específicas é o que permite conectar, buscar e reaproveitar depois.

## Etapa 4 — Publicar e manter o índice

Com as notas prontas, suba os arquivos para o GitHub (Guia 04) e atualize o `indice.json` rodando a última célula do notebook, ou manualmente adicionando uma linha por livro novo. Atualize também a tabela "Painel de temas" do `README.md` — ela é a fachada do painel.

## Outras maneiras de explorar o acervo (além do NotebookLM)

O fluxo principal já cobre o essencial, mas existem caminhos complementares. Esta comparação honesta ajuda a escolher quando usar cada um:

| Ferramenta | O que faz de melhor | Limitações | Quando usar |
|---|---|---|---|
| **NotebookLM** | Respostas ancoradas nas fontes, com referência de trecho; mapa mental; resumo em áudio; compara várias obras do mesmo tema | Limite de 50 fontes por caderno (grátis); exportar exige copiar e colar | Exploração rotineira de todo o acervo — é o motor do projeto |
| **Conversa direta com IA** (GLM, Claude, ChatGPT) | Raciocínio mais profundo por obra; aceita o PDF anexado e conversas longas e sofisticadas sobre o texto | Um livro por conversa; sem memória entre conversas; respostas não são ancoradas com referências como no NotebookLM | Análise profunda de um livro difícil; discutir críticas e contra-argumentos |
| **Obsidian** (aplicativo gratuito) | Abre exatamente os arquivos Markdown deste repositório como um "segundo cérebro" local, com busca poderosa e grafo visual de conexões entre conceitos | É mais um lugar de leitura do que de extração; exige instalar um programa | Opcional: se você quiser um "modo offline" do painel no computador |
| **Zotero** (gratuito) | Organiza a biblioteca de PDFs em si, com metadados (autor, ano, editora) e extração dos seus grifos feitos no leitor de PDF | Mais um sistema para aprender a usar; não extrai conceitos | Opcional: se a biblioteca de PDFs estiver fora de controle |
| **Leitura com OCR no Google Drive** | Converte PDFs escaneados em texto selecionável ("Abrir com Documentos Google") | Demora e perde formatação; só vale para resgatar livros problemáticos | Apenas quando o notebook avisar que um PDF não tem texto extraível |

O que este projeto **não** recomenda no momento: pagar por ferramentas de "resumo de PDF" (o conjunto gratuito acima já cobre), e tentar extrair o acervo inteiro de uma vez (o ritmo por lotes é mais sustentável e evita acúmulo de material mal revisado).

## PDFs escaneados: o problema mais comum (e a solução)

Uma parte dos PDFs didáticos é, na verdade, uma **fotografia das páginas** — não há texto selecionável. O notebook de conversão avisa quando isso acontece ("SEM TEXTO — provavelmente escaneado"). Duas soluções:

1. **Deixar o NotebookLM ler:** ele processa PDFs escaneados internamente, inclusive em português. Se o objetivo é explorar a obra (e não converter o texto integral), basta subir o PDF original lá e seguir com os prompts.
2. **Resgatar o texto pelo Google Drive:** suba o PDF no Drive, clique com o botão direito, escolha **Abrir com > Documentos Google**. O Google aplica OCR (reconhecimento de texto sobre imagem) e gera um documento editável. Depois é só baixar como texto e tratar como os demais.

## Ritmo sugerido

Consistência vence volume. Um ciclo realista para quem estuda além do trabalho:

- **Por semana:** 1 livro processado de ponta a ponta (converter, 3 a 4 prompts no NotebookLM, 5 a 10 notas, publicar).
- **Por lote:** trabalhe com 5 a 10 livros por vez entre as etapas de conversão e exploração.
- **Por mês:** revise o painel de temas e o índice; escolha um tema "focado" do mês para aprofundar com comparações entre obras no NotebookLM.

Com esse ritmo, em seis meses o painel terá entre 25 e 50 obras processadas e algumas centenas de conceitos organizados — o que já é uma base de estudos de nível universitário.
