# Guia 10 — O ritual de estudo: como transformar uma leitura em nota `ok`

> **Para que serve este guia:** o painel já tem 87 notas e **0 reescritas**. Toda a
> infraestrutura está paga; o que falta é o trabalho que não se automatiza. Este guia é
> o procedimento operacional desse trabalho — 90 minutos por sessão, uma nota por vez.
> Ele não substitui o [Guia 07](07-rumos-e-proximos-passos.md) (que decide *o que*
> estudar); ele resolve *como*.

## Em cinco linhas

1. Uma nota só vira `ok` quando passa em cinco testes: definição de cartão, explicação
   sua, citação com página, exemplo brasileiro e conexão interdisciplinar.
2. A sessão tem 90 minutos e cinco blocos cronometrados — sem consultar a IA no bloco de
   escrita, que é onde o aprendizado acontece.
3. O critério de "terminei" não é "entendi": é `make pendencias` sem pendências e
   `make auditar` sem erro naquela nota.
4. A IA ajuda antes (organizar, perguntar, localizar passagem) e depois (conferir o que
   você esqueceu). Nunca durante.
5. O produto da sessão não é a nota: é a nota **e** a entrada de diário. A nota é o
   espelho; o diário é a impressão digital.

---

## 1. O que é uma nota `ok` (os cinco testes)

O `status` no frontmatter não é decoração: o `progresso.md` e os marcos do Guia 07 contam
só `ok`. Para mudar de `rascunho` para `ok`, a nota precisa passar nos cinco testes:

| # | Teste | Critério objetivo | Como o CLI verifica |
|---|---|---|---|
| 1 | **Definição de cartão** | cabe em um flashcard, 1 frase, sem "e também" | `pendencias` → "definição em uma frase" |
| 2 | **Explicação** | 3 a 5 frases **suas**, com um exemplo concreto | `pendencias` → "explicação com as suas palavras" |
| 3 | **Citação** | trecho literal **com capítulo e página** (ou a frase "Sem citação — fonte secundária") | `auditar` + `pendencias` → "citação de apoio" |
| 4 | **Exemplo brasileiro** | um caso seu, do seu bairro, trabalho ou notícia | `pendencias` → "exemplo próprio (de preferência brasileiro)" |
| 5 | **Conexão** | uma ligação com outro tema **e o porquê** dela | revisão manual (o CLI não julga qualidade) |

E dois campos do frontmatter, que a auditoria cobra:

- `fonte_verificada: sim` — você conferiu a obra primária (não o resumo de site);
- `status: ok` — só depois dos cinco testes.

> **Teste do cartão:** se a sua definição não cabe num cartão de memória, ela ainda não
> é uma definição — é um resumo. Volte e corte até doer.

---

## 2. O ritual de 90 minutos

Uma sessão = uma nota. Não tente três. O relógio abaixo é o que separa "estudei" de
"achei que estudei".

| Bloco | Tempo | O que fazer | Regra |
|---|---|---|---|
| **1. Leitura ativa** | 20 min | Ler a seção da obra que cobre o conceito, marcando **3 passagens**: a definição, o exemplo do autor e a objeção mais forte | Não anote ainda; só marque |
| **2. Escrita às cegas** | 25 min | Preencher *Definição em uma frase* e *Explicação com as minhas palavras* **sem olhar a nota antiga e sem IA** | Se travar, escreva o que travou — é o diagnóstico |
| **3. Citação e página** | 15 min | Copiar a passagem marcada com capítulo e página; escrever 1 frase dizendo por que ela captura o conceito | Sem página = sem citação |
| **4. Exemplo e conexão** | 15 min | Escrever um exemplo brasileiro seu e uma conexão com outro tema, com o *porquê* | O exemplo precisa ser seu, não do autor |
| **5. Conferência** | 10 min | Rodar `make pendencias`, comparar com a nota antiga e com a IA, corrigir o que você esqueceu | Só agora a IA entra |
| **6. Diário** | 5 min | Uma entrada curta: o que mudou no seu jeito de ver | Nunca gerado por IA |

**Por que a ordem importa:** os blocos 2 a 4 são onde a memória se forma. Se você ler a
resposta da IA antes de tentar, o cérebro reconhece e não recupera — e a nota fica bonita
e oca. É o mesmo motivo pelo qual reler não funciona e responder funciona.

### 2.1 O bloco 5 — como usar o CLI sem terceirizar o estudo

```bash
make pendencias                 # o que falta em cada nota, em ordem de pendência
make pendencias TEMA=historia   # só o tema da sessão
make auditar                    # links, metadados, seções obrigatórias
make painel                     # regenera índice, tabela, progresso e flashcards
```

Se `pendencias` lista uma pendência que você **discorda**, escreva na nota por quê (na
própria seção). Discórdia argumentada é estudo; pendência ignorada é dívida.

---

## 3. Antes e depois: a mesma nota, dois estados

Exemplo real do painel — `sociologia-imaginacao-sociologica.md`, eleita padrão-ouro pelo
Guia 07. Ela está em `rascunho`. Veja o que muda:

**Antes (rascunho — o que existe hoje):**

```markdown
## Definição em uma frase

Imaginação sociológica é a capacidade de conectar a experiência pessoal à estrutura
social e à história — entender que o "problema meu" quase nunca nasce só dentro de mim.

## Explicação com as minhas palavras (rascunho — reescrever)

O exemplo de Mills é cirúrgico: um homem desempregado vive um problema pessoal [...]
Para o painel, ela é o hábito fundador [...]
```

**Depois (o que a sessão produz):**

```markdown
## Definição em uma frase

Ver o próprio problema como caso de uma questão pública — e a questão pública como
história de alguém.

## Explicação com as minhas palavras

Meu irmão perdeu o emprego em março e passou quatro meses dizendo que era "falta de
competência". Ele tinha razão em uma coisa: a entrevista foi mal. Mas a firma demitiu 40
pessoas na mesma semana, e o bairro inteiro dependia dela. Mills chama de imaginação
sociológica exatamente essa troca de lente — do que eu fiz de errado para o que estava
armado antes de eu chegar. Não é tirar a responsabilidade: é não confundir biografia com
culpa. A pergunta que fica é sempre dupla: o que em mim explica isto, e o que na estrutura
explica isto?

## Trecho de apoio

> "Nem a vida de um indivíduo nem a história de uma sociedade podem ser entendidas sem
> que se entenda a de ambos." (cap. 1, "A Promessa", p. 12)

É a frase que define o método: o par indivíduo/sociedade não é uma escolha, é uma
unidade de análise.

## Exemplos que ilustram

- O irmão demitido (acima): 1 caso é drama pessoal, 40 casos na mesma semana é questão
  pública.
- "Burnout" virou diagnóstico individual de um problema de organização do trabalho —
  a mesma operação, invertida.
```

Repare no que **não** mudou: o autor, a obra, a ideia. O que mudou foi a voz, o exemplo e
a prova. Uma nota `ok` não é uma nota maior — é uma nota **sua**.

---

## 4. Anti-padrões (o que impede a nota de virar `ok`)

| Anti-padrão | Como reconhecer | Correção |
|---|---|---|
| **Nota-enciclopédia** | 800 palavras, cobre 3 autores, nenhum exemplo | Corte para o conceito central; os outros viram notas próprias |
| **Citação órfã** | trecho bonito sem página e sem comentário | Página + uma frase dizendo por que ele serve |
| **Eco da IA** | frases genéricas, zero particularidade | Reescreva citando um caso seu; se não houver caso, você não entendeu |
| **Concordância automática** | só repete o autor, sem objeção | Escreva a objeção mais forte que você conhece |
| **Exemplo importado** | "nos Estados Unidos, um estudo mostrou..." | Troque por um caso brasileiro verificável |
| **Diário terceirizado** | síntese em linguagem de resumo executivo | Escreva à mão, sem IA, mesmo que pior |
| **Nota nova em vez de nota pronta** | 90 notas, 0 `ok` | Pague a dívida antes de abrir tema novo |

---

## 5. Ritmo: quantas sessões, em que ordem

A ordem vem das trilhas, não do entusiasmo:

1. **Sessão 1 por semana, mínimo.** 90 minutos, uma nota. Em 6 meses são 26 notas `ok`.
2. **Um tema por mês.** Termine as 5 notas do tema antes de abrir outro (senão você
   reproduz no estudo o problema que o Guia 09 chama de sopa de disciplinas).
3. **Ordem interna:** a nota-bússola (eixo) primeiro? **Não** — ela é a última. Comece
   pelas notas que a trilha lista primeiro e deixe o eixo para o fechamento: ele
   reorganiza o que já existe.
4. **Diário a cada 3 sessões**, no mínimo. O marco do Guia 07 pede 12 entradas.

### 5.1 A fila sugerida (primeiras 10 sessões)

| # | Nota | Tema | Por que nesta ordem |
|---|---|---|---|
| 1 | Imaginação sociológica | Sociologia | é a lente que abre todas as outras |
| 2 | Fato social | Sociologia | dá o objeto; sem ele a lente é só opinião |
| 3 | Alienação | Sociologia | primeiro clássico com diagnóstico do trabalho |
| 4 | Racionalização | Sociologia | o par de alienação: a mesma fábrica, duas leituras |
| 5 | Eixo Conflito × Coesão | Sociologia | fecha o bloco e reposiciona 2, 3 e 4 |
| 6 | Fonte histórica | História | muda o jeito de ler tudo o que vem depois |
| 7 | Colonialismo | História | conecta Brasil ao resto do painel |
| 8 | Racismo estrutural | História | a ponte entre história e desigualdade atual |
| 9 | Cordialidade | Sociologia | o conceito que explica o cotidiano brasileiro |
| 10 | Eixo Natureza × Cultura | Antropologia | abre o segundo tema com a bússola certa |

> Se em alguma sessão você não conseguir escrever o exemplo brasileiro, **não pule**:
> escolha outro conceito mais próximo da sua vida. Exemplo é o teste de compreensão.

---

## 6. Integração com os marcos do projeto

Cada sessão move números reais em [`progresso.md`](../progresso.md):

| Marco do Guia 07 | Alvo | Cada sessão move? |
|---|---|---|
| Notas reescritas (`ok`) | 25 | **sim**, +1 |
| Entradas de diário | 12 | a cada 3 sessões |
| Notas com citação de apoio | 25 | **sim**, +1 |
| Fichas de leitura | 3 | ao fechar um livro (2 a 3 sessões) |

A conta honesta: **25 sessões** de 90 minutos (≈ 37 horas) destravam três dos quatro
marcos do Guia 07. Não existe atalho — e é por isso que o painel mede isso e não o número
de notas.

---

## 7. Quando quebrar o ritual

O ritual existe para vencer a procrastinação, não para virar burocracia. Quebre quando:

- **o livro te pegar:** se uma passagem abrir uma pergunta que não está na trilha, siga a
  pergunta e registre no diário (é o Modo Exploração Livre do Guia 02);
- **a nota não fechar em 90 min:** pare no bloco 4 e retome amanhã. Nota pela metade é
  normal; nota empurrada com texto de IA não é;
- **você já souber o conceito:** pule a leitura e vá direto ao bloco 2. O teste é escrever,
  não ler.

## 8. Uma frase para lembrar

> O painel não precisa de mais uma nota. Precisa de você escrevendo esta.
