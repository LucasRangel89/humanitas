# docs/ — guias do projeto

Comece pelo que resolve o seu problema agora.

| Guia | Para quem / quando |
|---|---|
| [01 — Criar o repositório no GitHub](01-criar-repositorio-no-github.md) | Primeira vez; publicar o painel e ligar o CI |
| [02 — Fluxo de extração](02-fluxo-de-extracao.md) | Entender o caminho PDF → Markdown → nota → painel |
| [03 — Prompts do NotebookLM + Modo Tutor](03-prompts-notebooklm.md) | Extrair ficha, conceitos, trechos, perguntas e críticas de uma obra |
| [04 — Atualizar o GitHub no dia a dia](04-atualizar-o-github.md) | Adicionar, editar, renomear e excluir arquivos pelo navegador |
| [05 — Prioridades de leitura](05-prioridades-de-leitura.md) | Escolher o próximo livro (os 10 livros-chave e as filas seguintes) |
| [06 — Manutenção: CLI e CI](06-manutencao-e-ci.md) | Rodar `scripts/painel.py`, entender a auditoria e importar flashcards |
| [07 — Rumos e próximos passos](07-rumos-e-proximos-passos.md) | O que fazer depois da fundação: padrão-ouro, site, RAG e **quando migrar de ferramenta** (Fase 4) |
| [08 — Instruções para futuros mantenedores](08-instrucoes-futuras.md) | Como adicionar campo, manter CI, publicar site e criar PRs |
| [09 — Mapa das humanidades](09-mapa-das-humanidades.md) | **Expansão**: quais áreas entram, como (tema × eixo × tag), em que ordem e com que critério |
| [Análise do projeto (arquivo histórico)](arquivo/analise-2026-10-21.md) | Diagnóstico de 21/10/2026 — números desatualizados, não é plano vigente |

## Anexos

`anexos/` guarda os planos de estudo, a grade curricular e o `.docx` que originaram
as trilhas. São **materiais de terceiros**: não estão cobertos pelas licenças do
projeto e não devem ser redistribuídos.

## Três comandos que você usa toda semana

```bash
make pendencias  # o que falta em cada nota (padrão-ouro)
make nova TIPO=conceito NOME="Habitus" TEMA=sociologia
make auditar     # links, metadados, duplicados, seções ausentes
make painel      # índice, tabela de temas, progresso e flashcards
make site        # site com busca (http://127.0.0.1:8000)
```
