# Guia 11 — Mídias e videoaulas

> **A regra que organiza tudo:** mídia é **apoio**, nunca fonte. Um vídeo pode
> abrir a porta de um conceito, mas a nota só vira `ok` com obra primária, capítulo
> e página na seção *Trecho de apoio*. Quem assiste e não escreve não estudou —
> apenas se informou.

Este guia explica a biblioteca de mídias do painel: o que entra, como se verifica,
como se usa e o que ficou de fora dos planos antigos.

---

## 1. O que é a biblioteca

Um arquivo de curadoria — [`midias/biblioteca.yml`](https://github.com/LucasRangel89/humanitas/blob/main/midias/biblioteca.yml) — e
dois artefatos gerados dele:

| Arquivo | O que é |
|---|---|
| `midias/biblioteca.yml` | A **fonte**: uma entrada por mídia, com tema, notas ligadas, data e método de verificação |
| [`midias.md`](../midias.md) | Página pública (também no site, em **Biblioteca → Mídias**), agrupada por tema |
| `indices/midias.json` | Versão para máquina: contagens por tipo, tema e método de verificação |

Hoje: **86 indicações** em 8 temas. A maioria são videoaulas gratuitas (várias de
graduação); há também artigos em acesso aberto, um resumo acadêmico, um
documentário, filmes, um podcast e um curso universitário em inglês com legenda em
português. A própria página mostra a **cobertura das trilhas**: **90 de 90** nós com
link já têm mídia **em português** ligada (a regra de idioma está na seção 2).

### Os cinco pesos (para você saber o que esperar antes de clicar)

| Peso | O que é | Quando usar |
|---|---|---|
| `aula-universitaria` | Aula de graduação/pós gravada (USP, Univesp, SBS, institutos) | **Primeiro contato sério** com um conceito; costuma ter 40–90 min |
| `curso-livre` | Curso gratuito de longa duração (30–50 aulas) | Percursos longos; escolha módulos, não assista tudo de uma vez |
| `divulgacao` | Aula curta de cursinho ou canal de divulgação | Revisar, ver exemplo, fixar vocabulário — **nunca** substitui a aula |
| `fonte-academica` | Artigo revisado por pares, de acesso aberto | Quando você já leu o texto-base e quer uma leitura de segunda ordem |
| `obra-de-apoio` | Filme, documentário, podcast | Criar intuição e pergunta; entra no diário, não na citação |

---

## 2. Como uma mídia entra (o protocolo)

Nada entra "porque eu conheço o canal". Cada linha da biblioteca foi **aberta e
conferida**, e o arquivo registra a data e o método:

| `verificado_como` | Significa | Como se faz |
|---|---|---|
| `oembed` | Título e canal copiados da API oficial do YouTube | `https://www.youtube.com/oembed?url=<link>&format=json` — devolve `title` e `author_name`. Abrir no navegador e copiar |
| `pagina` | Página aberta e lida (artigo, verbete, resumo) | Abrir a URL, conferir título, autor e veículo |
| `material-do-autor` | Veio dos planos/anexos do próprio autor, **sem URL** | Só vale para filme/podcast/documentário, e o campo `onde` diz onde procurar |

Regras que a auditoria cobra (erro bloqueia o CI):

1. `id`, `tipo`, `titulo`, `autor`, `tema`, `verificado_em` e `verificado_como` são obrigatórios;
2. `tipo` ∈ `videoaula · curso · podcast · documentario · filme · artigo · resenha · verbete`;
3. `tema` tem de existir em `TEMAS` (os mesmos 9 do painel);
4. toda `conceitos` precisa apontar para uma nota que existe em `conceitos/`;
5. URL sempre `https://`, sem repetição entre entradas;
6. entrada com URL **não pode** ser marcada como `material-do-autor`;
7. mídia em idioma estrangeiro declara `idioma` **e** `legendas` (ver abaixo);
8. `midias.md` tem de estar igual ao que o gerador produz (senão: rode `make painel`).

**Hospedagem fora do YouTube** (Drive, Vimeo, site do curso): só entra com o aval
explícito do autor do projeto, caso a caso, porque o link é mais frágil e não
passa pelo oEmbed. Nesse caso `verificado_como: pagina` e a página indicada é a
do curso, não o arquivo solto. Exceção registrada hoje: o curso *Introdução a
Economia* do LALT/FEC-Unicamp, cujos vídeos são mp4 no Drive.

### Mídia em outro idioma (espanhol, inglês)

O projeto é **em português**. Uma mídia estrangeira entra como *camada de
aprofundamento* — nunca como porta de entrada de um conceito, e nunca no lugar de
um material em português que exista.

| Campo | Valores | Regra |
|---|---|---|
| `idioma` | `pt` (padrão) · `en` · `es` | Ausência do campo significa `pt`. Mídia em `en`/`es` **precisa** declarar `legendas`, senão a auditoria barra |
| `legendas` | `pt` · `es` · `en` · `nenhuma` · `nao-verificado` | O que a pessoa vai ver ao assistir. `nao-verificado` é permitido, mas gera aviso na auditoria — é dúvida assumida, não atalho |

Critérios para aceitar:

1. **Só onde o português é fraco ou não existe.** Se há aula de graduação em
   português cobrindo o conceito, a estrangeira não entra para "melhorar a nota".
   A `nota` do item tem de dizer **por que não há equivalente em português** — não
   basta "é excelente".
2. **Legenda decide o desempate.** Entre uma fonte inglesa com legenda em
   português e uma espanhola sem legenda, ganha a inglesa. Vídeo sem legenda
   nenhuma e com áudio difícil só entra se for a única opção e a nota avisar.
3. **Continua valendo o protocolo da seção 2**, inclusive a regra de hospedagem:
   player próprio (por exemplo, CanalUNED) não entra sem aval do autor do projeto.
4. **A cobertura não muda de régua.** O placar das trilhas conta **só mídia em
   português**. Há uma segunda contagem, ao lado, que soma espanhol e inglês — ela
   existe para mostrar apoio extra, jamais para inflar o número de português.

Na página gerada, o item estrangeiro aparece com o selo ao lado do canal:
`**inglês, legenda em português**`, `**espanhol, legenda em espanhol**` ou
`**inglês, sem legenda**`. Em `indices/midias.json`, `totais.por_idioma` traz a
contagem por idioma.

O item 4 é o que dá sentido à lista: **a mídia é indexada pelo conceito que ela
ajuda a estudar**, não pelo canal. Se você não sabe a qual nota ela serve, é
entretenimento.

> ⚠️ Se um vídeo sair do ar, o título continua verdadeiro — mas o link quebra.
> Corrija a linha no YAML, atualize `verificado_em` e rode `make painel`.
> Não substitua o link por uma busca ("procure no YouTube"): isso devolve o
> problema que esta biblioteca resolve.

---

## 3. O que já está lá

| Tema | Indicações | Melhor porta de entrada |
|---|---|---|
| Psicologia | 17 | *Introdução à Psicanálise* (Instituto ESPE) e Fulgencio sobre o apego (IP-USP) |
| Sociologia | 20 | *SBS Aulas Abertas — O que é Sociologia?* (Irlys Barreira, UFC) |
| Filosofia | 13 | *Curso Introdução Geral à Filosofia, Aula 1* (Victor Sales Pinheiro/INÉF) |
| História | 9 | *Continuidade e Ruptura na Construção Nacional do Brasil* (IEA-USP) |
| Economia | 8 | *Introdução a Economia, aula 1* (FEC-Unicamp, Cursos Abertos do LALT) |
| Antropologia | 9 | *O Povo Brasileiro, ep. 4* (Darcy Ribeiro) e a aula de Munanga |
| Geografia | 5 | *Espaço geográfico* (Brasil Escola) |
| Ciência Política | 5 | *Curso de Ciência Política, Aula 02* (Prof. Matheus Passos) |

### Cobertura das trilhas

O gerador compara os links de cada nó com as notas citadas em `conceitos` e publica
a tabela de cobertura dentro de `midias.md`. Situação em 27/10/2026: **90 de 90
nós com link** (ficam fora da conta os nós "síntese no diário" e a trilha
Integrada, cujos nós não apontam para notas).

| Trilha | Nós com mídia |
|---|---|
| Antropologia — Nível 1 | 7/7 (100%) |
| Ciência Política — Nível 1 | 7/7 (100%) |
| Economia — Nível 1 | 8/8 (100%) |
| Filosofia — Nível 1 | 12/12 (100%) |
| Geografia — Nível 1 | 7/7 (100%) |
| História — Nível 1 | 7/7 (100%) |
| Pensamento Social Brasileiro | 11/11 (100%) |
| Psicologia — Nível 1 | 11/11 (100%) |
| Psicologia — Nível 2 | 8/8 (100%) |
| Sociologia — Nível 1 | 12/12 (100%) |

**Todas as dez trilhas estão em 100%** — e vale olhar o campo `peso` antes de
comemorar, porque cobertura mede link, não profundidade. Em Filosofia e
Sociologia, que estavam em 8/12, das oito lacunas fechadas,
duas entraram como `curso-livre` de um curso público sobre Kant (Escola do
Parlamento, com professor da PUC-SP), uma como `aula-universitaria` (SBS), e as
outras cinco como `divulgacao` do Brasil Escola e de um canal de filosofia. O nó
do eixo Conflito × Coesão, em particular, foi fechado com **duas** videoaulas de
divulgação — uma para cada polo —, porque não achei material que tratasse da
comparação de uma vez. Cobertura é cobertura; o peso continua dizendo o que
esperar antes de clicar.

**Segunda rodada: trocar divulgação por aula de universidade.** A fila do Guia
apontava oito nós fechados com divulgação. Nesta rodada entraram dois, os dois da
UNIVESP, e a diferença não está no link (que já existia) e sim no que a pessoa
encontra ao clicar:

| Nó | Antes | Agora |
|---|---|---|
| `sociologia-anomia` | Brasil Escola (7 min, divulgação) | videoaula 3 de *Sociologia da Educação* (HSE-001), com **Gabriel Cohn (USP) e Raquel Weiss**: fato social, solidariedade e anomia como forma patológica, 17 min. O vídeo do Brasil Escola continua na lista, como revisão |
| `eixo-conflito-coesao` | duas videoaulas de divulgação, uma por polo | *Na Íntegra*: **Gabriel Cohn** compara Marx e Durkheim, os dois polos do eixo, de uma vez, em 25 min |

Onde a fila continua travada — e por quê, depois de procurar de novo:

- `psicologia-funcionalismo`, `sociologia-papel-social`/`identidade`,
  `geografia-escala`, `filosofia-eudaimonia`: procurei aula de graduação aberta em
  português e **não existe** no YouTube. O que aparece é divulgação de canal, que é
  exatamente o que já está lá. Não vou trocar seis por meia dúzia para melhorar a
  aparência da tabela.
- `antropologia-ritual`: o material certo está no e-Aulas da USP, atrás de login.

Uma exceção recente, e só uma: o eixo Liberdade × Igualdade ganhou o curso
*Justice*, de Michael Sandel, **em inglês com legenda em português**. Ele não entra
na conta da cobertura porque a régua é o português; entra ao lado dela, para o nó
em que a biblioteca em português só tinha um lado da balança. A regra que permite
essa exceção está na seção 2.

As três últimas lacunas — Psicologia N1, Ciência Política e Geografia — caíram
todas na mesma rodada e **todas com divulgação**, das três a mais fraca em peso.
Vale dizer o que isso significa: `psicologia-funcionalismo` tem vídeo de canal
introdutório, `eixo-liberdade-igualdade` tem a explicação do par de Berlin por um
professor mas **só um lado da balança**, e `geografia-escala` tem um vídeo de
categoria geográfica que vem emendado com redes. O placar fechou; a qualidade
desses três é a mais baixa da biblioteca, e está escrito na nota de cada um.

Antropologia fechou com o par mais desigual da biblioteca: uma
jornada de seminários do Departamento de Antropologia da USP sobre os 90 anos de
*As técnicas do corpo* (institucional, densa, longa) e uma conversa de TV
universitária em que DaMatta explica o carnaval como ritual. A segunda não ensina
van Gennep nem Turner — está registrada como `obra-de-apoio` justamente por isso.

Acervos que aparecem mais de uma vez e valem assinar: **Canal USP** (aulas de
graduação da FEA e da FFLCH), **UNIVESP** (cursos completos de Sociologia,
Filosofia da Educação), **SBS tv** (ciclo *Aulas Abertas* da Sociedade Brasileira
de Sociologia), **Brasil Escola** (divulgação curta e correta), **ILP**
(conferências sobre formação do Brasil), **IEA-USP** e **Quilombo da UFRJ**
(universidade em vídeo aberto) e, para revisão rápida, **Minutos Psíquicos**,
**Nerdologia** e **Canal Futura**.

### Lacunas conhecidas

- **Antropologia**: 7 de 7, mas ainda **não há introdução à antropologia em
  vídeo aberto** — o que existe são aulas sobre recortes (Munanga, Darcy Ribeiro,
  técnicas do corpo, ritual). As aulas de *Antropologia I* da USP estão na
  [e-Aulas](https://eaulas.usp.br/) e são exatamente o que falta — inclusive uma
  chamada *Ritual, símbolo, liminaridade e poder* —, **mas exigem login USP**
  (conferido de novo em 27/10/2026), então não entram nesta lista. Ficam como
  sugestão para quem tem vínculo.
- **Economia**: 8 de 8, mas metade da trilha depende de um curso cujo vídeo é
  **mp4 no Google Drive**, não YouTube: os Cursos Abertos do LALT (FEC-Unicamp)
  publicam a aula em Drive, com slides, leituras e exercícios na página. Funciona
  e abre sem login (conferido em 27/10/2026), mas é um formato mais frágil que o
  oEmbed — se o arquivo sair do ar, o link morre sem aviso. As outras duas
  entradas (UNIVESP) são YouTube.
- **Filosofia e Sociologia**: fecharam em 12/12 nesta rodada, mas o caminho foi
  desigual. O melhor achado foram duas aulas do curso *Introdução à Filosofia de
  Immanuel Kant* da Escola do Parlamento (Câmara Municipal de SP), com o Prof.
  Dr. Mario Ariel González Porta (PUC-SP): a aula 3 trata justamente de
  fenômeno e númeno e a aula 4, do imperativo categórico. Ressalva importante: o
  nó é sobre o par **kantiano** — **fenomenologia** como escola (Husserl,
  Heidegger) continua sem aula aberta em português, e isso não foi resolvido.
  Em Sociologia, o nó de gênero/interseccionalidade foi fechado com a aula 7 do
  ciclo SBS (Profª. Paula Cristina da Silva, UFBA). Eudaimonia, anomia, papéis/
  identidade e o eixo Conflito × Coesão ficaram com divulgação: procurei aula
  universitária aberta para os quatro e não encontrei (Butler e movimentos
  sociais seguem sem vídeo próprio).
- **Racismo estrutural e democracia racial**: cobertos, mas por palestras
  publicadas em canais que não são da universidade (Munanga está numa
  republicação, Silvio Almeida na UFSC, Jessé Souza num sindicato). São boas falas
  dos próprios autores; o risco é o vídeo sair do ar — reconferir a cada seis
  meses.
- **História**: 7 de 7, mas com peso desigual — só duas entradas são de nível
  universitário (IEA-USP e Quijano pelo Quilombo da UFRJ). As demais são
  divulgação correta, não aula de graduação.
- **Psicologia Nível 2**: 8 de 8. O elo mais fraco é `psicologia-fluxo`, que
  depende de uma palestra do próprio Csikszentmihalyi (TED, 2004) e não de uma
  aula em português; e `eixo-mente-corpo` está apoiado em divulgação sobre
  Damásio, não em aula de neurociência.
- **Psicologia Nível 1, Ciência Política e Geografia**: 100% de cobertura, mas
  fechadas com divulgação (ver acima). São os primeiros candidatos a substituição
  quando aparecer aula universitária aberta. Em Ciência Política há um paliativo
  assumido: o curso *Justice* (Harvard, legenda em português) cobre Rawls, Nozick,
  Mill e Locke com profundidade de graduação, mas **em inglês** — é aprofundamento,
  não substitui a porta de entrada em português.
- **Integrada**: nenhuma indicação; a trilha não tem nós linkados, então nem
  aparece na cobertura.

---

## 4. Como assistir sem perder tempo

O [Guia 10](10-ritual-de-estudo.md) manda dividir a sessão de 90 minutos em
leitura ativa, escrita e conferência. A mídia entra **no lugar da leitura**, com
três ajustes:

1. **Escolha pelo peso, não pela duração.** Primeiro contato de um conceito?
   `divulgacao` (10–20 min) e depois a nota. Já leu o texto e quer consolidar?
   `aula-universitaria`.
2. **Regra dos 20 minutos.** A cada 20 minutos, pause e escreva uma frase com as
   suas palavras. Se a frase não sair, o vídeo não entrou — reveja ou troque.
3. **Termine no diário, não no vídeo.** Uma entrada de diário ligando o vídeo à
   nota é o que transforma "assisti" em "estudei". Depois marque o nó na trilha.

Anti-padrões: assistir em 1,5x sem pausar; colecionar playlists; usar vídeo como
prova de que "já sei o conceito"; citar o vídeo como se fosse a obra (não é).

---

## 5. Como adicionar uma mídia

1. Abra a mídia e copie o título **exato** (para YouTube, use o endpoint de
   oEmbed do §2 — ele devolve o título e o canal oficiais).
2. Acrescente o bloco em `midias/biblioteca.yml`, no tema correspondente:

```yaml
  - id: sobrenome-conceito          # minúsculas, hífens, único
    tipo: videoaula                 # videoaula | curso | podcast | documentario | filme | artigo | resenha | verbete
    peso: aula-universitaria        # aula-universitaria | curso-livre | divulgacao | fonte-academica | obra-de-apoio
    titulo: "Título exato como aparece na fonte"
    autor: "Quem fala/escreve, com a instituição"
    canal: "Nome do canal (YouTube)"   # ou `veiculo:` para artigo
    url: "https://..."
    tema: sociologia
    conceitos: [sociologia-habitus]  # notas que existem em conceitos/
    nota: "Por que vale, em uma ou duas frases — e o que ele NÃO cobre."
    verificado_em: 2026-10-27
    verificado_como: oembed
```

3. Rode:

```bash
make midias     # regenera midias.md e indices/midias.json
make auditar    # confere tema, conceito, URL repetida, data de verificação
make painel     # índice, progresso, cartões e mídias
```

4. Se o vídeo for longo, diga na `nota` **qual parte** interessa ("assista dos
   12 aos 40 minutos") — isso economiza mais tempo do que qualquer resumo.

---

## 6. O que veio dos dez arquivos antigos

Os planos anexados nesta rodada foram lidos um a um. O que era reaproveitável
virou dado; o que era projeto de outro produto ficou de fora — de propósito.

| Arquivo | O que trazia | O que entrou no projeto |
|---|---|---|
| **Plano de Estudos Detalhado** (Filosofia, Psicologia Social, Antropologia, Estudos Culturais, Gestão de TI e Design) — 18 aulas | Estrutura de aula com objetivos, contexto, leituras, **filmes e podcasts** por aula | Os filmes (Matrix, Tempos Modernos, O Experimento, Parasita, Laranja Mecânica, Gattaca) e o podcast *Filosofia Pop* foram cadastrados como `obra-de-apoio`, ligados às notas certas |
| **Guia de Estudos Integrativo de Psicologia** | Tabela escolas × autores × objeto × grande questão filosófica, **com fontes reais** | Duas fontes verificadas entraram como `artigo`/`resenha` (SciELO sobre Milgram; Unoesc sobre Titchener). A tabela em si é o desenho da trilha de Psicologia — que já existe |
| **Grade Curricular para Psicologia** (102 KB) e **para Estudo Autodidata** (22 KB) | Currículo completo em 4 módulos: bases biológicas, desenvolvimento, psicopatologia, metodologia, neuropsicologia, ética | Serviu de **checklist de lacunas**: psicopatologia, neuropsicologia, métodos e ética ainda não têm nota nem trilha (ver §3 e Guia 09) |
| **Grade Curricular: Sociologia, Tecnologia e Sociedade** | Fases com sociologia digital, STS, ética da IA, letramento de dados | Confirma a direção do tema `sociologia` na fronteira com tecnologia; alimenta as próximas notas (ainda sem trilha) |
| **Trilha de aprendizagem** | Três degraus com conceitos-chave, leituras primárias x secundárias e perguntas orientadoras por tópico | Reforçou o formato das trilhas atuais (nó = conceito + leitura + pergunta). Não gerou mídia |
| **Introdução à Filosofia** | 30+ módulos com objetivo, tópicos, pensadores, leituras, perguntas e "recursos contínuos" (SEP, IEP, Philosophy Talk) | Os "recursos contínuos" justificam as indicações de curso longo (INÉF, Filosofia Vermelha) |
| **HUMANITAS EXPLORE — Blueprint** (86 KB) e **Humanitas Explore Gemini** | Especificação de app: onboarding, XP, badges, streak, JSON de dados, prompts para AI Studio | **Fora de escopo**: o painel é um repositório estático + MkDocs. Progresso já existe via localStorage (`/registrar/`), sem gamificação por decisão de projeto |
| **Dashboard de Estudos Interdisciplinares (deepseek)** | Markdown escapado (`\#\#`), arquitetura de dashboard em caixas de texto | Sem conteúdo recuperável — descartado após leitura |

### O que foi deliberadamente recusado

- **Gamificação (XP, badges, streak)**: recompensa consumo, não compreensão. O
  painel mede o que interessa — nota reescrita, citação com página, nó concluído.
- **Currículos completos como trilhas**: um currículo de 60 disciplinas não diz
  por onde começar. As trilhas do projeto têm 12 nós e um objetivo em uma frase.
- **"Procure no YouTube por X"**: era o formato dos planos antigos e devolve o
  problema. Toda indicação daqui tem link, título e data de conferência.
- **Citar vídeo como fonte primária**: não. Filme e videoaula entram no diário e
  na pergunta, nunca na seção *Trecho de apoio*.

---

## 7. Próximos passos

1. **A cobertura acabou: 90 de 90.** O que resta não é acrescentar indicação, é
   **substituir as fracas por fortes**. Já resolvidos: `eixo-liberdade-igualdade`
   (curso *Justice*, em inglês com legenda), `sociologia-anomia` e o eixo
   Conflito × Coesão (UNIVESP). A fila que sobra, da pior para a menos pior:
   `geografia-escala`, `psicologia-funcionalismo`,
   `sociologia-papel-social`/`identidade`, `antropologia-ritual`,
   `filosofia-eudaimonia`.
2. **Antropologia e Filosofia dependem de acesso institucional.** A introdução à
   antropologia e a fenomenologia de Husserl/Heidegger só existem em vídeo dentro
   do e-Aulas da USP, atrás de login. Sem vínculo USP, a lacuna é real e não tem
   solução no YouTube aberto — melhor registrar do que fingir.
3. **Uma mídia por nó**: a meta nunca foi 133 links, é que cada trilha tenha
   **uma porta de entrada em vídeo** e **uma leitura de apoio por nó**. Com o
   placar fechado, essa é a única régua que ainda diz alguma coisa.
4. **Podcasts com episódio específico**: hoje *Filosofia Pop* está cadastrado sem
   episódio. O certo é cadastrar o episódio (título, número, duração).
5. **Reconferir a cada seis meses**: `verificado_em` serve para isso. Uma mídia
   com mais de um ano sem revisão deve ser reaberta antes de continuar na lista.
