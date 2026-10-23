from __future__ import annotations

import argparse
import csv
import pathlib
import sys

from .modelo import RAIZ_PADRAO, MARCADOR_TEMAS, MARCADOR_PROGRESSO, rel, ler
from .indice import montar_indice, tabela_temas, gravar_indice, atualizar_readme_temas
from .progresso import texto_progresso, bloco_progresso_readme, atualizar_readme_progresso, calcular_progresso
from .cartoes import gerar_flashcards
from .auditoria import auditar
from .scaffolding import TIPOS_NOVA, cmd_nova, cmd_pendencias
from .site import montar_site_src, cmd_site
from .afirmacoes import cmd_afirmacoes
from .grafo import cmd_grafo
from .obras import cmd_obras
from .retencao import cmd_retencao
from .marcacao import aplicar_progresso
import json as _json

# ---------------------------------------------------------------------------
# Comandos
# ---------------------------------------------------------------------------


def _imprimir_lista(titulo: str, itens: list[str]) -> None:
    if not itens:
        return
    print(f"\n{titulo} ({len(itens)}):")
    for item in itens:
        print(f"  - {item}")


def cmd_indice(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    caminho = gravar_indice(raiz, indice)
    t = indice["totais"]
    print(
        f"{rel(caminho, raiz)} regenerado: {t['livros']} livro(s), {t['fichas']} ficha(s), "
        f"{t['conceitos']} conceito(s), {t['eixos']} eixo(s), {t['trechos']} trecho(s), "
        f"{t['trilhas']} trilha(s), {t['diario']} entrada(s) de diário."
    )
    return 0


def cmd_tabela(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    tabela = tabela_temas(indice)
    readme = raiz / "README.md"
    texto = ler(readme) if readme.exists() else ""
    inicio, fim = MARCADOR_TEMAS
    if inicio not in texto or fim not in texto:
        destino = raiz / "indices" / "tabela-temas.md"
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text("## Painel de temas\n\n" + tabela + "\n", encoding="utf-8")
        print(
            "Aviso: marcadores PAINEL-TEMAS não encontrados no README. "
            f"Tabela salva em {rel(destino, raiz)}."
        )
    elif atualizar_readme_temas(raiz, tabela):
        print("README.md atualizado com a tabela de temas.")
    else:
        print("Tabela de temas já estava atualizada.")
    print()
    print(tabela)
    return 0


def cmd_progresso(raiz: pathlib.Path) -> int:
    indice = montar_indice(raiz)
    conteudo = texto_progresso(indice)
    destino = raiz / "progresso.md"
    destino.write_text(conteudo, encoding="utf-8")
    atualizar_readme_progresso(raiz, bloco_progresso_readme(indice))
    p = calcular_progresso(indice)
    print(
        f"{rel(destino, raiz)} regenerado: {p['ok']}/{p['conceitos']} notas ok, "
        f"{p['nos_concluidos']}/{p['nos_total']} nós de trilha, "
        f"{p['diario_total']} entrada(s) de diário."
    )
    return 0


def cmd_flashcards(raiz: pathlib.Path) -> int:
    linhas = gerar_flashcards(raiz)
    destino = raiz / "flashcards.csv"
    with destino.open("w", newline="", encoding="utf-8") as arquivo:
        escritor = csv.writer(arquivo)
        escritor.writerow(["guid", "frente", "verso", "tags", "baralho"])
        escritor.writerows(linhas)
    print(f"{rel(destino, raiz)} criado com {len(linhas)} cartão(ões).")
    if not linhas:
        print("Nenhum cartão: crie notas com 'Definição em uma frase' preenchida.")
    return 0


def cmd_auditar(raiz: pathlib.Path, estrito: bool = False) -> int:
    erros, avisos = auditar(raiz)
    print("# Auditoria do painel")
    _imprimir_lista("Erros", erros)
    _imprimir_lista("Avisos", avisos)
    if not erros and not avisos:
        print("Painel limpo: nenhum erro e nenhum aviso.")
    print(
        f"\nResumo: {len(erros)} erro(s), {len(avisos)} aviso(s)."
    )
    if erros or (estrito and avisos):
        return 1
    return 0


# ---------------------------------------------------------------------------
def cmd_tudo(raiz: pathlib.Path) -> int:
    for comando in (cmd_indice, cmd_tabela, cmd_progresso, cmd_flashcards, cmd_grafo, cmd_obras, cmd_retencao):
        codigo = comando(raiz)
        if codigo:
            return codigo
    return 0


def cmd_aplicar_progresso(raiz: pathlib.Path, **opcoes) -> int:
    """Grava nas trilhas o progresso exportado pelo site (botão "Exportar")."""
    arquivo = (opcoes.get("arquivo") or "").strip()
    if not arquivo:
        print(
            "Informe o arquivo exportado pelo site:\n"
            "  python -m scripts.painel aplicar-progresso --arquivo progresso.json"
        )
        return 1
    caminho = pathlib.Path(arquivo)
    if not caminho.is_absolute():
        caminho = (pathlib.Path.cwd() / caminho).resolve()
    if not caminho.exists():
        print(f"Arquivo não encontrado: {caminho}")
        return 1
    try:
        dados = _json.loads(caminho.read_text(encoding="utf-8"))
    except Exception as exc:  # JSON inválido
        print(f"JSON inválido em {caminho.name}: {exc}")
        return 1

    simular = bool(opcoes.get("simular"))
    mudancas, avisos = aplicar_progresso(dados, raiz, gravar=not simular)
    print("# Progresso do site → trilhas")
    _imprimir_lista("Mudanças" + (" (simulação, nada gravado)" if simular else ""), mudancas)
    _imprimir_lista("Avisos", avisos)
    if simular and mudancas:
        print("\nRode sem --simular para gravar, depois `make painel` e commite.")
    elif mudancas:
        print("\nAgora rode `make painel` para atualizar índice, progresso e cartões.")
    return 0


COMANDOS = {
    "indice": cmd_indice,
    "tabela": cmd_tabela,
    "progresso": cmd_progresso,
    "flashcards": cmd_flashcards,
    "auditar": cmd_auditar,
    "tudo": cmd_tudo,
    "nova": cmd_nova,
    "pendencias": cmd_pendencias,
    "site": cmd_site,
    "afirmacoes": cmd_afirmacoes,
    "grafo": cmd_grafo,
    "obras": cmd_obras,
    "retencao": cmd_retencao,
    "aplicar-progresso": cmd_aplicar_progresso,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Manutenção do painel Humanitas (índice, tabelas, auditoria e flashcards)."
    )
    parser.add_argument(
        "--raiz",
        default=str(RAIZ_PADRAO),
        help="Raiz do repositório (padrão: pasta do projeto).",
    )
    parser.add_argument("comando", choices=COMANDOS)
    parser.add_argument(
        "--estrito",
        action="store_true",
        help="No comando auditar, tratar avisos como erro.",
    )

    grupo = parser.add_argument_group("nova")
    grupo.add_argument("--tipo", choices=sorted(TIPOS_NOVA), help="Tipo de nota a criar (nova).")
    grupo.add_argument("--nome", help="Nome do conceito, do eixo, da obra ou da reflexão (nova).")
    grupo.add_argument("--tema", help="Tema da nota (nova, pendencias).")
    grupo.add_argument("--nivel", help="iniciante | entusiasta | avancado (nova).")
    grupo.add_argument("--autor", help="Autor da obra (nova).")
    grupo.add_argument("--obra", help="Obra de origem (nova).")
    grupo.add_argument("--ano", help="Ano da obra (nova, ficha).")
    grupo.add_argument("--capitulo", help="Capítulo do trecho (nova, trecho).")
    grupo.add_argument("--pagina", help="Página do trecho (nova, trecho).")
    grupo.add_argument("--data", help="Data AAAA-MM-DD (nova, diario). Padrão: hoje.")
    grupo.add_argument("--origem", help="Módulo/conceito que gerou o diário (nova).")
    grupo.add_argument("--tags", help="Tags separadas por vírgula (nova).")
    grupo.add_argument("--fonte-verificada", dest="fonte_verificada", help="sim | nao (nova, conceito/eixo).")
    grupo.add_argument("--tradicao", help="Tradição/escola do conceito (nova).")
    grupo.add_argument("--nivel-evidencia", dest="nivel_evidencia", help="alta|media|baixa|teorica|empirica (nova).")
    grupo.add_argument("--contestado-por", dest="contestado_por", help="Quem contesta, separado por vírgula (nova).")
    grupo.add_argument("--eixos", help="Eixos relacionados, separados por vírgula (nova).")
    grupo.add_argument("--relacoes", help="Relações com outros conceitos, separadas por vírgula (nova).")
    grupo.add_argument("--forcar", action="store_true", help="Sobrescrever arquivo existente (nova).")
    grupo.add_argument("--limite", type=int, help="Máximo de notas listadas (pendencias).")
    grupo.add_argument("--prontas", action="store_true", help="Incluir as notas já prontas (pendencias).")
    grupo.add_argument("--arquivo", help="Arquivo JSON do progresso exportado pelo site (aplicar-progresso).")
    grupo.add_argument("--simular", action="store_true", help="Só mostrar o que mudaria (aplicar-progresso).")

    args = parser.parse_args(argv)
    raiz = pathlib.Path(args.raiz).resolve()
    comando = COMANDOS[args.comando]
    if args.comando == "auditar":
        return comando(raiz, estrito=args.estrito)  # type: ignore[call-arg]
    if args.comando == "aplicar-progresso":
        return comando(raiz, arquivo=args.arquivo, simular=args.simular)  # type: ignore[call-arg]
    if args.comando in ("nova", "pendencias"):
        opcoes = {
            chave: getattr(args, chave)
            for chave in (
                "tipo", "nome", "tema", "nivel", "autor", "obra", "ano", "capitulo",
                "pagina", "data", "origem", "tags", "fonte_verificada", "tradicao", "nivel_evidencia",
                "contestado_por", "eixos", "relacoes", "forcar", "limite", "prontas",
            )
        }
        return comando(raiz, **opcoes)  # type: ignore[call-arg]
    return comando(raiz)


if __name__ == "__main__":
    sys.exit(main())
