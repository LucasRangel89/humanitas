# Guia 03 — Prompts prontos para o NotebookLM

Copie e cole os prompts abaixo no NotebookLM, um por vez, com o livro desejado selecionado como fonte. Cada prompt foi desenhado para gerar um resultado que se encaixa direto nos templates da pasta `templates/`.

## Como usar bem estes prompts

1. **Um prompt por vez.** Não peça tudo de uma vez; cada resposta merece uma leitura sua e, se necessário, um pedido de ajuste ("refaça só os conceitos 3 e 7, com mais detalhe").
2. **Peça referências.** Todos os prompts já pedem indicação de capítulo/seção. Se a resposta vier sem, insista: "indique de qual capítulo vem cada item".
3. **Selecione a fonte certa.** Para prompts de obra única, deixe selecionado apenas o livro em questão. Para o prompt de conexões, selecione duas ou mais obras.
4. **Trate a resposta como rascunho.** O valor está em você reescrever com as próprias palavras ao colar no template.
5. **Itere sem medo.** Peça "explique como se eu nunca tivesse estudado isso", "dê um exemplo brasileiro", "resuma em uma frase só" — o NotebookLM reformula bem.

---

## Prompt 1 — Ficha de leitura completa (o prompt-mestre)

Uso: com o livro selecionado. Produz a base do `template-livro.md`.

```text
Analise a obra selecionada e preencha uma ficha de leitura completa com os seguintes campos:

1. IDENTIFICAÇÃO: título, autor, ano de publicação original e área de conhecimento.
2. CONTEXTO: em que circunstâncias a obra foi escrita e a qual debate ela responde.
3. PROBLEMA: qual pergunta ou problema o autor tenta resolver.
4. TESE CENTRAL: o argumento principal em no máximo 3 frases.
5. MÉTODO: como o autor constrói o argumento (dados, história, teoria, evidências).
6. RESUMO POR CAPÍTULOS: 3 a 5 frases por capítulo, indicando o número do capítulo.
7. CONCEITOS-CHAVE: 10 a 20 conceitos centrais, cada um com definição em uma frase.
8. CONCLUSÕES: o que o autor conclui e o que isso implica.
9. CRÍTICAS: as objeções mais comuns feitas a esta obra.

Formate a resposta em seções numeradas com títulos. Indique o capítulo de origem sempre que citar um trecho.
```

## Prompt 2 — Mapa de conceitos

Uso: com o livro selecionado. Alimenta o `template-conceito.md`.

```text
Liste os 15 a 25 conceitos centrais da obra selecionada. Para cada conceito, apresente:
1. O nome do conceito como o autor usa;
2. Uma definição clara em UMA frase;
3. O capítulo ou seção onde ele é apresentado;
4. Uma explicação de 2 a 3 frases para alguém que nunca leu o livro;
5. Um exemplo concreto (histórico, social ou do cotidiano) que ilustre o conceito.

Ordene os conceitos do mais fundamental ao mais derivado, como uma trilha de estudo.
```

## Prompt 3 — Trechos essenciais

Uso: com o livro selecionado. Alimenta o `template-trecho.md`.

```text
Selecione os 10 trechos mais importantes da obra selecionada — citações literais que representam o coração do argumento. Para cada trecho:
1. A citação EXATA entre aspas, com o capítulo (e página, se identificável);
2. Uma explicação de 2 a 3 frases sobre por que este trecho importa para a obra;
3. Uma pergunta de estudo que este trecho levanta.

Priorize trechos que resumem a tese, definem conceitos centrais ou provocam reflexão.
```

## Prompt 4 — Perguntas de estudo

Uso: com o livro selecionado. Vai para o final do `template-livro.md`.

```text
Crie 10 perguntas de estudo sobre a obra selecionada, organizadas em três níveis:
- Nível 1 (3 perguntas): compreensão básica dos conceitos;
- Nível 2 (4 perguntas): comparação e aplicação das ideias;
- Nível 3 (3 perguntas): crítica, conexões com outras obras e com o Brasil atual.

Para cada pergunta, indique em qual capítulo encontrar os elementos da resposta e escreva uma resposta-modelo de 2 a 3 frases.
```

## Prompt 5 — Glossário

Uso: com o livro selecionado. Complementa a ficha de leitura.

```text
Monte um glossário da obra selecionada com 15 termos técnicos ou que têm significado específico no contexto do autor. Para cada termo:
1. O termo;
2. O significado no uso comum, em uma frase;
3. O significado ESPECÍFICO que o autor dá ao termo, em uma ou duas frases;
4. O capítulo onde o termo é melhor definido.

Escreva as definições em linguagem simples, como se explicasse para um estudante do ensino médio.
```

## Prompt 6 — Conexões entre obras (o superpoder do NotebookLM)

Uso: com DUAS OU MAIS obras selecionadas no mesmo caderno. Gera material único de aprofundamento.

```text
Compare as obras selecionadas respondendo:
1. Em que ponto as obras CONCORDAM e qual ideia compartilham?
2. Em que ponto elas se CONTRADIZEM, e qual é exatamente o ponto de desacordo?
3. O que cada autor responderia ao outro, se pudesse?
4. Qual obra lê "melhor" qual aspecto da realidade? Dê um exemplo concreto.
5. Que pergunta nenhuma das duas responde satisfatoriamente?

Indique capítulos das duas obras a cada resposta. Formate como um diálogo estruturado entre os autores.
```

## Prompt 7 — Contra-argumentos e críticas

Uso: com o livro selecionado. Excelente para o campo "Críticas" da ficha.

```text
Assuma o papel de um revisor crítico da obra selecionada. Liste:
1. As 5 críticas acadêmicas mais comuns feitas a esta obra ou ao autor;
2. Para cada crítica, o que os defensores do autor respondem;
3. Sua avaliação equilibrada: quais críticas parecem justas e quais parecem caricaturas.

Indique capítulos da obra quando a crítica se referir a trechos específicos.
```

## Prompt 8 — Roteiro de estudo personalizado

Uso: com o livro selecionado.

```text
Crie um roteiro de estudo de 4 semanas para a obra selecionada, assumindo que tenho cerca de 4 horas semanais. Para cada semana indique:
1. Quais capítulos ler e em que ordem;
2. O foco de compreensão da semana (qual ideia dominar);
3. Um exercício prático (resumo, mapa, aplicação a um caso atual);
4. Uma pergunta para autoavaliação ao fim da semana.

Ao final, sugira 2 obras de leitura complementar que dialoguem com esta.
```

## Prompt 9 — Explicação para leigos

Uso: com o livro selecionado, para capítulos ou conceitos difíceis.

```text
Explique a ideia central da obra selecionada como se eu tivesse 15 anos e nunca tivesse estudado o tema. Use:
1. Uma analogia do cotidiano;
2. Um exemplo histórico ou brasileiro concreto;
3. Uma explicação direta em 5 frases;
4. O que NÃO é essa ideia (para evitar confusões comuns).

Depois, explique a mesma ideia no nível de um curso universitário, indicando o vocabulário técnico correto.
```

## Prompt 10 — Plano de aula autoexplicativo

Uso: com o livro selecionado. Ótimo para transformar leitura em material de revisão.

```text
Transforme a obra selecionada em um plano de aula de 1 hora, como se eu fosse o professor. Inclua:
1. O objetivo de aprendizagem em uma frase;
2. A sequência da aula em 5 blocos, com o tempo de cada um;
3. A pergunta que abre a aula e a pergunta que a fecha;
4. Os 3 exemplos que o professor deve usar;
5. O "dever de casa": o que o aluno deve revisar e por quê.

Indique os capítulos de origem de cada bloco.
```

---

## Além dos prompts: dois recursos que valem a ativação

- **Mapa Mental:** no painel do caderno, peça a geração do mapa mental da obra. Ele mostra a estrutura de ideias em árvore e é um ótimo "sumário visual" para abrir cada sessão de estudo. Dá para copiar a estrutura em texto e colar em uma nota.
- **Resumo em Áudio:** gera uma conversa entre duas vozes, em formato de podcast, sobre as fontes do caderno. Ideal para revisar o conteúdo em deslocamentos. Disponível em português.

## O que fazer com cada resposta

| Resposta do prompt | Para onde vai |
|---|---|
| Prompt 1 (ficha) | `templates/template-livro.md` > salvo em `acervo/` |
| Prompt 2 (conceitos) | Um `template-conceito.md` por conceito > salvo em `conceitos/` |
| Prompt 3 (trechos) | Um `template-trecho.md` por trecho > salvo em `trechos/` |
| Prompts 4, 5, 7 (perguntas, glossário, críticas) | Campos finais do `template-livro.md` |
| Prompts 6, 8, 9, 10 (conexões, roteiro, leigos, aula) | Notas avulsas em `conceitos/` ou no final da ficha do livro |
