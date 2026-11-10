"""Linha de comando: python -m linear <comando>."""
from __future__ import annotations

import argparse
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pyautogui
from rich.console import Console
from rich.table import Table

from . import checagem, config, downloads, imagens

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


def _data(texto: str) -> date:
    return datetime.strptime(texto, "%Y-%m-%d").date()


def cmd_run(args) -> int:
    """E3: executa a rotina para cada filial, uma por vez (modo individual, sem retentativas)."""
    from .rotinas import relatorio_padrao as rotina
    from .tela import ErroConfiguracao, Tela, TelaErro

    geral = config.carregar_geral()
    perfis = config.carregar_perfis()
    perfil = perfis.get(args.perfil)
    if not perfil:
        console.print(f"[red]Perfil '{args.perfil}' não existe.[/] Disponíveis: {', '.join(perfis)}")
        return 1
    erros = config.validar_perfil(perfil, geral)
    try:
        filiais = config.resolver_filiais(args.filiais or perfil.get("filiais_padrao"), geral)
        fora = set(filiais) - set(geral["filiais_ativas"])
        if fora:
            erros.append(f"filiais fora da lista ativa: {sorted(fora)}")
    except ValueError as e:
        erros.append(str(e))
    formato = args.formato or perfil["formato"]
    if formato == "ambos":
        erros.append("formato 'ambos' chega na etapa E5; use pdf ou xlsx")
    ontem = date.today() - timedelta(days=1)
    de = args.de or ontem
    ate = args.ate or de
    if de > ate:
        erros.append("a data De é maior que a data Até")
    for item, ok, detalhe in checagem.checar():
        if not ok and item in ("Resolução", "Escala do Windows", "Pasta Downloads"):
            erros.append(f"{item}: {detalhe}")
    if erros:
        for e in erros:
            console.print(f"[red]❌ {e}[/]")
        return 1

    console.print(f"[bold]{perfil['nome']}[/] · filiais {filiais} · {de:%d/%m/%Y} a {ate:%d/%m/%Y} · {formato}")
    console.print("Solte o mouse. Para parar: leve o mouse ao [bold]canto superior esquerdo[/].")
    imagens.contagem(5, "Começando", console.print)

    t = Tela(geral["confianca_imagem"], depurar=args.depurar, avisar=console.print)
    pasta_dl = Path(geral["pasta_downloads"])
    falhas = 0
    for f in filiais:
        console.print(f"[blue]⏳ F{f:02d}[/]")
        pedido = rotina.Pedido(
            menu=perfil["menu"], modelo_filtro=perfil["modelo_filtro"], filiais=[f], de=de, ate=ate,
            formato=formato, nome_servidor=f"{perfil['processo']}_F{f:02d}_{datetime.now():%H%M%S}",
            pasta_servidor=geral["pasta_servidor"], espera=geral["espera_padrao_s"])
        antes = downloads.fotografar(pasta_dl)
        try:
            arquivo = rotina.executar(t, pedido)
            baixado = downloads.esperar_novo(pasta_dl, antes, arquivo, geral["espera_download_s"])
            console.print(f"[green]✅ F{f:02d}[/] {baixado}")
            rotina.fechar_telas(t)
        except pyautogui.FailSafeException:
            console.print("[yellow]⚠️ Parada de emergência acionada. Execução interrompida.[/]")
            return 2
        except (TelaErro, ErroConfiguracao, TimeoutError) as e:
            falhas += 1
            prt = t.print_tela(f"erro_F{f:02d}")
            console.print(f"[red]❌ F{f:02d}[/] {e} · print: {prt}")
            return 1   # E3: para no primeiro erro (retentativas chegam na E6)
    return 0 if not falhas else 1


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
    p = sub.add_parser("run", help="executa um perfil")
    p.add_argument("perfil")
    p.add_argument("--filiais", help="ex.: 3,4,6 ou seneto,60 ou todas")
    p.add_argument("--de", type=_data, help="data inicial AAAA-MM-DD (padrão: ontem)")
    p.add_argument("--ate", type=_data, help="data final AAAA-MM-DD (padrão: igual ao --de)")
    p.add_argument("--formato", choices=["pdf", "xlsx", "ambos"])
    p.add_argument("--depurar", action="store_true", help="tira um print a cada passo (logs/prints)")
    p.set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
