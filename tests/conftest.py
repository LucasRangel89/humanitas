"""Fixtures dos testes: um mini-repositório válido do painel."""

from __future__ import annotations

import pathlib
import shutil
import sys

import pytest

RAIZ_PROJETO = pathlib.Path(__file__).resolve().parents[1]
if str(RAIZ_PROJETO) not in sys.path:
    sys.path.insert(0, str(RAIZ_PROJETO))

CONCEITO_VALIDO = """---
conceito: "Habitus"
obra_origem: "Bourdieu, O Senso Prático"
autor_origem: "Pierre Bourdieu"
tema: sociologia
tipo: conceito
nivel: entusiasta
tags: [sociologia, bourdieu, pratica]
status: ok
---

# Conceito — Habitus

## Definição em uma frase

Disposição durável, incorporada e transponível que orienta práticas sem obedecer a regras explícitas.

## Explicação com as minhas palavras

O habitus é o social feito corpo: um conjunto de esquemas que faz o mundo parecer óbvio.

## Onde aparece na obra

No capítulo sobre a lógica da prática.

## Trecho de apoio

> "As estruturas sociais passam para dentro dos corpos." (cap. 3, p. 94)

O trecho resume a tese da incorporação.

## Exemplos que ilustram

- Um jogador que "sente" o lance antes de calcular.

## Conceitos relacionados

- [Campo](sociologia-campo.md)

## Conexões interdisciplinares

- **Psicologia — automatismo:** porque o habitus explica o comportamento sem deliberação.

## Por que este conceito importa

Sem ele, prática social vira escolha consciente; com ele, vira história incorporada.
"""

EIXO_VALIDO = """---
eixo: "Natureza × Cultura"
autor_origem: "Debate clássico"
tema: filosofia
tipo: eixo
nivel: iniciante
tags: [eixo]
status: ok
---

# Eixo — Natureza × Cultura

## A questão em uma frase

O que no humano é dado pela biologia e o que é fabricado pela cultura?

## Por que é uma grande questão

Define o que cada disciplina pode explicar sozinha.

## Posições no debate

| Posição | Autores | Obra de referência | Nota no painel |
|---|---|---|---|
| Inatismo | Descartes | Meditações | (a criar) |
| Culturalismo | Durkheim | Regras do método | (a criar) |

## Conexões interdisciplinares

- **Biologia:** limite dos instintos.
"""

TRILHA_VALIDA = """---
trilha: "Sociologia — teste"
tema: sociologia
nivel: iniciante
status: em-andamento
tags: [trilha]
---

# Trilha — Sociologia teste

## Objetivo da trilha

Explicar o conceito com as suas palavras.

## Nós da trilha

1. [x] **[Habitus](../conceitos/sociologia-habitus.md)** — concluído.
2. [ ] **[Campo](../conceitos/sociologia-campo.md)** — pendente.
3. [ ] **Síntese** — escrever no diário.
"""


def _escrever(caminho: pathlib.Path, conteudo: str) -> pathlib.Path:
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_text(conteudo, encoding="utf-8")
    return caminho


@pytest.fixture()
def mini_repo(tmp_path: pathlib.Path) -> pathlib.Path:
    """Repositório mínimo e válido (sem erros de auditoria)."""
    _escrever(
        tmp_path / "README.md",
        "# Painel\n\n<!-- PAINEL-TEMAS-INICIO -->\n\n| Tema |\n|---|\n\n"
        "<!-- PAINEL-TEMAS-FIM -->\n\n<!-- PROGRESSO-INICIO -->\n\n"
        "<!-- PROGRESSO-FIM -->\n",
    )
    _escrever(tmp_path / "conceitos" / "README.md", "# conceitos/\n")
    _escrever(tmp_path / "conceitos" / "sociologia-habitus.md", CONCEITO_VALIDO)
    _escrever(tmp_path / "conceitos" / "sociologia-campo.md", CONCEITO_VALIDO.replace(
        '"Habitus"', '"Campo"').replace("# Conceito — Habitus", "# Conceito — Campo"))
    _escrever(tmp_path / "conceitos" / "eixo-natureza-cultura.md", EIXO_VALIDO)
    _escrever(tmp_path / "trilhas" / "sociologia-teste.md", TRILHA_VALIDA)
    _escrever(
        tmp_path / "diario" / "2026-01-15-sociologia-habitus.md",
        "---\ndata: 2026-01-15\ntema: sociologia\norigem: Habitus\ntipo: diario\n"
        "tags: [diario]\n---\n\n# Diário — habitus\n\n## Minha síntese\n\nTexto.\n",
    )
    _escrever(
        tmp_path / "trechos" / "bourdieu-corpo.md",
        '---\nobra: "O Senso Prático"\nautor: "Bourdieu"\ncapitulo: "3"\n'
        'pagina: "94"\ntema: sociologia\ntipo: trecho\ntags: [trecho]\n---\n\n'
        "# Trecho — corpo\n\n## O trecho\n\n> Citação.\n\n## Por que guardei este trecho\n\nPorque sim.\n",
    )
    _escrever(
        tmp_path / "acervo" / "fichas" / "bourdieu-senso-pratico-ficha.md",
        '---\nobra: "O Senso Prático"\nautor: "Bourdieu"\nano: 1980\ntema: sociologia\n'
        'tipo: ficha-de-leitura\ntags: [ficha]\nstatus: em-andamento\n---\n\n'
        "# Ficha — O Senso Prático\n\n## Tese central\n\nO habitus.\n",
    )
    _escrever(tmp_path / "acervo" / "README.md", "# acervo/\n")
    _escrever(tmp_path / "progresso.md", "# Progresso do painel\n\nGerado.\n")
    _escrever(tmp_path / "diario" / "README.md", "# diario/\n\nDiário de bordo.\n")
    _escrever(tmp_path / "trechos" / "README.md", "# trechos/\n\nCitações.\n")
    _escrever(
        tmp_path / "docs" / "README.md",
        "# docs/\n\n- [Guia 03](03-prompts-notebooklm.md)\n",
    )
    _escrever(tmp_path / "docs" / "03-prompts-notebooklm.md", "# Guia 03\n")
    _escrever(tmp_path / "docs" / "07-rumos-e-proximos-passos.md", "# Guia 07\n")
    # templates reais: o comando `nova` monta o esqueleto a partir deles
    shutil.copytree(RAIZ_PROJETO / "templates", tmp_path / "templates")
    return tmp_path
