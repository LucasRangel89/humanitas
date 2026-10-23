# Guia 09 — Expansão para as humanidades: mapa, critérios e ordem de entrada

> **Status deste documento:** plano de expansão, não conteúdo de estudo. Nada aqui
> cria notas sozinho — ele decide *o que* pode entrar, *como* cada área entra e *em
> que ordem*, para o painel crescer sem virar uma estante de assuntos pela metade.
> O plano de execução vigente continua sendo o [Guia 07](07-rumos-e-proximos-passos.md).

## Em cinco linhas

1. As humanidades já estão no DNA do projeto: o README promete "história, sociologia,
   filosofia, ciência política, antropologia e áreas vizinhas", e **seis dos dez temas
   registrados no código estão vazios** (História, Geografia, Ciência Política, Economia,
   Antropologia, Psicologia Social). Não é expansão — é preencher o mapa que já existe.
2. O gargalo não é técnico: `scripts/painel/modelo.py` já aceita todos esses temas, e
   `make nova` cria as notas. O gargalo é **leitura e escrita** (50 notas, 0 `ok`).
3. Por isso a regra: **expanda o mapa primeiro, o acervo um tema por vez.**
4. Toda área nova entra como **tema**, **eixo** ou **tag** — nunca como as três coisas
   ao mesmo tempo. Sem esse filtro, em seis meses o painel tem 25 disciplinas e nenhuma
   trilha terminada.
5. Ordem recomendada: **Antropologia → História → Geografia → Ciência Política →
   Economia**, com uma segunda onda (Direito, RI, Linguística, Comunicação, Estudos
   Raciais e de Gênero, CTS) e uma terceira onda opcional.

---

## 1. Diagnóstico: o mapa já existe, o conteúdo não

| Tema | Slug | Notas | Fichas | Trilhas | Situação real |
|---|---|---|---|---|---|
| Sociologia | `sociologia` | 20 | 0 | 1 | Ativo |
| Filosofia | `filosofia` | 15 | 0 | 1 | Ativo |
| Psicologia | `psicologia` | 15 | 0 | 2 | Ativo |
| Integrada | `integrada` | 0 | 0 | 1 | Ativo (só trilha) |
| História | `historia` | 0 | 0 | 0 | **Vazio** |
| Geografia | `geografia` | 0 | 0 | 0 | **Vazio** |
| Ciência Política | `ciencia-politica` | 0 | 0 | 0 | **Vazio** |
| Economia | `economia` | 0 | 0 | 0 | **Vazio** |
| Antropologia | `antropologia` | 0 | 0 | 0 | **Vazio** |
| Psicologia Social | `psicologia-social` | 0 | 0 | 0 | **Vazio** |

Três consequências práticas:

- **A infraestrutura já está paga.** Os cinco temas clássicos estão em `TEMAS`; a
  auditoria aceita o slug; a tabela do README os mostra como "Em breve". Abrir
  Antropologia custa *uma nota*, não uma refatoração.
- **"Em breve" é uma promessa, não um plano.** Hoje seis linhas do README prometem
  conteúdo que não existe. Ou viram plano com data (este guia), ou saem da vitrine.
- **Volume de notas não é progresso.** O `progresso.md` mede `status: ok`. Somar dez
  temas com dez rascunhos de IA cada levaria o painel de 50 para 150 notas e de 0 para
  0 notas reescritas. Seria o dobro de trabalho com o mesmo aprendizado.

**A tese deste guia:** o mapa pode crescer rápido porque é texto e taxonomia; o acervo
cresce devagar porque é leitura. Trate os dois com orçamentos separados.

### 1.1 Orçamento de atenção (por semana)

| Frente | Fatia | O que conta |
|---|---|---|
| Reescrever notas existentes | 60% | transformar `rascunho` em `ok` |
| Tema novo | 30% | 1 a 2 notas reescritas + 1 conceito lido de verdade |
| Infra e taxonomia | 10% | `make painel`, este guia, ajustes de tag |

Se a semana só deu para a infraestrutura, o tema novo não abre. A ordem é essa.

---

## 2. A regra que evita a sopa de disciplinas: tema × eixo × tag

O risco de "adicionar todas as humanidades" não é ficar grande — é ficar **plano**:
trinta disciplinas irmãs, sem hierarquia, cada uma com duas notas. A saída é separar
três camadas que o projeto já tem, mas ainda não usa com disciplina.

| Camada | O que é | Onde vive | Ganha linha no painel? | Exemplo |
|---|---|---|---|---|
| **Tema** | disciplina com objeto, pergunta e método próprios | `tema:` no frontmatter | Sim, com trilha | `antropologia` |
| **Eixo** | pergunta transversal que atravessa temas | nota com `tipo: eixo` + campo `eixos` | Não; aparece no grafo | Natureza × Cultura |
| **Tag** | recorte: autor, escola, país, período, método | `tags:` | Não | `bourdieu`, `brasil`, `seculo-xx` |

**Regra de ouro:** se a área nova não tem pergunta própria, ela é *tag*. Se tem
pergunta própria mas não tem objeto próprio, ela é *eixo*. Só vira *tema* quem tem as
duas coisas — e mais o que está abaixo.

### 2.1 Os seis testes de entrada

Uma área só entra no mapa como tema se passar nos seis. Falhou em um, muda de camada.

1. **Pergunta própria** — o que só ela pergunta? (se a resposta cabe em outra
   disciplina, não é tema)
2. **Objeto próprio** — o que ela recorta do mundo? (o passado? o espaço? a norma?)
3. **Método ou tipo de evidência** — como ela justifica o que afirma? (fonte, trabalho
   de campo, modelo, doutrina, estatística)
4. **Fonte acessível** — pelo menos duas obras de entrada, de preferência em português
   e presentes no seu acervo.
5. **Ponte** — um eixo que a ligue a pelo menos dois temas já ativos. Sem ponte, o tema
   nasce ilha.
6. **Densidade** — oito conceitos que não sejam sinônimos dos que já existem no painel.

### 2.2 Caminho de promoção e de poda

A taxonomia é viva, mas com portas de entrada e de saída explícitas:

| De → para | Gatilho | Exemplo |
|---|---|---|
| tag → eixo | a tag aparece em 5+ notas de 2+ temas e organiza um debate | `genero` → eixo Corpo × Sociedade |
| eixo → tema | o eixo acumula 8 conceitos próprios e um método | Natureza × Cultura → Antropologia |
| tema → pausado | 3 meses sem nota nova e sem nó concluído | Economia, se ficar só no desejo |
| tema → eixo/tag | nunca passou de 3 notas e não tem trilha em 6 meses | Psicologia Social (ver §4.1.6) |

Registre a mudança neste guia e rode `make painel`. Taxonomia sem registro de decisão
vira preferência pessoal — o mesmo princípio da tabela de decisões do Guia 07.

### 2.3 Duas regras operacionais

- **Regra do zero:** tema sem nenhuma nota ou trilha **não entra no README**. Ele vive
  aqui, na seção "planejado", até ter a primeira nota. Isso acaba com a vitrine de
  "Em breve" e transforma o painel num retrato honesto do que você estuda.
  *(Implementação: filtrar `tabela_temas` e listar os planejados em uma linha de
  rodapé — mudança pequena, com teste, para uma PR própria.)*
- **Teto de dois:** no máximo **dois temas em expansão** ao mesmo tempo (com trilha
  aberta e notas nascendo). Os outros ficam "planejados". O teto não limita a
  curiosidade: limita o número de trilhas que você abandona.

---

## 3. As famílias: como o painel continua legível com 20+ temas

Com dez temas, uma tabela plana funciona. Com vinte, não. A solução é agrupar por
**família** — não como hierarquia rígida, mas como agrupamento de leitura na tabela e,
depois, no site.

| Família | Pergunta que une | Temas |
|---|---|---|
| **F1. Normas e ideias** | como devemos viver e o que podemos conhecer? | Filosofia, Direito |
| **F2. Poder, mercado e território** | quem decide, para quem e com que recursos? | Sociologia, Ciência Política, Economia, Relações Internacionais |
| **F3. Tempo, espaço e cultura material** | como o mundo virou este mundo? | História, Geografia, Arqueologia |
| **F4. Cultura, linguagem e sentido** | como atribuímos significado? | Antropologia, Linguística, Comunicação e Mídia, Estudos Literários, História da Arte, Estudos Religiosos |
| **F5. Mente, comportamento e aprendizagem** | como pensamos, sentimos e aprendemos? | Psicologia, Psicologia Social, Educação |
| **F6. Corpo, diferença e poder** | como as diferenças são produzidas e hierarquizadas? | Estudos de Gênero, Estudos Raciais, Estudos Indígenas, Humanidades Ambientais, CTS, Estudos Urbanos |
| **F7. Integração** | o que só se vê juntando as lentes? | Integrada |

Três cuidados:

1. **Sete famílias é o teto.** Oito já é uma nova sopa.
2. **A família é do tema, não da nota.** A nota de "Gênero" mora em Sociologia ou em
   Estudos de Gênero; a família organiza a leitura, não o arquivo.
3. **F6 é transversal de propósito.** Gênero, raça, indígena, ambiente e tecnologia são
   recortes que atravessam todas as famílias; por isso precisam de lugar próprio *e*
   de tags nos outros temas.

Uma nota pertence a **um** `tema` e pode ser pendurada em vários `eixos` e `tags`. O
campo `eixos:` já existe no frontmatter e já alimenta `indices/grafo.json` — use-o.

---

## 4. O catálogo: o que incluir, como e em que ordem

### 4.1 Primeira onda — os cinco temas já registrados

Ordem recomendada, do mais barato e conectado ao mais caro:

1. **Antropologia** — barata, conecta com quase tudo e entrega o eixo Natureza × Cultura
   que serve de ponte para História, Geografia e Humanidades Ambientais.
2. **História** — estruturante: dá o "quando" a todas as outras lentes. Custa mais
   porque exige recorte (Brasil + mundo, não "tudo").
3. **Geografia** — conecta Economia, História, CTS e a trilha da Confluência.
4. **Ciência Política** — fecha o tripé com Sociologia e Filosofia; exige vocabulário
   institucional.
5. **Economia** — a mais custosa (tentação de virar curso de cálculo) e a mais útil no
   dia a dia; entra como economia política, não como microeconomia.

#### 4.1.1 Antropologia — `antropologia`

- **Pergunta própria:** o que significa ser humano em outra cultura — e o que isso diz
  da nossa?
- **Método:** etnografia, observação participante, comparação.
- **Eixo-ponte:** **Natureza × Cultura** (novo) + Universal × Particular.
- **Conceitos-semente (10):** cultura; alteridade; etnocentrismo; relativismo; trabalho
  de campo; dom e reciprocidade; parentesco; ritual; mito e tabu; corpo e técnicas do
  corpo.
- **Obras de entrada:** Lévi-Strauss, *Raça e História* (curto, ideal); Malinowski,
  *Argonautas do Pacífico Ocidental* (introdução); Roberto DaMatta, *Carnavais,
  Malandros e Heróis*; Darcy Ribeiro, *O Povo Brasileiro* (opcional, aproxima do Brasil).
- **Trilha proposta:** "Estranhar o familiar" — 12 nós, do etnocentrismo à antropologia
  brasileira, fechando no eixo.
- **Conecta com:** Sociologia (cultura, identidade), Psicologia (corpo, self),
  Integrada (nó A1). Já há seis notas em Sociologia com tag `socio-antropologia`.
- **Primeiro passo:** criar o eixo-ponte antes dos conceitos (ver §8).

#### 4.1.2 História — `historia`

- **Pergunta própria:** como as sociedades mudam no tempo — e quem conta essa mudança?
- **Método:** crítica de fontes, periodização, escala (longa duração × evento),
  historiografia.
- **Eixo-ponte:** **Continuidade × Ruptura** (novo) + Memória × História.
- **Conceitos-semente (10):** tempo histórico e longa duração; fonte histórica;
  historiografia e regimes de verdade; memória e esquecimento; evento × estrutura;
  colonialismo; escravidão e abolição; República; ditadura e transição; história
  pública e negacionismo.
- **Obras de entrada:** Marc Bloch, *Apologia da História*; E. H. Carr, *Que é História?*;
  Boris Fausto, *História do Brasil*; Lilia Schwarcz e Heloisa Starling, *Brasil: uma
  biografia* (opcional).
- **Trilha proposta:** "Do documento ao tempo longo" — 12 nós, do ofício do historiador
  ao Brasil republicano.
- **Cuidado:** resistir à cronologia decorada. A trilha ensina o *método*, não a lista
  de reis e datas; o conteúdo factual entra como exemplo.
- **Conecta com:** Filosofia (tempo, verdade), Sociologia (modernidade), Integrada
  (módulo 5), Antropologia (memória).

#### 4.1.3 Geografia — `geografia`

- **Pergunta própria:** como o espaço produz a sociedade e é produzido por ela?
- **Método:** análise espacial, escala, cartografia, trabalho de campo.
- **Eixo-ponte:** **Natureza × Sociedade** (mesmo tronco de Natureza × Cultura) +
  **Local × Global** (novo).
- **Conceitos-semente (10):** espaço geográfico; lugar; território; paisagem; região;
  escala; rede e fluxos; urbanização; globalização; geopolítica e justiça ambiental.
- **Obras de entrada:** Milton Santos, *A Natureza do Espaço* (capítulos iniciais) e
  *Por uma outra globalização*; Yi-Fu Tuan, *Espaço e Lugar*; David Harvey, *Condição
  Pós-Moderna* (cap. sobre compressão espaço-tempo).
- **Trilha proposta:** "Ler o mundo pela escala" — do lugar ao sistema-mundo.
- **Conecta com:** Economia (desenvolvimento regional), História (território e
  fronteiras), CTS (redes e plataformas), Confluência Humano-Tecnológica.

#### 4.1.4 Ciência Política — `ciencia-politica`

- **Pergunta própria:** quem manda, com que autoridade e com que limites?
- **Método:** análise institucional, comparação de regimes, teoria normativa.
- **Eixo-ponte:** **Liberdade × Igualdade** (novo; conversa direto com Rawls/Kant do
  painel) + Público × Privado.
- **Conceitos-semente (10):** poder; Estado; soberania; legitimidade; regime político;
  democracia; autoritarismo; populismo; instituições e federalismo; accountability e
  políticas públicas.
- **Obras de entrada:** Norberto Bobbio, *Estado, Governo, Sociedade*; Weber, "A
  política como vocação"; Robert Dahl, *Poliarquia*; Levitsky e Ziblatt, *Como as
  democracias morrem*; José Murilo de Carvalho, *Cidadania no Brasil*.
- **Trilha proposta:** "Do poder ao regime" — 12 nós, fechando em democracia brasileira.
- **Conecta com:** Filosofia (justiça, contrato), Sociologia (poder, Estado), Direito
  (norma), Integrada (nós C3 e C5).

#### 4.1.5 Economia — `economia`

- **Pergunta própria:** como as sociedades decidem o que produzir, para quem e a que
  custo?
- **Método:** modelos, incentivos, dados; no painel, **sem cálculo** — economia política
  e leitura de conjuntura.
- **Eixo-ponte:** **Mercado × Estado** (novo) + Escassez × Distribuição.
- **Conceitos-semente (10):** escassez e custo de oportunidade; incentivos; oferta e
  demanda; PIB e crescimento; inflação e juros; desemprego; desigualdade (Gini);
  externalidades e bens públicos; desenvolvimento; economia política brasileira.
- **Obras de entrada:** Ha-Joon Chang, *Economia: Modo de Usar* (a melhor porta de
  entrada sem matemática); Thomas Piketty, *O Capital no Século XXI* (introdução);
  Celso Furtado, *Formação Econômica do Brasil*.
- **Trilha proposta:** "Como ler o noticiário econômico" — inflação, juros, emprego,
  câmbio, desigualdade, com um conceito por semana.
- **Conecta com:** Ciência Política (políticas públicas), História (colonialismo,
  industrialização), Geografia (desigualdade regional).
- **Cuidado:** não duplicar Sociologia. "Desigualdade" e "trabalho" já existem lá; aqui
  o recorte é distribuição, incentivo e mensuração.

#### 4.1.6 Psicologia Social — `psicologia-social` (decisão pendente)

Hoje há notas de identidade social, obediência e dissonância **dentro de** Psicologia.
Duas saídas honestas:

- **Promover:** 8 notas próprias (conformidade, atitudes, influência, grupos,
  preconceito, relações intergrupais, comportamento pró-social, self) + trilha. Aí vira
  tema de verdade.
- **Rebaixar:** vira tag `psicologia-social` e um eixo (Indivíduo × Grupo). É o mais
  econômico e o que a regra do zero recomenda enquanto houver menos de 8 notas.

Escolha e **registre a decisão**. Hoje o tema existe no código e não existe no estudo —
o pior dos dois mundos.

### 4.2 Segunda onda — novos temas candidatos

| Área | Slug | O que acrescenta de único | Entra como | Custo |
|---|---|---|---|---|
| **Comunicação e Estudos da Mídia** | `comunicacao` | como a informação é produzida, enquadrada e distribuída | tema (curto prazo) | baixo |
| **Estudos Raciais e Afro-brasileiros** | `estudos-raciais` | raça como estrutura, não como tema de sociologia | tema | médio |
| **Direito** | `direito` | a norma como linguagem do poder; constitucionalismo | tema | médio |
| **Linguística** | `linguistica` | língua, discurso, variação e preconceito linguístico | tema | baixo |
| **Estudos de Gênero** | `estudos-genero` | gênero como categoria de análise, não como recorte | tema | médio |
| **Relações Internacionais** | `relacoes-internacionais` | soberania, guerra, comércio e sistema-mundo | tema (depois de Política e Economia) | médio |
| **Ciência, Tecnologia e Sociedade** | `ciencia-tecnologia-sociedade` | tecnociência, risco, algoritmos, vigilância | tema **ou** eixo Técnica × Política | baixo |
| **Estudos Indígenas** | `estudos-indigenas` | perspectivismo, territorialidade, oralidade | tema | médio |
| **História da Arte** | `historia-arte` | forma, estilo e imagem como documento | tema (repertório) | baixo |
| **Estudos Literários** | `literatura` | texto, gênero, cânone e leitura social | tema (repertório) | baixo |
| **Estudos Religiosos** | `religiao` | sagrado, ritual, secularização e laicidade | tema | médio |
| **Educação** | `educacao` | currículo, reprodução e pedagogia crítica | tema (tardio) | médio |
| **Humanidades Ambientais** | `humanidades-ambientais` | antropoceno, justiça climática, ecologia política | tema ou eixo | baixo |
| **Demografia** | `demografia` | transição, migração, envelhecimento | eixo (Geografia/Economia) | médio |
| **Estudos Urbanos** | `estudos-urbanos` | cidade, segregação, direito à cidade | eixo (Geografia/Sociologia) | baixo |
| **Arqueologia** | `arqueologia` | cultura material e tempo profundo | tag (Antropologia/História) | alto |
| **Estudos Clássicos** | `classicos` | a matriz greco-romana das nossas perguntas | tag (Filosofia/História/Literatura) | baixo |

**Por que Comunicação vem primeiro na segunda onda:** o projeto já tem metade do
caminho andado. A trilha Integrada e a Confluência Humano-Tecnológica já citam Castells,
Zuboff, *O Dilema das Redes* e algoritmos; três ou quatro notas de mídia (indústria
cultural, esfera pública, enquadramento, algoritmo e bolha) transformam o que hoje é
exemplo em conceito com nota própria. É o melhor retorno por hora investida.

**Por que Raça e Gênero são temas e não tags:** ambos têm pergunta, objeto, método e
produção brasileira robusta (Gonzalez, Saffioti, Almeida, Nascimento). Rebaixá-los a
tag de Sociologia é exatamente o erro que o painel já comete ao tratar "gênero" como
uma nota solta. Mas eles entram **depois** de a primeira onda estar de pé — senão
viram mais duas trilhas inacabadas.

**Por que Direito e RI esperam:** são caros (vocabulário próprio, muitas instituições)
e ficam mais baratos depois de Política e Economia, que emprestam os conceitos de
poder, soberania, mercado e instituição.

**Por que CTS pode ser só eixo:** se a pergunta for "quem decide o rumo da técnica?",
ela atravessa Filosofia, Sociologia, Comunicação e Política. Eixo Técnica × Política +
tag `cts` entrega 80% do valor com 20% do custo.

### 4.3 Terceira onda e os "não-temas"

Algumas áreas são excelentes **como lente**, não como disciplina no painel. Elas entram
como tag, eixo ou trilha de repertório:

| Área | Forma de entrada | Por quê |
|---|---|---|
| Musicologia, Artes Cênicas, Cinema | tag em História da Arte/Comunicação; 1 trilha de repertório | o valor está em ver/ouvir, não em encher o painel de fichas |
| Serviço Social, Administração Pública, Jornalismo | eixo aplicado + tag | são formações profissionais; o núcleo teórico já está em Sociologia/Política/Comunicação |
| Turismo, Marketing, Contabilidade | fora do escopo | núcleo técnico, não humanidade interpretativa |
| Teologia confessional | fora; entra "Estudos Religiosos" | o painel estuda religião como fenômeno, não como doutrina |
| Biomedicina, Neurociência | tag em Psicologia | biologia não é humanidade, mas dialoga (e o painel já usa Damásio) |

### 4.4 O caso especial: Pensamento Social Brasileiro

Esta é a adição mais alinhada ao projeto e não está em nenhuma lista acima, porque não é
uma disciplina nova: é um **eixo transversal + trilha**.

- **Pergunta:** por que o Brasil é assim — e quem já tentou responder?
- **Conceitos:** colonização e colonialidade; escravidão e racismo estrutural;
  patrimonialismo; cordialidade (Holanda); homem cordial × cidadão; mestiçagem e
  identidade nacional; desigualdade e elite do atraso; urbanização desigual; democracia
  e autoritarismo; cultura popular e sincretismo.
- **Obras:** Sérgio Buarque de Holanda, *Raízes do Brasil*; Gilberto Freyre, *Casa-Grande
  & Senzala* (com crítica); Jessé Souza, *A Elite do Atraso*; Lélia Gonzalez; Darcy
  Ribeiro.
- **Forma:** um eixo (Brasil × Universal) + uma trilha de 10 nós que puxa notas de
  História, Sociologia, Antropologia, Política e Economia.
- **Por que importa:** o painel hoje é majoritariamente eurocêntrico em autores e
  exemplos. Uma trilha brasileira corrige isso sem criar dez temas novos e dá ao
  projeto uma identidade que manuais importados não têm.

---

## 5. Eixos transversais: a cola entre as áreas

Os cinco eixos atuais (Conflito × Coesão, Estrutura × Agência, Inatismo × Empirismo,
Livre-arbítrio × Determinismo, Mente × Corpo) cobrem bem Filosofia, Psicologia e
Sociologia. Para as novas áreas, faltam as perguntas que fazem as disciplinas
conversarem:

| Eixo novo | A pergunta | Liga |
|---|---|---|
| **Natureza × Cultura** | o que é dado e o que é fabricado? | Antropologia, Geografia, Ambiental, Psicologia |
| **Continuidade × Ruptura** | o que muda e o que permanece? | História, Sociologia, Arte |
| **Universal × Particular** | vale para todos ou só para nós? | Antropologia, Direito, Ética |
| **Liberdade × Igualdade** | os dois valores cabem juntos? | Política, Filosofia, Direito |
| **Mercado × Estado** | quem coordena a vida material? | Economia, Política, História |
| **Local × Global** | que escala explica o fenômeno? | Geografia, RI, Comunicação |
| **Técnica × Política** | quem decide o rumo da técnica? | CTS, Comunicação, Ética |
| **Representação × Realidade** | o que a imagem/texto faz com o real? | Comunicação, Arte, Linguística |
| **Corpo × Sociedade** | como o corpo é marcado e disciplinado? | Gênero, Antropologia, Psicologia, História |

Regras para não inflar: **teto de ~15 eixos no total**; cada eixo precisa de **pelo menos
três notas** ligadas a ele para existir; e todo tema novo nasce com **um eixo-ponte
obrigatório**.

---

## 6. Roadmap de 12 meses

O plano abaixo pressupõe ~3 h/semana. Se a rotina mudar, o prazo muda — a ordem não.

| Fase | Quando | Entrega | Horas |
|---|---|---|---|
| **0. Decidir** | semana 1 | preencher as três decisões do §11; escolher o 1º tema | 1 h |
| **1. Fechar o ciclo** | mês 1 | 5 notas `ok` + 1 ficha + 1 diário (Guia 07, Fase 1) + eixo **Natureza × Cultura** | 8 h |
| **2. Antropologia** | meses 2–3 | 8 notas (4 `ok`), trilha de 12 nós, 1 ficha, 1 diário | 18 h |
| **3. História** | meses 4–6 | 8 notas (4 `ok`), trilha, 1 ficha, eixo **Continuidade × Ruptura** | 20 h |
| **4. Geografia + Política** | meses 7–9 | 6 notas em cada, 1 trilha cada, eixos Local × Global e Liberdade × Igualdade | 24 h |
| **5. Economia + Brasil** | meses 10–12 | 6 notas de Economia, trilha "noticiário", eixo Mercado × Estado e trilha **Pensamento Social Brasileiro** | 24 h |

O que **não** está no roadmap: converter os 100+ PDFs, criar 20 temas, migrar o site.
Isso é o Guia 07 dizendo "não" — e este guia concorda.

Por que Antropologia antes de História: ela custa metade, entrega o eixo que serve de
ponte para História/Geografia e tem clássicos curtos (*Raça e História* tem menos de 100
páginas). É o teste de baixo risco do método de expansão: se você não terminar
Antropologia, não termine História — e economizou seis meses.

---

## 7. Como o site e o painel precisam mudar (depois do conteúdo)

Nada aqui é urgente, mas duas mudanças ficam baratas se planejadas agora:

1. **Famílias na tabela e no site.** Uma coluna "Família" (ou abas por família) só faz
   sentido quando houver 15+ temas ativos. Antes disso, é UI para esconder ausência de
   conteúdo.
2. **Filtros por eixo e por estado.** O `indice.json` já carrega `eixos` e `status`;
   falta só expor. Quando existirem 3+ temas ativos, vale uma PR de 1 dia.

O que **não** fazer: reescrever o gerador de site para acomodar temas que ainda não
têm notas. O gargalo é texto.

---

## 8. Receita técnica: abrir um tema novo em 8 passos

Use Antropologia como exemplo. Tempo: ~1 h de infra + o tempo de escrever.

1. **Eixo-ponte primeiro.**
   ```bash
   python -m scripts.painel nova --tipo eixo --nome "Natureza × Cultura" --tema antropologia
   ```
   Preencha "A questão em uma frase" e duas posições no debate. Sem isso, o tema nasce
   ilha.
2. **Uma nota por vez, com fonte declarada.**
   ```bash
   python -m scripts.painel nova --tipo conceito --nome "Etnocentrismo" --tema antropologia
   ```
   Nasce `rascunho`. Ela só vira `ok` quando tiver definição de uma frase, explicação
   sua, exemplo brasileiro, citação com capítulo/página e conexão interdisciplinar.
3. **Pendure a nota nos eixos e tags certos** (`eixos: [natureza-cultura]`), para o
   grafo não ficar órfão.
4. **Trilha semente** em `trilhas/antropologia-nivel-1.md` (copie `template-trilha.md`),
   com 12 nós e um nó final de síntese no diário.
5. **Ficha de leitura** da obra de entrada em `acervo/fichas/` — a ficha é o que impede
   a trilha de virar colagem de resumos de IA.
6. **Se o slug é novo** (Direito, RI, etc.), acrescente em `TEMAS`, em
   `scripts/painel/modelo.py`, e só faça isso quando o tema já tiver pelo menos uma nota
   ou trilha — pela regra do zero.
7. **Rode e confira:**
   ```bash
   python -m scripts.painel auditar
   python -m scripts.painel tudo
   python -m scripts.painel tudo   # segunda vez não deve mudar nada
   ```
8. **PR com a seção de sempre:** o que mudou / decisões / verificação / limitações.

### 8.1 Slugs reservados (para não inventar nome na hora)

| Nome de exibição | Slug |
|---|---|
| Direito | `direito` |
| Relações Internacionais | `relacoes-internacionais` |
| Linguística | `linguistica` |
| Comunicação e Mídia | `comunicacao` |
| Estudos de Gênero | `estudos-genero` |
| Estudos Raciais e Afro-brasileiros | `estudos-raciais` |
| Estudos Indígenas | `estudos-indigenas` |
| História da Arte | `historia-arte` |
| Estudos Literários | `literatura` |
| Estudos Religiosos | `religiao` |
| Educação | `educacao` |
| Humanidades Ambientais | `humanidades-ambientais` |
| Ciência, Tecnologia e Sociedade | `ciencia-tecnologia-sociedade` |
| Demografia | `demografia` |
| Estudos Urbanos | `estudos-urbanos` |
| Arqueologia | `arqueologia` |
| Estudos Clássicos | `classicos` |

Bloco pronto para `modelo.py`, quando a segunda onda começar (não adicione antes):

```python
TEMAS = {
    # ... os 10 atuais ...
    "comunicacao": "Comunicação e Mídia",
    "estudos-raciais": "Estudos Raciais e Afro-brasileiros",
    "direito": "Direito",
    "linguistica": "Linguística",
    "estudos-genero": "Estudos de Gênero",
    "relacoes-internacionais": "Relações Internacionais",
    "ciencia-tecnologia-sociedade": "Ciência, Tecnologia e Sociedade",
    "estudos-indigenas": "Estudos Indígenas",
    "historia-arte": "História da Arte",
    "literatura": "Estudos Literários",
    "religiao": "Estudos Religiosos",
    "educacao": "Educação",
    "humanidades-ambientais": "Humanidades Ambientais",
}
```

### 8.2 Vocabulário de tags (para o site conseguir cruzar temas depois)

Mantenha as tags em minúsculas, sem acento, com prefixo quando o tipo importar:

| Prefixo | Uso | Exemplo |
|---|---|---|
| *(tema)* | sempre a primeira tag | `antropologia` |
| `autor-` | autor estudado | `autor-levi-strauss` |
| `escola-` | corrente | `escola-estruturalismo` |
| `pais-` | recorte nacional | `pais-brasil` |
| `seculo-` | período | `seculo-xx` |
| `metodo-` | abordagem | `metodo-etnografia` |

Isso permite, no futuro, uma view "todo o painel por método" sem uma linha de código
nova no gerador — só leitura de `indice.json`.

---

## 9. Riscos e antídotos

| Risco | Como aparece | Antídoto |
|---|---|---|
| **Dispersão** | 20 temas, 0 trilhas concluídas | teto de 2 temas em expansão + regra do zero |
| **Rascunho infinito** | 150 notas geradas por IA, todas `rascunho` | 8 notas por tema; 1 reescrita por semana antes de abrir outra |
| **Ilha** | tema sem conexão com o resto do grafo | eixo-ponte obrigatório antes do primeiro conceito |
| **Fonte frágil** | trilha montada só em resumo de site | 2 obras de entrada + 1 ficha antes de publicar a trilha |
| **Eurocentrismo** | só autores europeus e exemplos importados | cota: 1/3 de autores brasileiros/latino-americanos por tema + trilha Brasil |
| **Direitos autorais** | texto integral em repositório público | acervo segue privado; site publica só notas próprias |
| **Sobrecarga do painel** | tabela com 25 linhas e 20 "Em breve" | famílias + filtrar temas sem conteúdo |
| **Taxonomia zumbi** | tema que ninguém estuda há 6 meses | poda registrada: volta a eixo/tag ou vira "planejado" |

---

## 10. Métricas de sucesso (e as que enganam)

Meça:

- **notas `ok` por tema** — a única prova de que a expansão ensinou algo;
- **eixos com ≥ 3 notas ligadas** — a prova de que o tema não é ilha;
- **temas com trilha iniciada e ≥ 1 nó concluído**;
- **proporção de fontes brasileiras/latino-americanas** — meta: ≥ 1/3;
- **tempo entre criar e reescrever uma nota** — se cresce, o acervo está virando
  depósito.

Não meça (ou meça só como curiosidade): número de temas, número de notas, número de
PDFs convertidos. O `progresso.md` já cobre os números que importam; este guia só
acrescenta o corte por tema.

---

## 11. Três decisões que são suas

Nenhuma delas é técnica. Responda por escrito aqui (ou no Guia 07) e a expansão deixa
de ser intenção.

1. **Ritmo:** um tema novo por trimestre ou por semestre? (recomendo trimestre, com teto
   de dois simultâneos)
2. **Primeiro tema:** Antropologia (barato e conectado), História (estruturante e caro),
   Geografia ou Política? (recomendo Antropologia)
3. **Profundidade Brasil:** a trilha Pensamento Social Brasileiro entra no primeiro ano
   ou fica para o segundo? (recomendo primeiro ano — é o que dá identidade ao painel)

### Registro de decisões

| Data | Decisão | Evidência | Reavaliar quando |
|---|---|---|---|
| 2026-10-23 | Mapa criado com 7 famílias, 5 temas de primeira onda e 14 candidatos | 6 de 10 temas vazios; 0 notas `ok` | houver 10 notas `ok` e 2 temas ativos |
|  |  |  |  |

---

## 12. O que já está pronto e o que falta

**Pronto:** taxonomia de temas no código; templates de conceito, eixo, trilha e ficha;
auditoria e CI; painel gerado; este mapa com critérios, ordem e receita.

**Falta, em ordem:** (1) as três decisões do §11; (2) o eixo Natureza × Cultura;
(3) a primeira nota de Antropologia; (4) a trilha de Antropologia; (5) a ficha de
*Raça e História*; (6) a primeira entrada de diário do tema novo.

Repare que os itens 2 a 6 são **conteúdo**, não infraestrutura. É sempre assim neste
projeto — e é por isso que ele funciona.
