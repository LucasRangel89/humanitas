# Guia 08 — Instruções para futuros mantenedores

> Este guia consolida como manter o Humanitas após as PRs 1–7. Leia em ordem: Guias 01–05 (fluxo), 06 (CI), 07 (rumos).

## O que você precisa saber antes de mexer

- **Nunca reescreva conteúdo de estudo** (`conceitos/`, `trilhas/`, `diario/`, `trechos/`, `acervo/fichas/`) manualmente, exceto backfill mecânico de frontmatter via script. O conteúdo é de estudo, não código.
- **Não toque** em `docs/anexos/`, `acervo/*.md` integrais e licenças.
- **Todo comportamento novo precisa de teste** em `tests/` e passar em `make testar`.
- **Antes de cada PR**: `make testar && make auditar && make painel` e confirmar idempotência (segundo `make painel` sem diff). Commite `README.md`, `indices/indice.json`, `progresso.md`, `indices/grafo.json`, `indices/obras.json`, `indices/retencao.json`, `flashcards.csv` se mudou.

## Onde está cada coisa

| Lugar | O que faz | Quando mexer |
|---|---|---|
| `scripts/painel/` | CLI que gera índices, progresso, flashcards, grafo, obras, retenção e site | PRs de funcionalidade |
| `templates/` | Modelos para `nova` | Ao adicionar campo novo |
| `docs/06-manutencao-e-ci.md` | Como usar `make painel` e CI | Ao mudar workflow |
| `docs/07-rumos-e-proximos-passos.md` | Backlog priorizado | Ao fechar/entregar marco |
| `docs/08-instrucoes-futuras.md` | Este guia | Ao mudar processo |

## Como adicionar um campo novo no esquema

1. **Decida se é obrigatório ou opcional.** Quase tudo novo deve ser opcional para não quebrar 50 notas existentes.
2. **Modelo** (`scripts/painel/modelo.py`): defina constantes (`NIVEIS_*`, etc.) e, se precisar, `substituir_bloco` já está lá.
3. **Coleta** (`scripts/painel/indice.py`): preserve o campo em `coletar_conceitos` (ex.: `registro["meu_campo"] = fm.get("meu_campo")`).
4. **Validação** (`scripts/painel/auditoria.py`): adicione checagem em `_validar_metadados`, retornando erro claro com `rel(caminho, raiz)`.
5. **Scaffold** (`scripts/painel/scaffolding.py`): aceite `opcoes.get("meu_campo")`, valide e inclua em `frente["conceito"]` e `frente["eixo"]`.
6. **CLI** (`scripts/painel/cli.py`): adicione `--meu-campo` e inclua no `opcoes` de `nova/pendencias`.
7. **Templates** (`templates/template-*.md`): adicione linha com default (ex.: `meu_campo: ""`).
8. **Grafo/Cartões/Obras/Retenção**: se o campo alimenta grafo ou cartões, atualize `grafo.py`/`cartoes.py`/`obras.py`/`retencao.py`.
9. **Testes** (`tests/test_painel.py`): cubra preservação no índice, validação de erro e criação via `nova`.
10. **Docs**: atualize Guias 06/08 e, se mudar fluxo de CI, `README.md`.

Exemplo PR3 fez exatamente isso para `tradicao`, `nivel_evidencia`, `contestado_por`, `eixos`, `relacoes`.

## Comandos do dia a dia

```bash
# verificar
make testar
make auditar
make painel

# criar nota
python -m scripts.painel nova --tipo conceito --nome "Novo Conceito" --tema sociologia --tradicao "critica" --nivel-evidencia alta

# ver pendências (filtra por fonte_verificada agora)
python -m scripts.painel pendencias --tema sociologia
python -m scripts.painel pendencias --fonte-verificada nao

# gerar artefatos específicos
python -m scripts.painel afirmacoes  # relatorio-afirmacoes.md (ignorado no Git)
python -m scripts.painel grafo       # indices/grafo.json
python -m scripts.painel obras       # indices/obras.json
python -m scripts.painel retencao    # indices/retencao.json
python -m scripts.painel site        # site-src/ (bloqueia se auditar falhar)

# tudo + idempotência
python -m scripts.painel tudo
python -m scripts.painel tudo  # segunda vez não deve mudar nada (git diff --exit-code)
```

## CI e publicação

- `.github/workflows/painel.yml` roda `make testar`, `make auditar`, `make painel`, e checa `git diff --exit-code` para `README.md`, `indices/`, `progresso.md`. Não faz push, só artefato `flashcards.csv` (e futuro `grafo.json`/`obras.json` se quiser).
- `site.yml` publica `site-src/` no `gh-pages` só após gate passar.
- `converter-pdfs.ipynb` **não** gera mais `indice.json` — só `make painel` o faz. Rodar o notebook não deve criar diff em `indices/`.

## Retenção e cartões

- `cartoes.py` gera `flashcards.csv` com GUID estável. Reimportar no Anki atualiza.
- `retencao.py` calcula taxa_ok e cartões por tema. Use para decidir o que revisar.
- Cartões extras para `tradicao`/`nivel_evidencia`/`relacoes` foram adicionados em PR4 — desative se poluir.

## Próximos passos práticos (resumo do Guia 07)

1. Preencher `Trecho de apoio` + `fonte_verificada: sim` nas 50 notas (priorize 12 de Psicologia).
2. Adicionar `tradicao` e `nivel_evidencia` onde fizer sentido; `eixos` e `relacoes` para conectar trilhas.
3. Gerar grafo e revisar conexões órfãs (`pendencias`).
4. Publicar site quando `auditar` = 0 erros (gate PR7 garante).

## Quando criar novas PRs

- Uma PR por item, branch `prN-descricao` a partir de `main`, commits em português (`feat:`, `fix:`, `chore:`, `refactor:`).
- Cada PR termina com seção: **o que mudou / decisões / verificação / limitações**.
- Entrega final: tabela `PR | link | CI | desvios`.

## Dúvidas frequentes

- **Mudei template e 50 notas não têm o campo novo, auditar reclama?** Campo novo deve ser opcional; validação só dispara se presente e inválido.
- **Site não publica, gate bloqueou.** Rode `make auditar`, corrija erros (duplicata, frontmatter, fonte_verificada), depois `make painel && make site`.
- **Preciso migrar 50 notas manualmente?** Não. PR3 mostrou como fazer backfill mecânico só de frontmatter via script Python, sem tocar corpo.
