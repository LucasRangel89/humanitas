# Análise do projeto Humanitas — diagnóstico, correções e rumos

> Análise feita em 21/10/2026 sobre o commit `fe2b3ef` (branch `main`).
> Métodos: leitura integral dos guias e templates, execução do notebook `atualizador-do-painel` contra o repositório real, checagem automática de frontmatter, links, duplicatas (hash) e consulta à API do GitHub.

> **Status (atualizado em 21/10/2026):** as correções P0 e as implementações P1
> **já foram aplicadas** — limpeza das duplicatas, `.gitignore` (acervo fora do Git),
> licenças, CLI `scripts/painel.py` com 33 testes, auditoria bloqueante no CI,
> `progresso.md` e GitHub Actions. O que segue pendente é o trabalho de estudo:
> reescrever notas com fonte primária e citação, escrever fichas e diário.
> Plano de voo em [`07-rumos-e-proximos-passos.md`](07-rumos-e-proximos-passos.md).
> Este documento é mantido como registro do diagnóstico original — os números
> abaixo descrevem o estado **antes** das correções.

---

## 1. Resumo executivo

O Humanitas é **um dos projetos de estudo autodidata mais bem concebidos que se vê em um repositório**: a tese (não é um resumo de PDFs, é um *painel de conceitos interligado por eixos de debate*), a documentação em português e a arquitetura de conteúdo (`conceito` / `eixo` / `trilha` / `diário`) são de nível profissional. O problema não está na concepção — está na **execução**: o repositório hoje conta duas histórias (uma de 36 notas, outra de 18), a automação é um ciclo manual de zip-download-upload, e a base de notas é derivada de um guia secundário **sem uma única citação com página**. O projeto está mais bem documentado do que praticado.

| Dimensão | Nota | Comentário curto |
|---|---|---|
| Concepção pedagógica | **9/10** | Eixos como bússola + diário humano + trilhas com critério de conclusão é uma síntese original |
| Documentação / onboarding | **9/10** | 5 guias, ~7.500 palavras, zero jargão; falta uma página de "comandos" |
| Arquitetura de conteúdo | **8/10** | Modelo de dados coerente, mas o template não é seguido pelas notas |
| Qualidade do conteúdo atual | **5/10** | Uniforme demais, sem trechos/páginas, 100% em `rascunho`, fonte secundária |
| Engenharia / automação | **3/10** | Colab + zip + upload manual; bug que apaga dados do índice; auditoria incompleta |
| Higiene do repositório | **2/10** | 38 dos 39 arquivos da raiz são duplicatas; snapshot antigo aninhado; sem `.gitignore` nem licença |
| Postura jurídica | **3/10** | O README manda manter privado, mas o repositório é **público** hoje |
| Produto / experiência | **4/10** | Sem busca, sem site, tags 100% mortas, nenhuma métrica de progresso |

**Os quatro riscos que podem matar o projeto** (em ordem de urgência):

1. **Perder trabalho editando a cópia errada** — há 18 notas e 5 trilhas duplicadas na raiz, defasadas em relação a `conceitos/` e `trilhas/`.
2. **Publicar acervo protegido sem perceber** — o repositório está público e o fluxo prevê colocar texto integral de livros em `acervo/`.
3. **Virar coleção sem estudo** — 36 notas `rascunho`, 0 diários, 0 fichas, 0 trechos, 0 nós concluídos. É exatamente o "anti-colecionismo" que o próprio Guia 02 alerta.
4. **Automação que se degrada** — o ciclo manual tem quatro pontos de falha e o conversor **sobrescreve** o índice completo com um índice pobre.

---

## 2. Inventário verificado (o que existe de fato)

| Item | Quantidade real | Observação |
|---|---|---|
| Arquivos rastreados no Git | 123 | dos quais **38 são duplicatas exatas** de arquivos em subpastas (2,1 MB) |
| Notas de conceito | 36 | Sociologia 14 · Filosofia 11 · Psicologia 11 (sendo 5 delas eixos) |
| Eixos (`tipo: eixo`) | 5 | Mente × Corpo, Livre-arbítrio × Determinismo, Inatismo × Empirismo, Conflito × Coesão, Estrutura × Agência |
| Palavras nas notas | 13.927 | mediana de **427 palavras/nota** (mín. 323, máx. 480) |
| Palavras nos guias | 7.551 | README + Guias 01–05 |
| Trilhas | 5 | 56 nós no total, **0 concluídos** |
| Fichas de leitura em `acervo/` | **0** | só o README da pasta |
| Trechos em `trechos/` | **0** | template existe, pasta vazia |
| Diários em `diario/` | **0** | template existe, pasta vazia |
| `indice.json` | vazio (`livros: []`, `conceitos: []`, `atualizado_em: null`) | e existe em **dois** lugares (raiz e `indices/`) |
| Links quebrados nas 36 notas + 5 trilhas | **0** | o único "quebrado" de `conceitos/` está no README, como exemplo de sintaxe |
| Links quebrados nos arquivos duplicados da raiz | **113** | prova de que a raiz é lixo defasado |
| Notas com fonte secundária | **17 de 36** | declaram origem em "Guia de Estudos Integrativo (anexo)" ou "Planos de estudo" |
| Notas com trecho literal + capítulo/página | **0 de 36** | nenhuma |
| Seções do template ausentes | `Onde aparece na obra`, `Trecho de apoio`, `Exemplos que ilustram` — **31/31 notas** | o template não é seguido |
| Uso de `status` | 36 `rascunho`, 0 `ok` | e o script não contabiliza esse campo |
| Repositório no GitHub | `LucasRangel89/humanitas`, **público**, sem licença | verificado via API em 21/10/2026 |

---

## 3. Pontos positivos

1. **A tese do projeto é forte e não óbvia.** "Painel de conceitos, não pilha de resumos" é uma resposta madura ao problema real de quem estuda sozinho: a informação existe, a *ligação* entre ela não.
2. **Os eixos são a melhor ideia do repositório.** `eixo-mente-corpo.md` e `eixo-livre-arbitrio-determinismo.md` têm tabela de posições com autor/obra/nota e uma pergunta operacional ("onde esta teoria fica neste eixo?"). É isso que transforma uma enciclopédia em espinha dorsal de estudo — e é raro em projetos do tipo.
3. **Documentação de altíssimo nível, em PT-BR, para não-programador.** O Guia 02 é honesto até no que costuma ser escondido: compara ferramentas *com as limitações*, desaconselha gastar dinheiro e alerta contra converter 100 PDFs de uma vez.
4. **Separação correta de granularidades.** Conceito (1 ideia/arquivo), trecho (citação + comentário), ficha (obra), eixo (debate), trilha (sequência), diário (síntese pessoal). Cada camada tem um propósito claro, e você escreveu o critério de cada uma (ex.: "trecho sem comentário é recorte; com comentário é estudo").
5. **Consistência de metadados.** As 36 notas usam exatamente o mesmo esquema de frontmatter (8 chaves: `conceito|eixo`, `obra_origem`, `autor_origem`, `tema`, `tipo`, `nivel`, `status`, `tags`) e os 3 temas batem com a tabela do README. Isso é o que permite automatizar depois.
6. **Núcleo de links íntegro.** 0 links quebrados nas 36 notas e nas 5 trilhas — todos os alvos existem e as 36 notas são citadas em alguma trilha. A convenção Markdown relativa — em vez de `[[wikilinks]]` — foi escolha acertada (funciona no GitHub *e* no Obsidian).
7. **Trilhas com critério de conclusão verificável.** "Explicar em voz alta + quiz + diário" é avaliação de verdade, não "li o capítulo". As cinco trilhas estão justificadas a partir dos planos anexados, com a Integrada explicitando duas rotas.
8. **O diário é o antídoto contra a própria IA.** "A única parte do painel que a IA nunca escreve por você" é a regra que salva o projeto de virar um gerador de resumos.
9. **Estratégia híbrida + Guia 05.** Escolher 10 livros-chave por evidência (cruzamento dos planos) e converter por demanda é a decisão de escopo mais madura do repositório.
10. **O atualizador já resolve o essencial.** Regenera índice, tabela idempotente por marcadores `<!-- PAINEL-TEMAS-INICIO/FIM -->`, checa links, detecta duplicados e gera flashcards — e roda de fato (testei: 36 conceitos, 36 cartões, relatório "Painel limpo"). A tabela regenerada bate com a do README.
11. **Curadoria de custo zero.** GitHub + Colab + NotebookLM + Anki + Obsidian, todos gratuitos, com papéis bem definidos — decisão certa para um projeto pessoal.
12. **O blueprint já existe.** Ter um destino desenhado (Humanitas Explore, em `docs/anexos/`) e mantê-lo como "futuro" no roadmap protege o presente do escopo.

---

## 4. Pontos negativos e riscos

### 4.1 Higiene do repositório (crítico, 10 minutos para resolver)

- **38 dos 39 arquivos da raiz são duplicatas exatas** de arquivos que já estão em `conceitos/`, `trilhas/`, `docs/`, `templates/` e `notebooks/`. Só o `README.md` da raiz é único.
- As cópias da raiz **estão defasadas**: faltam 6 notas existentes em `conceitos/` (ex.: `filosofia-morte-de-deus.md`, `eixo-livre-arbitrio-determinismo.md`), e elas geram **113 links quebrados** porque apontam para irmãos de pasta que não existem na raiz.
- A pasta **`painel-ciencias-humanas/` é um snapshot inteiro e antigo do repositório**, com README anterior (tabela sem Psicologia), notebooks e docs — três cópias de cada notebook no total.
- **Sem `.gitignore`**: quando `acervo/` for populado, texto integral de livros e PDFs entram no histórico (e no tamanho do repo) sem nenhum filtro.
- **Sem licença.** Sem `LICENSE`, ninguém pode reutilizar suas notas — o padrão legal é "todos os direitos reservados", o oposto da intenção declarada de "compartilhar as notas quando quiser".
- **PDFs e `.docx` versionados em dois lugares** (raiz + `docs/anexos/`): 4,1 MB, metade duplicada. A `grade-curricular-psicologia.pdf` fica solta na raiz.
- **Dois `indice.json`** (raiz e `indices/`), ambos vazios; a documentação diz que o canônico é `indices/indice.json`. O da raiz só existe para confundir.

### 4.2 Automação: frágil, manual e com um bug que apaga dados

- **O ciclo de manutenção é 100% manual**: baixar ZIP do GitHub → subir no Colab → executar → baixar ZIP → descompactar → arrastar 4 arquivos de volta. São quatro pontos de falha por rodada, e nada impede esquecer uma etapa. Para uma tarefa mensal, é aceitável; para uma tarefa semanal (que o próprio Guia 02 recomenda), não é.
- **Bug real de schema no conversor** (`notebooks/converter-pdfs.ipynb`, célula 5): ele grava um `indice.json` contendo **apenas** `livros` — e o Guia 02 manda colocar esse arquivo em `indices/`. Resultado: a primeira conversão depois de uma rodada do atualizador **apaga** `conceitos`, `trechos` e `fichas` do índice. Os dois notebooks têm contratos de dados incompatíveis.
- **Contagem dupla de livros** (`atualizador`, célula 4): as fichas são somadas a `livros_tema`. Uma obra com ficha + texto integral conta 2 na coluna "Livros processados".
- **A auditoria não olha onde os links mais importam.** Ela varre `conceitos/`, `trechos/` e `acervo/`, mas **não** `trilhas/`, `diario/`, `README.md` nem `docs/` — justamente os arquivos que apontam para todas as notas. Um link quebrado em `trilhas/` passa batido.
- **Detecção de duplicados com índice desalinhado**: `nomes` é filtrado por `if r['conceito']`, mas depois indexado em `registros['conceitos'][i]`. Basta uma nota sem nome para comparar as notas erradas.
- **Nenhuma validação de frontmatter.** `tema: histórria`, `nivel: avancado` (grafia inconsistente), campo faltando ou `status` inventado não geram erro — viram lixo silencioso no índice.
- **O notebook não mede progresso.** Ele não lê os checkboxes das trilhas, não conta `status: rascunho` vs `ok`, não conta entradas de diário. Ou seja: o painel diz quantas notas existem, nunca **quanto você aprendeu** — que é a métrica que importa neste projeto.
- **Conversor sem incrementalidade nem limpeza**: reconverte tudo sempre, não deduplica por hash, não remove cabeçalho/rodapé de página, não separa por capítulo e gera **um arquivo único por livro** (um manual de 700 páginas vira ~2 MB de Markdown — lento no GitHub, inútil para busca por trecho).
- **Título gerado por `stem.title()`** produz "Carr O Que E Historia" em vez de "O que é História" — e o índice nasce com metadados ruins que depois ninguém corrige.
- **Dependência sem versão** (`!pip install -q pymupdf4llm`): a API da biblioteca já mudou entre versões; um dia o notebook "quebra sozinho" e o usuário não-programador não saberá por quê.
- **Zero testes e zero CI.** Nenhum arquivo de `requirements`, nenhum teste do parser de frontmatter (que é a peça mais crítica).
- **Flashcards pobres**: 36 cartões, todos com a mesma forma ("O que é X?" → definição). Sem ID estável, reimportar no Anki **duplica** os cartões; sem deck/tag mapeada; e os 5 eixos (que têm "A questão em uma frase") não geram cartão nenhum.

### 4.3 Conteúdo e epistemologia (o risco mais sério de médio prazo)

- **A base não vem do acervo — vem de um derivado dele.** 17 das 36 notas declaram `obra_origem: "Guia de Estudos Integrativo (anexo do autor)"` ou "Planos de estudo"; uma cita "fonte didática: Wikipédia" e admite "confirmar em obra primária". O README afirma que as notas são produzidas "a partir do acervo" — hoje elas são notas *sobre um guia de estudo*, não sobre livros. Isso não é pecado, mas precisa ser dito com clareza (e corrigido quando as obras entrarem).
- **Nenhuma citação literal com capítulo/página em 36 notas.** O template pede "Trecho de apoio"; **31 de 31 notas de conceito não têm essa seção**. Sem ancoragem, não há como verificar uma afirmação nem voltar ao texto — e o projeto perde exatamente a vantagem que justifica converter PDFs em Markdown.
- **Uniformidade suspeita.** Todas as notas têm entre 323 e 480 palavras, a mesma sequência de seções, o mesmo rótulo "(rascunho — reescrever)" e o mesmo tom. Isso é assinatura de geração em lote, não de reescrita. O risco pedagógico é o "efeito fluência": o texto parece seu, mas não passou pela sua cabeça.
- **As três camadas mais autorais estão vazias.** `acervo/` (0 fichas), `trechos/` (0), `diario/` (0). O projeto construiu o andaime completo e ainda não subiu nele. O roadmap também está 100% desmarcado — inclusive "Criar o repositório", que já existe.
- **O template promete o que as notas não entregam.** `template-conceito.md` tem 8 seções; as notas têm 6 e trocam "Onde aparece na obra / Trecho de apoio / Exemplos" por "Autores e obras para aprofundar". Ou o template é aspiracional (e deveria marcar o que é opcional), ou as notas estão incompletas. Hoje o leitor não sabe qual é o padrão.
- **Cobertura desequilibrada frente à promessa.** O README anuncia história, ciência política, antropologia, economia e geografia; há **zero** notas nelas. 11 das 36 notas são de psicologia (e 3 das 5 trilhas). O projeto é, na prática, "psicologia + sociologia + filosofia", guiado por um guia anexo de psicologia.
- **Sem campo de confiança/contestação.** Não existe forma de registrar "isto é consenso", "isto é interpretação de X" ou "isto foi criticado por Y" — e em ciências humanas essa distinção é o conteúdo.
- **Inconsistência documental**: o Guia 02 manda salvar fichas em `acervo/fichas/`; o README de `acervo/` diz para salvar no próprio `acervo/` com sufixo `-ficha.md`. O notebook aceita os dois, mas o leitor não sabe qual seguir.

### 4.4 Jurídico e privacidade (sensível, e hoje já é um problema)

- O README e o Guia 01 recomendam **repositório privado** por causa do texto integral em `acervo/`. O repositório, porém, está **público** (`private: false` na API do GitHub). Hoje `acervo/` está vazio, então a exposição atual é "só" dos PDFs de planos/grade curricular e do `.docx` — mas **no dia em que o primeiro livro convertido entrar, ele será publicado**.
- A regra precisa ser técnica, não uma recomendação em texto: `acervo/` deve estar no `.gitignore` (ou em repositório separado/privado), com o texto morando no Drive e apenas as notas no repositório.
- **Sem `LICENSE`**: as notas são "produção própria que pode ser compartilhada", mas juridicamente ninguém pode copiá-las. Se a intenção é jardim público, escolha CC BY-SA 4.0 para o conteúdo e MIT para o código.
- **PDFs duplicados no repo** (raiz + `docs/anexos/`) ampliam exposição e tamanho sem necessidade; o `.docx` é editável e não versionável de forma útil.
- **Direito de citação**: quando os trechos começarem a existir, vale registrar a política (citações curtas, com autoria e página; não reproduzir capítulos).

### 4.5 Produto e experiência de uso

- **As `tags` do frontmatter são dados mortos**: existem em 100% das notas e nenhuma página, busca ou índice as usa. O mesmo vale para `nivel` e `status`.
- **Não há busca real.** Hoje, com 14 mil palavras, Ctrl+F resolve. Com 100 notas e 100 mil palavras, não resolve — e não há plano de busca antes do "site futuro".
- **Nenhuma visão de progresso**: não há "3 de 56 nós", "12 notas rascunho", "5 dias de diário seguidos". O usuário não tem feedback, e sem feedback o hábito morre.
- **Três nomes para o mesmo produto**: repositório `humanitas`, produto "Painel de Ciências Humanas", blueprint "Humanitas Explore". Escolha um guarda-chuva e trate os outros como módulos.
- **Onboarding longo para tarefas repetitivas**: 7.500 palavras de guias, excelentes na primeira leitura, pesadas na décima. Falta um cartão de "3 comandos que você usa toda semana".
- **Sem acessibilidade/idioma definidos**: tudo em PT-BR (correto para o autor), mas sem indicar se o projeto é pessoal ou publicável para fora.

---

## 5. Correções concretas — quick wins (P0, ~1 dia)

| # | Ação | Onde | Esforço | Ganho |
|---|---|---|---|---|
| 1 | Remover as 38 duplicatas da raiz e a pasta `painel-ciencias-humanas/` | raiz | 10 min | elimina 2,1 MB, 113 links quebrados e o risco de editar a cópia errada |
| 2 | Consolidar PDFs em `docs/anexos/` (remover cópias da raiz) | raiz | 5 min | −1,6 MB, um lugar só |
| 3 | Criar `.gitignore` bloqueando `acervo/*.md` (exceto README), `*.pdf` soltos, `flashcards.csv`, `relatorio-problemas.md`, `__pycache__` | raiz | 5 min | impede publicar obra protegida por acidente |
| 4 | Decidir a visibilidade do repo **antes** do primeiro livro convertido (privado agora, ou `acervo/` fora do Git) | GitHub | 2 min | elimina o risco jurídico principal |
| 5 | Adicionar `LICENSE` (CC BY-SA 4.0 para conteúdo; MIT para código, se houver) | raiz | 10 min | torna o "compartilhar" legalmente possível |
| 6 | Corrigir o conversor para **não** escrever `indice.json` (ou para fazer merge com o existente) | notebook | 20 min | evita apagar conceitos/trechos/fichas do índice |
| 7 | Alinhar template-conceito × notas (definir seções obrigatórias e opcionais) | `templates/` + `conceitos/` | 30 min | acaba a ambiguidade do padrão |
| 8 | Unificar a regra de fichas (`acervo/*-ficha.md` **ou** `acervo/fichas/`) nos guias 02 e README | docs | 10 min | remove contradição |
| 9 | Marcar no roadmap o que já foi feito ("Criar o repositório", "36 notas semente") | README | 5 min | o roadmap passa a dizer a verdade |

Sequência segura para o item 1 (nada é perdido — tudo existe em subpasta; rode em uma branch e confira o `git status`):

```bash
# 0) numa branch de trabalho
git checkout -b limpeza

# 1) conferir que cada arquivo da raiz tem uma cópia idêntica em subpasta
python3 - <<'PY'
import hashlib, pathlib
raiz = pathlib.Path('.')
for arq in raiz.iterdir():
    if not arq.is_file() or arq.name == 'README.md':
        continue
    h = hashlib.md5(arq.read_bytes()).hexdigest()
    iguais = [p for p in raiz.rglob(arq.name) if p != arq and '.git' not in p.parts
              and hashlib.md5(p.read_bytes()).hexdigest() == h]
    print(('OK  ' if iguais else 'REVER '), arq.name, '→', iguais[:1])
PY

# 2) remover as cópias da raiz (todas as .md exceto README, + notebooks, json, pdf, templates)
git rm -q -- $(git ls-files | grep -v / | grep -v '^README.md$')

# 3) remover o snapshot antigo do repositório
git rm -rq painel-ciencias-humanas

# 4) conferir e commitar
git status --short | head
git commit -m "Limpeza: remove duplicatas da raiz e snapshot antigo; consolida docs, templates e notebooks"
```

---

## 6. Implementações sugeridas (P1)

### 6.1 Trocar os dois notebooks por um CLI único (`scripts/painel.py`)

Um só script, rodável localmente **e** no CI, com subcomandos — o que hoje são 12 células de Colab separadas:

```bash
python -m scripts.painel indice      # regenera indices/indice.json (schema único, com livros+fichas+conceitos+trechos+trilhas+diario)
python -m scripts.painel tabela      # regenera a tabela do README entre os marcadores
python -m scripts.painel auditar     # links (todas as pastas + README + docs), frontmatter, duplicados, órfãs
python -m scripts.painel flashcards  # flashcards.csv com IDs estáveis (uuid5)
python -m scripts.painel progresso   # progresso.md: nós concluídos, notas ok/rascunho, dias de diário
```

Esqueleto mínimo (o parser pode e deve ser testado):

```python
# scripts/painel.py
from __future__ import annotations
import argparse, json, pathlib, re, sys
import yaml  # PyYAML: substitui o parse manual por split('---')

RAIZ = pathlib.Path(__file__).resolve().parents[1]
TEMAS = {"historia", "sociologia", "filosofia", "ciencia-politica",
         "antropologia", "economia", "geografia", "psicologia", "psicologia-social", "integrada"}
STATUS = {"rascunho", "ok", "arquivada"}

def frontmatter(caminho: pathlib.Path) -> dict:
    texto = caminho.read_text(encoding="utf-8")
    if not texto.startswith("---"):
        return {}
    _, fm, _ = texto.split("---", 2)
    return yaml.safe_load(fm) or {}

def validar(caminho: pathlib.Path) -> list[str]:
    fm = frontmatter(caminho)
    erros = []
    if fm.get("tema") not in TEMAS:
        erros.append(f"tema inválido: {fm.get('tema')!r}")
    if fm.get("status") and fm["status"] not in STATUS:
        erros.append(f"status inválido: {fm['status']!r}")
    for campo in ("tema", "tipo", "nivel", "tags"):
        if not fm.get(campo):
            erros.append(f"campo obrigatório ausente: {campo}")
    return erros

def auditar() -> int:
    problemas = []
    for pasta in ("conceitos", "trechos", "trilhas", "diario", "acervo", "docs"):
        for arq in (RAIZ / pasta).rglob("*.md"):
            for alvo in re.findall(r"\]\(([^)\s]+)\)", arq.read_text(encoding="utf-8")):
                if alvo.startswith(("http", "#")):
                    continue
                alvo = alvo.split("#")[0]
                if alvo and not (arq.parent / alvo).exists() and not (RAIZ / alvo).exists():
                    problemas.append(f"{arq.relative_to(RAIZ)} → link quebrado: {alvo}")
            if pasta in ("conceitos", "trechos", "trilhas", "diario"):
                problemas += [f"{arq.relative_to(RAIZ)} → {e}" for e in validar(arq)]
    print("\n".join(problemas) or "Painel limpo.")
    return 1 if problemas else 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("comando", choices=["indice", "tabela", "auditar", "flashcards", "progresso"])
    args = parser.parse_args()
    sys.exit(auditar() if args.comando == "auditar" else 0)
```

Complementos: `requirements.txt` com versões fixas (`PyYAML`, `pymupdf4llm`, `python-frontmatter`, `pytest`) e uma pasta `tests/` com um mini-repositório de fixtures (3 notas + 1 trilha) para testar parser, tabela e auditoria.

### 6.2 Tornar a atualização automática (GitHub Actions)

Elimina o ciclo de zip/Colab e garante que o painel nunca fique defasado:

```yaml
# .github/workflows/painel.yml
name: Atualizar painel
on:
  push:
    branches: [main]
    paths: ['conceitos/**', 'trilhas/**', 'diario/**', 'acervo/**', 'README.md', 'scripts/**']
  workflow_dispatch:
permissions:
  contents: write
jobs:
  painel:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: '3.12' }
      - run: pip install -r requirements.txt
      - run: python -m scripts.painel indice
      - run: python -m scripts.painel tabela
      - run: python -m scripts.painel flashcards
      - run: python -m scripts.painel progresso
      - run: python -m scripts.painel auditar      # falha o build se houver link/schema quebrado
      - uses: actions/upload-artifact@v4
        with: { name: flashcards, path: flashcards.csv }
      - name: Commit dos artefatos
        run: |
          git config user.name  "painel-bot"
          git config user.email "painel@users.noreply.github.com"
          git add README.md indices/indice.json progresso.md
          git diff --cached --quiet || git commit -m "chore: regenera índice, tabela e progresso"
          git push
```

Depois disso, o Guia 04 vira três linhas ("escreva a nota, dê push, baixe o `flashcards.csv` nos artifacts") — e sai o Colab da rotina.

### 6.3 Publicar o painel como site com busca (o "futuro" mais próximo)

Com Markdown + frontmatter pronto, um site estático custa poucas horas e resolve busca, tags e navegação de uma vez. `mkdocs-material` é o caminho de menor atrito (busca embutida, tags nativas, deploy no GitHub Pages):

```yaml
# mkdocs.yml
site_name: Humanitas
theme:
  name: material
  language: pt-BR
  features: [navigation.sections, navigation.indexes, search.suggest, content.tags]
plugins:
  - search:
      lang: pt
  - tags
markdown_extensions: [admonition, tables, toc, pymdownx.superfences]
nav:
  - Início: README.md
  - Trilhas:
      - Psicologia 1: trilhas/psicologia-nivel-1.md
      - Psicologia 2: trilhas/psicologia-nivel-2.md
      - Filosofia: trilhas/filosofia-nivel-1.md
      - Sociologia: trilhas/sociologia-nivel-1.md
      - Integrada: trilhas/integrada-nivel-1.md
  - Conceitos: conceitos/
```

Regra de ouro: **publicar apenas notas, trilhas, eixos e diário** — `acervo/` fica fora do site (privado/no Drive). Publicar um site é também o argumento que justifica escolher CC BY-SA: o conteúdo passa a ter valor fora do seu computador.

Alternativas, se o objetivo for "segundo cérebro": **Quartz** (grafo e backlinks a partir de Markdown puro) ou abrir a pasta no **Obsidian** e usar o **Obsidian Publish** (pago). Para um portfólio: Astro Starlight com a mesma estrutura.

### 6.4 Melhorar o conversor (o que realmente importa em PDF → Markdown)

```python
import pymupdf4llm, hashlib, json, pathlib

def converter(pdf: pathlib.Path, destino: pathlib.Path, manifesto: dict) -> None:
    sha = hashlib.sha256(pdf.read_bytes()).hexdigest()
    if manifesto.get(pdf.name, {}).get("sha256") == sha:
        return  # incremental: não reconverte o que não mudou
    paginas = pymupdf4llm.to_markdown(
        str(pdf), page_chunks=True, show_progress=False,
        margins=(0, 40, 0, 40),   # descarta cabeçalho/rodapé
    )
    texto = "\n\n".join(p["text"] for p in paginas)
    if len(texto.strip()) < 1000:
        manifesto[pdf.name] = {"sha256": sha, "status": "sem-texto (OCR necessário)"}
        return
    # um arquivo por capítulo, com metadados herdados do nome "Autor - Título.pdf"
    ...
    manifesto[pdf.name] = {"sha256": sha, "status": "ok", "paginas": len(paginas)}
```

Ganhos: reconversão só do que mudou, limpeza de cabeçalho/rodapé, arquivos por capítulo (busca e leitura melhores), manifesto `acervo/manifesto.json` auditável, e nenhuma escrita em `indices/` (o índice passa a ter **um** dono: o CLI).

### 6.5 Flashcards de verdade (e sem duplicar no Anki)

```python
import uuid

TIPOS = {
    "definicao":  ("O que é {conceito}?", "{definicao}"),
    "aplicacao":  ("Dê um exemplo concreto de {conceito} e explique por que ele ilustra o conceito.", "{exemplos}"),
    "eixo":       ("Onde a teoria {conceito} se posiciona no eixo {eixo}?", "{posicao}"),
}

def cartoes(nota: dict) -> list[list[str]]:
    base = uuid.uuid5(uuid.NAMESPACE_URL, f"humanitas/{nota['arquivo']}/{nota['conceito']}")
    saida = []
    for i, (tipo, (frente, verso)) in enumerate(TIPOS.items()):
        if not nota.get(tipo):
            continue
        saida.append([
            str(uuid.uuid5(base, tipo)),            # GUID estável: reimportar atualiza, não duplica
            frente.format(**nota), verso.format(**nota),
            f"humanitas::{nota['tema']}::{' '.join(nota['tags'][:5])}",
            str(i),
        ])
    return saida
```

Regras que valem mais que o código: (a) ID estável (`GUID` na 4ª coluna no formato de importação do Anki); (b) no máximo 1 cartão de definição por nota; (c) cartões de **aplicação** ("dê um exemplo e explique") são os que realmente testam entendimento; (d) eixos viram cartões de posicionamento ("onde Freud fica no eixo livre-arbítrio × determinismo?"); (e) agendar com **FSRS** (nativo no Anki moderno), não SM-2.

### 6.6 Calcular progresso (o feedback que falta)

- Ler os checkboxes `- [ ]` / `- [x]` das trilhas → `56 nós, 3 concluídos (5%)`.
- Contar `status` das notas → `12 ok / 24 rascunho`.
- Contar entradas em `diario/` e a sequência de semanas com pelo menos 1 entrada.
- Contar conceitos com `obra_origem` apontando para fonte primária.
- Emitir `progresso.md` com uma tabela por trilha e um badge no README (`![progresso](https://img.shields.io/badge/nós-5%25-yellow)`).

Isso ataca o problema mais provável do projeto: **a sensação de avanço sem evidência de aprendizado**.

### 6.7 Busca e IA de consulta (fase posterior, com cuidado)

- **Curto prazo**: busca nativa do site (Pagefind no MkDocs/Astro, zero backend) — resolve 90% do problema.
- **Médio prazo**: RAG **local** sobre as notas (SQLite FTS5 + embeddings em `sentence-transformers`), com resposta sempre **citando o arquivo e a seção**. Nunca gerar texto novo sobre o conteúdo: só localizar e resumir o que você mesmo escreveu.
- **Nunca**: um chat que responda "o que é habitus" sem passar pela sua nota — isso destrói a função pedagógica do painel.

### 6.8 Qualidade editorial: uma "definição de pronto" por nota

Adicionar ao template (e validar no CI) os campos que hoje faltam:

```yaml
# campos novos sugeridos
fonte_primaria: "Weber, A Ética Protestante..., cap. 2"   # obra real, não o guia
confianca: media            # alta | media | baixa
contestado_por: "Durkheim; crítica weberiana de ..."      # opcional
revisado_em: 2026-10-21
```

E uma checklist no topo de cada nota nova:

- [ ] Definição em uma frase que caiba num cartão
- [ ] Explicação escrita **sem consultar** a IA (comparar depois)
- [ ] Uma citação literal com capítulo/página (ou "sem citação — fonte secundária")
- [ ] Um exemplo brasileiro/atual
- [ ] Pelo menos uma conexão interdisciplinar com o "porque"
- [ ] Posição no(s) eixo(s) correspondente(s)

---

## 7. Rumos possíveis

| Cenário | O que é | Esforço | Riscos | Quando faz sentido |
|---|---|---|---|---|
| **A. Painel pessoal privado** (estado atual, limpo) | Reorganizar, automatizar, começar a estudar de verdade | 1 semana | continuar sendo documentação sobre um método | **agora** |
| **B. Jardim digital público** | Site com busca, tags, grafo e progresso; só notas (sem acervo) | 2–3 semanas | curadoria pública exige rigor; links quebrados ficam visíveis | começar com ~20 notas `ok` |
| **C. "Humanitas Explore" (produto/curso)** | Trilhas como cursos, quiz, XP, comunidade, eventualmente pago | meses | direitos autorais, conteúdo raso em escala, virar "curso de resumos" | depois de 2–3 trilhas realmente concluídas |
| **D. Ferramenta open-source (pipeline)** | CLI/extensão "PDF → notas → flashcards" reutilizável por outras pessoas | 1–2 meses | concorrência com NotebookLM/Obsidian; manutenção | se o CLI provar valor no seu uso |
| **E. Tutor com IA (RAG sobre suas notas)** | Perguntas, quiz gerado, revisão espaçada personalizada | 1 mês | IA no centro do aprendizado, contra a tese do projeto | depois de B, e com citação obrigatória |

**Recomendação: A → B, e só então decidir entre C, D e E.**

- **Fase 1 (agora, 1 semana):** limpeza (seção 5), CLI + CI (6.1–6.2), e **uma** nota reescrita de ponta a ponta com citação e página, como padrão-ouro. Escrever a primeira entrada do diário. Escrever a primeira ficha de leitura (Mills, *A Imaginação Sociológica* — é o livro nº 1 do Guia 05 e cobre dois nós).
- **Fase 2 (30–60 dias):** site público com busca e progresso (B). Publicar só notas. Métrica: 20 notas `ok` + 8 diários + 1 trilha em 30%.
- **Fase 3 (90 dias):** escolher **um** dos caminhos C/D/E conforme o sinal: se você usa o site todo dia → B evolui para C; se você quer que outras pessoas usem o pipeline → D; se a dificuldade é revisar → E (quiz/RAG).

### O que **não** fazer (economiza meses)

- Não converter os 100+ PDFs "para depois". O próprio Guia 02 já sabe disso — só falta o repositório obedecer.
- Não construir app/XP/gamificação antes de ter conteúdo reescrito. Gamificar 36 rascunhos de IA gamifica o vazio.
- Não tornar o repositório público com `acervo/` populado.
- Não deixar a IA "explicar" o que você deveria escrever no diário — o diário é o único ativo que não pode ser gerado.
- Não criar mais notas por tema antes de fechar as lacunas de seções/citações nas existentes (senão a dívida cresce junto com o acervo).

---

## 8. Backlog priorizado

| Prioridade | Item | Impacto | Esforço |
|---|---|---|---|
| P0 | Remover duplicatas da raiz + `painel-ciencias-humanas/` | alto | 15 min |
| P0 | `.gitignore` + decisão de visibilidade do repo | alto | 10 min |
| P0 | Corrigir conversor (não sobrescrever `indice.json`) | alto | 20 min |
| P0 | Alinhar template × notas (seções obrigatórias) | alto | 30 min |
| P1 | CLI `scripts/painel.py` + `requirements.txt` + testes | alto | 1 dia |
| P1 | GitHub Action de atualização + auditoria bloqueante | alto | meio dia |
| P1 | `progresso.md` + contagem de nós/status/diário | alto | meio dia |
| P1 | Licença + política de acervo (privado/Drive) | alto | 20 min |
| P1 | Reescrever 5 notas com fonte primária + citação + página (padrão-ouro) | alto | 1 semana |
| P1 | Primeira ficha de leitura + primeiro diário | alto | 1 dia |
| P2 | Site MkDocs com busca, tags e deploy | médio | 2 dias |
| P2 | Flashcards com GUID estável + tipos de cartão + FSRS | médio | 1 dia |
| P2 | Conversor incremental por capítulo + manifesto | médio | 1 dia |
| P2 | Schema validation (`pydantic`) + pre-commit | médio | meio dia |
| P3 | Grafo de conexões, quiz automático, RAG local | médio | semanas |
| P3 | Renomear/unificar produto (Humanitas) e escrever "README de 1 página" | baixo | 2 h |

---

## 9. Métricas de sucesso

**Métrica-norte:** notas **reescritas** (`status: ok`) + entradas de diário — não número de notas, nem de PDFs convertidos.

| Métrica | Hoje | Meta 30 dias | Meta 90 dias |
|---|---|---|---|
| Notas `ok` | 0 | 10 | 25 |
| Entradas de diário | 0 | 4 | 12 |
| Fichas de leitura | 0 | 1 | 3 |
| Nós de trilha concluídos | 0 / 56 | 6 | 15 |
| Notas com citação + página | 0 | 10 | 25 |
| Links quebrados / erros de schema | 113 | 0 | 0 |
| Cobertura de fontes primárias | ~0% | 30% | 60% |
| Repositório público sem acervo protegido | ✅ (acervo vazio) | ✅ | ✅ |

---

## 10. Anexo — como este diagnóstico foi feito

1. **Leitura integral** de `README.md`, `docs/01`–`05`, `templates/*`, `conceitos/README.md`, `trilhas/README.md` e das 5 trilhas.
2. **Execução do notebook atualizador** contra uma cópia do repositório (substituindo as células do Colab): resultado `36 conceitos, 0 trechos, 0 livros`, tabela idêntica à do README, 36 flashcards — nenhum erro de execução. Isso confirma que o script funciona; os defeitos são de contrato (auditoria incompleta, contagem dupla, schema divergente).
3. **Auditoria estática própria** em Python: frontmatter (36/36 com 8 chaves), temas, tipos, status, níveis, placeholders (`a criar` 1, `a escolher` 5, `aprofundar` 4), seções ausentes por nota, links relativos por pasta (`raiz` 113, `conceitos` 1 (exemplo no README), `trilhas` 0, `docs` 0, `templates` 9 — estes propositais), duplicatas por MD5 (38 arquivos de raiz, 2,1 MB).
4. **Consulta à API do GitHub** (`gh api repos/...`): `private: false`, sem licença, branch `main`.
5. **Comparação de links das trilhas × notas existentes**: 0 notas órfãs (todas as 36 são citadas em alguma trilha) e 0 links quebrados em `trilhas/` — mérito do estado atual.

> Observação final: nada neste documento desmerece o projeto. A documentação e a arquitetura estão acima da média; o que falta é **fechar o ciclo** — limpar o repositório, automatizar o que é mecânico e gastar o tempo economizado reescrevendo notas com fonte primária e escrevendo o diário.
