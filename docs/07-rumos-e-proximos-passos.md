# Guia 07 — Rumos: o que fazer depois da fundação

Este guia é o plano de voo do projeto depois da limpeza e da automação.
O diagnóstico completo (pontos fortes, riscos e evidências) está em
[`arquivo/analise-2026-10-21.md`](arquivo/analise-2026-10-21.md) — registro histórico; não é plano vigente.

## Princípio

> O projeto não precisa de mais notas. Precisa de **notas reescritas**, de
> **citações verificáveis** e de **diário**. Tudo o mais é infraestrutura.

A métrica-norte é `notas com status: ok + entradas de diário`, visível em
[`progresso.md`](../progresso.md). Número de PDFs convertidos não é progresso.

## Fase 1 — Fechar o ciclo de estudo (agora, ~2 semanas)

O objetivo é provar que o método funciona em **uma** nota, com qualidade de padrão-ouro,
e só depois escalar.

1. **Escolher a obra da vez**: Mills, *A Imaginação Sociológica* (livro nº 1 do
   [Guia 05](05-prioridades-de-leitura.md); cobre os nós 1 e 12 de Sociologia e dois da Integrada).
2. **Escrever a ficha de leitura** em `acervo/fichas/mills-imaginacao-sociologica-ficha.md`
   usando o `template-livro.md`.
3. **Reescrever 5 notas** sem consultar a IA enquanto escreve (compare depois):
   - `sociologia-imaginacao-sociologica.md`
   - `eixo-conflito-coesao.md`
   - `sociologia-fato-social.md`
   - `sociologia-alienacao.md`
   - `sociologia-racionalizacao.md`
4. **Padrão-ouro de cada nota** (é o que muda o `status` para `ok`):
   - definição em uma frase que caiba num cartão;
   - explicação com as suas palavras + **um exemplo brasileiro**;
   - citação literal com **capítulo e página** (ou "sem citação — fonte secundária");
   - pelo menos uma conexão interdisciplinar com o *porquê*;
   - posição no(s) eixo(s) correspondente(s).
5. **Escrever a primeira entrada do diário** em `diario/AAAA-MM-DD-sociologia-imaginacao.md`.
6. Rodar `make auditar` e conferir o `progresso.md`: 5 notas `ok`, 1 ficha, 1 diário.

## Fase 2 — Jardim público (30–60 dias) — **infraestrutura pronta**

O site está montado: **painel inicial gerado** (cartões de progresso, trilhas com
barra e próximo nó, temas, pendências, diário), abas de navegação, busca em
português e tags. Falta ligar a publicação e escrever o conteúdo.

**Publicar (5 minutos):**

1. **Settings → Pages → Build and deployment → Source: GitHub Actions**.
2. **Actions → "Site — publicar no GitHub Pages" → Run workflow**.
3. O site fica em `https://<usuario>.github.io/humanitas/`.

**Testar antes de publicar:**

```bash
make site          # serve em http://127.0.0.1:8000
```

O `make site` monta `site-src/` só com o que pode ser público — nunca o texto
integral do acervo nem `docs/anexos/`. O workflow roda a auditoria antes de
publicar, então link quebrado não vai para o ar.

**O que ainda depende de você (e só de você):**

- 20 notas `ok` antes de divulgar o link (hoje: 0). Publicar 36 rascunhos de IA
  contradiz a tese do projeto — a licença CC BY-SA já está pronta para quando
  houver conteúdo autoral.
- Um `index` que funcione como porta de entrada: o README já serve, mas vale
  escrever "por onde começar" em 5 linhas quando as trilhas tiverem progresso real.
- Fichas de leitura: o site já publica `acervo/fichas/`; com 0 fichas, a seção
  aparece vazia.

Métrica de saída da fase: 20 notas `ok`, 8 entradas de diário, 1 trilha em 30%.

## Fase 2.5 — Conteúdo antes de produto

Antes de qualquer app, quiz ou XP, o gargalo é escrever. Use as ferramentas:

```bash
make pendencias                        # o que falta em cada nota
make nova TIPO=conceito NOME="Habitus" TEMA=sociologia
```

## Fase 3 — Escolher **um** caminho (90 dias)

Só depois de ter conteúdo, escolha **um** com base no sinal que o uso der:

| Caminho | Quando escolher | Primeiro passo |
|---|---|---|
| **A. Aprofundar o painel** (recomendado) | Você usa o site quase todo dia | Fechar 2 trilhas e converter 3 livros-chave |
| **B. Ferramenta para outras pessoas** | Você quer que o pipeline sirva a outros | Empacotar o CLI (`pipx`), documentar em inglês, exemplos |
| **C. Curso / produto** | Você já concluiu 2–3 trilhas e sabe o que funciona | Transformar uma trilha em curso com quiz e progresso |
| **D. Tutor com IA (RAG)** | O gargalo é revisar, não escrever | SQLite FTS5 + embeddings locais, resposta sempre com citação do arquivo |

### Regras para o caminho D (IA de consulta), se for por ele

- A resposta **deve citar** a nota e a seção; nunca gerar conteúdo sem fonte no painel.
- A IA pode gerar **perguntas** e localizar trechos — nunca escrever o diário.
- Preferir busca local (FTS5/Pagefind) antes de qualquer LLM: 90% do valor, custo zero.

## Fase 4 — Ferramenta do site: quando migrar

A publicação do painel é infraestrutura, não o projeto. Hoje ela usa **MkDocs
Material** com painel inicial gerado; existem outras duas ferramentas possíveis,
com papéis diferentes — e uma não substitui a outra.

| | **MkDocs Material** (atual) | **Obsidian** (local) | **Astro** (site próprio) |
|---|---|---|---|
| Para quê | publicar o painel | ler, escrever e revisar | publicar com UI sob medida |
| Como se usa | `mkdocs.yml` + Markdown | abrir a pasta do repositório | projeto JS (componentes `.astro`) |
| Controle de UI | o que o tema permite (CSS) | painéis, grafo, plugins | total |
| Busca | plugin em português | instantânea, local | Pagefind |
| Como lê os dados | Python gera o Markdown | lê o frontmatter direto | lê `indices/indice.json` |
| Esforço para empatar | ~1 dia (feito) | 30 min | 1–2 semanas |
| Custo de manutenção | zero dependência nova | app gratuito (Publish é pago) | Node, dependências, build |
| Texto integral do acervo | fora do site | **abre localmente** | fora do site |

### Gatilhos de decisão — Astro

Migrar **somente** quando as três condições forem verdadeiras ao mesmo tempo:

1. **Conteúdo**: ≥ 25 notas com `status: ok` **e** ≥ 12 entradas de diário
   (números reais em [`progresso.md`](../progresso.md)) — senão é uma vitrine vazia;
2. **Lacuna concreta**: falta algo que o Material não faz e que você **usa de fato**
   — heatmap dos dias de estudo, filtro interativo ("só rascunhos"), gráfico de
   evolução, quiz embutido;
3. **Uso real**: o site publicado já é usado para estudar, não só para mostrar.

Se qualquer uma for falsa, **não migre** — volte para a Fase 1 e escreva notas.

### Gatilhos de decisão — Obsidian

Adotar quando você quiser **grafo, backlinks e revisão espaçada sobre os mesmos
arquivos**, sem publicar nada. Não substitui o site: é o "modo local".

- **Gatilho:** você quer ver "quem linka para esta nota", abrir o acervo protegido
  com conforto, ou revisar com o plugin *Spaced Repetition* — e isso não vale um
  projeto novo.
- **Custo:** abrir a pasta no app (30 min). Nenhuma mudança nos arquivos.
- **Risco:** criar nota fora do padrão (sem `status`, sem `tema`). O
  `python -m scripts.painel auditar` e o CI já pegam isso.

### Não gatilhos (parecem, mas não são)

- "Quero um site mais bonito" — o Material com dashboard já entrega isso.
- "O Astro é o que todo mundo usa" — irrelevante para um painel pessoal.
- Fazer os dois em paralelo (Pages + Astro): em duas semanas as saídas divergem.
- Migrar durante um período de estudo — trocar ferramenta no meio de uma trilha
  é a forma mais elegante de não terminá-la.

### Se migrar, como migrar sem perder nada

1. Rodar o Astro **em paralelo, lendo `site-src/`**, por uma semana, sem desligar o Material.
2. O `indices/indice.json` é a API do site: notas, pendências, trilhas e progresso
   já vêm prontos — nada de reprocessar Markdown no front-end.
3. `scripts/painel.py` continua sendo o **único dono dos dados**; o Astro só desenha.
4. Só desligar o Material quando busca, tags, painel e links estiverem equivalentes.

### Decisão registrada

| Data | Decisão | Gatilho | Situação |
|---|---|---|---|
| 2026-10-21 | Manter **MkDocs Material** com painel gerado | 0 notas `ok`, 0 diários | Reavaliar quando ≥ 25 `ok` e ≥ 12 diários |

Ao reavaliar, atualize esta tabela com a data e os números do dia — decisão sem
evidência registrada vira preferência.

Os números dos gatilhos **não são conferidos à mão**: o `progresso.md` tem uma
seção "Marcos de decisão" com atual/alvo/situação de cada um (gerada por
`python -m scripts.painel progresso`, ou pelo CI a cada push).

## O que não fazer

- Converter os 100+ PDFs "para depois".
- Construir gamificação/XP antes de ter notas reescritas: gamificar rascunhos de IA gamifica o vazio.
- Versionar texto integral em repositório público.
- Criar notas novas antes de fechar as lacunas (citação, exemplo, eixo) das existentes.
- Deixar o diário ser gerado por IA — é o único ativo que não pode ser terceirizado.
- Trocar a ferramenta do site (ver Fase 4) antes de ter conteúdo: o painel já existe;
  o que falta são notas reescritas.

## Backlog priorizado

A lista gerada de marcos e métricas está em [`progresso.md`](../progresso.md). Abaixo ficam apenas os próximos passos manuais (não duplicam o progresso gerado).

| Prioridade | Item | Esforço |
|---|---|---|
| P1 | Habilitar branch protection exigindo o CI verde em `main` | 10 min |
| P1 | ~~Decidir o primeiro tema da expansão~~ — **feito**: Antropologia, depois História ([Guia 09](09-mapa-das-humanidades.md), §11) | 30 min |
| P2 | ~~Regra do zero: tirar do README os temas sem nota/trilha~~ — **feito em 2026-10-23** ([Guia 09](09-mapa-das-humanidades.md), §2.3) | 1 h |
| P2 | Conversor por capítulo (arquivos menores, melhor busca) | 1 dia |
| P2 | `pre-commit` rodando `auditar` antes de cada commit | 1 h |
| P2 | Fichas de leitura de *Raça e História* e *Apologia da História* (Guia 09, §12) | 3 h |

## Como medir (sem autoengano)

O progresso atualizado está sempre em [`progresso.md`](../progresso.md), gerado por `python -m scripts.painel progresso`. Use-o como única fonte de números; não mantenha contagens manuais aqui.

```bash
python -m scripts.painel progresso && sed -n '1,25p' progresso.md
```
