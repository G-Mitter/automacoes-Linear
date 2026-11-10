"""Linha de comando: python -m linear <comando>."""
from __future__ import annotations

import argparse
import sys

import pyautogui
from rich.console import Console
from rich.table import Table

from . import checagem, config, imagens

pyautogui.FAILSAFE = True  # mouse no canto superior esquerdo = parada de emergência (RF-14)
console = Console()


def cmd_perfis(_args) -> int:
    geral = config.carregar_geral()
    perfis = config.carregar_perfis()
    if not perfis:
        console.print(f"Nenhum perfil em {config.PASTA_PERFIS}")
        return 1
    t = Table(title="Perfis")
    for col in ("id", "nome", "formato", "modo", "filiais", "ativo"):
        t.add_column(col)
    for pid, p in perfis.items():
        filiais = config.resolver_filiais(p.get("filiais_padrao"), geral)
        t.add_row(pid, p.get("nome", ""), p.get("formato", ""), p.get("modo_filiais", ""),
                  "todas" if p.get("filiais_padrao") == "todas" else ",".join(map(str, filiais)),
                  "sim" if p.get("ativo", True) else "não")
    console.print(t)
    return 0


def cmd_checar(args) -> int:
    if args.tela is not None:
        imagens.contagem(args.atraso, "Procurando imagens", console.print)
        resultados = imagens.procurar_na_tela(args.tela or None, config.carregar_geral()["confianca_imagem"])
        if not resultados:
            console.print("Nenhuma imagem cadastrada para essa tela.")
            return 1
    else:
        resultados = checagem.checar()
    t = Table(title="Pré-checagem")
    t.add_column("Item")
    t.add_column("Status")
    t.add_column("Detalhe")
    for item, ok, detalhe in resultados:
        t.add_row(item, "[green]✅ ok[/]" if ok else "[red]❌ problema[/]", detalhe)
    console.print(t)
    return 0 if all(ok for _, ok, _ in resultados) else 1


def cmd_grupos(_args) -> int:
    geral = config.carregar_geral()
    t = Table(title="Grupos de filiais")
    t.add_column("grupo")
    t.add_column("filiais")
    for nome, filiais in (geral.get("grupos") or {}).items():
        t.add_row(nome, ", ".join(map(str, filiais)))
    console.print(t)
    return 0


def cmd_capturar(args) -> int:
    destino = imagens.capturar(args.nome, args.atraso, console.print)
    console.print(f"[green]✅ Print salvo:[/] {destino}")
    return 0


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="python -m linear", description="Automações Linear (SGLinear)")
    sub = parser.add_subparsers(dest="comando", required=True)
    sub.add_parser("perfis", help="lista os perfis disponíveis").set_defaults(func=cmd_perfis)
    p = sub.add_parser("checar", help="confere o ambiente sem clicar em nada")
    p.add_argument("--tela", nargs="?", const="", default=None,
                   help="procura as imagens do catálogo na tela atual (opcional: só as de uma tela)")
    p.add_argument("--atraso", type=int, default=5, help="segundos antes de procurar (padrão 5)")
    p.set_defaults(func=cmd_checar)
    sub.add_parser("grupos", help="lista os grupos de filiais").set_defaults(func=cmd_grupos)
    p = sub.add_parser("capturar", help="tira um print da tela inteira após uma contagem")
    p.add_argument("nome", help="nome do print, ex.: tela_inicial")
    p.add_argument("--atraso", type=int, default=8, help="segundos antes do print (padrão 8)")
    p.set_defaults(func=cmd_capturar)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
