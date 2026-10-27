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

Hoje: **58 indicações** em 8 temas. A maioria são videoaulas gratuitas (várias de
graduação); há também artigos em acesso aberto, um resumo acadêmico, filmes e um
podcast. A própria página mostra a **cobertura das trilhas**: 67 dos 90 nós com
link já têm mídia ligada.

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
7. `midias.md` tem de estar igual ao que o gerador produz (senão: rode `make painel`).

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
| Psicologia | 16 | *Introdução à Psicanálise* (Instituto ESPE) e Fulgencio sobre o apego (IP-USP) |
| Sociologia | 11 | *SBS Aulas Abertas — O que é Sociologia?* (Irlys Barreira, UFC) |
| Filosofia | 9 | *Curso Introdução Geral à Filosofia, Aula 1* (Victor Sales Pinheiro/INÉF) |
| História | 8 | *Continuidade e Ruptura na Construção Nacional do Brasil* (IEA-USP) |
| Antropologia | 4 | *Relativismo cultural* (Brasil Escola) |
| Geografia | 4 | *Espaço geográfico* (Brasil Escola) |
| Ciência Política | 3 | *Curso de Ciência Política, Aula 02* (Prof. Matheus Passos) |
| Economia | 3 | *Introdução à Inflação* (Denise Cyrillo, FEA-USP) |

### Cobertura das trilhas

O gerador compara os links de cada nó com as notas citadas em `conceitos` e publica
a tabela de cobertura dentro de `midias.md`. Situação em 27/10/2026: **67 de 90
nós com link** (ficam fora os nós "síntese no diário" e a trilha Integrada, cujos
nós não apontam para notas).

| Trilha | Nós com mídia |
|---|---|
| História — Nível 1 | 7/7 (100%) |
| Psicologia — Nível 2 | 8/8 (100%) |
| Psicologia — Nível 1 | 10/11 (91%) |
| Ciência Política — Nível 1 | 6/7 (86%) |
| Geografia — Nível 1 | 6/7 (86%) |
| Antropologia — Nível 1 | 5/7 (71%) |
| Filosofia — Nível 1 | 8/12 (67%) |
| Sociologia — Nível 1 | 8/12 (67%) |
| Pensamento Social Brasileiro | 6/11 (55%) |
| Economia — Nível 1 | 3/8 (38%) |

As duas trilhas que estavam no fim da tabela (História, 14%, e Psicologia Nível 2,
12%) fecharam em 100% nesta rodada. Parte da subida das outras vem de nós
compartilhados, e não de mídia feita para elas: Filosofia ganhou um nó porque
`eixo-mente-corpo` é citado lá também; Pensamento Social Brasileiro ganhou dois
porque as notas de `historia-colonialismo` e `historia-escravidao-abolicao` são
usadas nos nós da trilha. Cobertura é cobertura — mas o peso da mídia continua
sendo o que diz o campo `peso`.

Acervos que aparecem mais de uma vez e valem assinar: **Canal USP** (aulas de
graduação da FEA e da FFLCH), **UNIVESP** (cursos completos de Sociologia,
Filosofia da Educação), **SBS tv** (ciclo *Aulas Abertas* da Sociedade Brasileira
de Sociologia), **Brasil Escola** (divulgação curta e correta), **ILP**
(conferências sobre formação do Brasil), **IEA-USP** e **Quilombo da UFRJ**
(universidade em vídeo aberto) e, para revisão rápida, **Minutos Psíquicos**,
**Nerdologia** e **Canal Futura**.

### Lacunas conhecidas

- **Antropologia**: continua sem aula universitária em vídeo aberto. As aulas de
  *Antropologia I* da USP (Heloisa Buarque de Almeida) estão na
  [e-Aulas](https://eaulas.usp.br/) e são excelentes — **mas exigem login USP**
  (conferido em 27/10/2026), então não entram nesta lista. Ficam como sugestão
  para quem tem vínculo.
- **Economia**: 3 de 8 — o gargalo seguinte. Falta vídeo aberto de qualidade
  sobre macro, moeda e pensamento econômico (a FEA-USP tem aula, mas o acervo
  aberto é pequeno).
- **História**: 7 de 7, mas com peso desigual — só duas entradas são de nível
  universitário (IEA-USP e Quijano pelo Quilombo da UFRJ). As demais são
  divulgação correta, não aula de graduação.
- **Psicologia Nível 2**: 8 de 8. O elo mais fraco é `psicologia-fluxo`, que
  depende de uma palestra do próprio Csikszentmihalyi (TED, 2004) e não de uma
  aula em português; e `eixo-mente-corpo` está apoiado em divulgação sobre
  Damásio, não em aula de neurociência.
- **Filosofia**: ainda falta Butler (o podcast cobre mal) e uma aula sobre
  fenomenologia (Husserl/Heidegger).
- **Integrada**: nenhuma indicação; a trilha não tem nós linkados, então nem
  aparece na cobertura.
- **Pensamento social brasileiro**: 4 de 11 — faltam Florestan Fernandes,
  DaMatta e Sérgio Buarque em vídeo.

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

1. **Economia (3/8)** — é a única trilha ainda abaixo de 40%; precisa de vídeo
   aberto de macro, moeda e história do pensamento econômico.
2. **Uma mídia por nó**: a meta não é 133 links, é que cada trilha tenha **uma
   porta de entrada em vídeo** e **uma leitura de apoio por nó**. A tabela de
   cobertura em `midias.md` é o placar.
3. **Podcasts com episódio específico**: hoje *Filosofia Pop* está cadastrado sem
   episódio. O certo é cadastrar o episódio (título, número, duração).
4. **Reconferir a cada seis meses**: `verificado_em` serve para isso. Uma mídia
   com mais de um ano sem revisão deve ser reaberta antes de continuar na lista.
