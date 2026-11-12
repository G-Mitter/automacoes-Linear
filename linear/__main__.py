"""Linha de comando: python -m linear <comando>."""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pyautogui
from rich.console import Console
from rich.table import Table

from . import checagem, config, downloads, imagens, organizador

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


def _salvar_execucao(exe: dict) -> None:
    pasta = Path(__file__).resolve().parent.parent / "execucoes"
    pasta.mkdir(exist_ok=True)
    (pasta / f"{exe['id']}.json").write_text(json.dumps(exe, ensure_ascii=False, indent=2), encoding="utf-8")


def cmd_run(args) -> int:
    """E5: um relatório por item (individual, por grupo ou consolidado), em PDF, Excel ou ambos.

    Se um item falhar, fecha as telas e segue para o próximo (retentativas chegam na E6).
    """
    from .rotinas import relatorio_padrao as rotina
    from .tela import ErroConfiguracao, Tela, TelaErro

    geral = config.carregar_geral()
    perfis = config.carregar_perfis()
    perfil = perfis.get(args.perfil)
    if not perfil:
        console.print(f"[red]Perfil '{args.perfil}' não existe.[/] Disponíveis: {', '.join(perfis)}")
        return 1
    erros = config.validar_perfil(perfil, geral)
    modo = args.modo or perfil.get("modo_filiais", "individual")
    itens = []
    try:
        itens = config.montar_itens(args.filiais or perfil.get("filiais_padrao"), geral, modo)
        fora = {f for _, fs in itens for f in fs} - set(geral["filiais_ativas"])
        if fora:
            erros.append(f"filiais fora da lista ativa: {sorted(fora)}")
    except ValueError as e:
        erros.append(str(e))
    formato = args.formato or perfil["formato"]
    formatos = ["pdf", "xlsx"] if formato == "ambos" else [formato]
    ontem = date.today() - timedelta(days=1)
    de = args.de or ontem
    ate = args.ate or de
    if de > ate:
        erros.append("a data De é maior que a data Até")
    for item, ok, detalhe in checagem.checar():
        if not ok and item in ("Resolução", "Escala do Windows", "Pasta Downloads", "Pasta base"):
            erros.append(f"{item}: {detalhe}")
    if args.a_partir not in rotina.ETAPAS:
        erros.append(f"--a-partir precisa ser uma de: {', '.join(rotina.ETAPAS)}")
    if args.a_partir == "E-08" and not args.nome:
        erros.append("--a-partir E-08 precisa do --nome do arquivo já exportado no servidor (sem extensão)")
    if args.a_partir != "E-01" and (len(itens) > 1 or len(formatos) > 1):
        erros.append("--a-partir só funciona com um relatório e um formato")
    if erros:
        for e in erros:
            console.print(f"[red]❌ {e}[/]")
        return 1

    console.print(f"[bold]{perfil['nome']}[/] · {modo} · {len(itens)} relatório(s) · "
                  f"{de:%d/%m/%Y} a {ate:%d/%m/%Y} · {formato}")
    console.print("Solte o mouse. Para parar: leve o mouse ao [bold]canto superior esquerdo[/].")
    imagens.contagem(5, "Começando", console.print)

    t = Tela(geral["confianca_imagem"], depurar=args.depurar, avisar=console.print,
             pausa_ms=geral.get("pausa_entre_acoes_ms", 400))
    pasta_dl = Path(geral["pasta_downloads"])
    agora = datetime.now()
    exe = {"id": f"{agora:%Y-%m-%d_%H%M%S}", "perfil_id": args.perfil, "modo_filiais": modo,
           "formato": formato, "periodo_de": str(de), "periodo_ate": str(ate),
           "filiais": sorted({f for _, fs in itens for f in fs}), "origem": "run",
           "execucao_origem_id": None, "inicio": agora.isoformat(timespec="seconds"), "fim": None,
           "status": "em_andamento", "motivo_aborto": None, "arquivo_log": None, "itens": []}
    _salvar_execucao(exe)

    for n, (escopo, filiais) in enumerate(itens, 1):
        console.print(f"[blue]⏳ {n}/{len(itens)} {escopo}[/] filiais {filiais}")
        it = {"escopo": escopo, "filiais": filiais, "status": "pendente", "tentativas": 1,
              "arquivos_finais": [], "erros": [], "inicio": datetime.now().isoformat(timespec="seconds"),
              "fim": None}
        exe["itens"].append(it)
        try:
            for k, fmt in enumerate(formatos):
                pedido = rotina.Pedido(
                    menu=perfil["menu"], modelo_filtro=perfil["modelo_filtro"], filiais=filiais, de=de, ate=ate,
                    formato=fmt,
                    nome_servidor=args.nome or f"{perfil['processo']}_{escopo}_{datetime.now():%H%M%S}",
                    pasta_servidor=geral["pasta_servidor"], espera=geral["espera_padrao_s"],
                    opcao_relatorio=perfil.get("opcao_relatorio", "analitico"))
                antes = downloads.fotografar(pasta_dl)
                # no 2º formato a visualização continua aberta: começa direto no Exportar
                arquivo = rotina.executar(t, pedido, args.a_partir if k == 0 else "E-07")
                baixado = downloads.esperar_novo(pasta_dl, antes, arquivo, geral["espera_download_s"])
                final = organizador.organizar(baixado, Path(geral["pasta_base"]), perfil["processo"],
                                              de, ate, escopo)
                it["arquivos_finais"].append(str(final))
                console.print(f"[green]✅ {escopo}[/] {final}")
            it["status"] = "ok"
            rotina.fechar_telas(t)
        except pyautogui.FailSafeException:
            it["status"] = "falha"
            exe.update(status="abortada", motivo_aborto="parada de emergência")
            console.print("[yellow]⚠️ Parada de emergência acionada. Execução interrompida.[/]")
            break
        except (TelaErro, ErroConfiguracao, TimeoutError) as e:
            prt = t.print_tela(f"erro_{escopo}")
            it["status"] = "falha"
            it["erros"].append({"tentativa": 1, "passo": None, "tipo": type(e).__name__,
                                "mensagem": str(e), "print": str(prt)})
            console.print(f"[red]❌ {escopo}[/] {e} · print: {prt}")
            if isinstance(e, ErroConfiguracao):
                exe.update(status="abortada", motivo_aborto=str(e))
                break
            try:                                   # volta à tela inicial e segue para o próximo
                rotina.fechar_telas(t)
            except (TelaErro, TimeoutError):
                exe.update(status="abortada", motivo_aborto=f"não voltou à tela inicial depois de {escopo}")
                console.print("[red]Não consegui voltar à tela inicial. Parando.[/]")
                break
        finally:
            it["fim"] = datetime.now().isoformat(timespec="seconds")
            _salvar_execucao(exe)

    ok = sum(i["status"] == "ok" for i in exe["itens"])
    if exe["status"] == "em_andamento":
        exe["status"] = "concluida" if ok == len(itens) else "concluida_com_falhas"
    exe["fim"] = datetime.now().isoformat(timespec="seconds")
    _salvar_execucao(exe)

    tab = Table(title=f"Resumo · execução {exe['id']}")
    for col in ("escopo", "status", "arquivos / erro"):
        tab.add_column(col)
    for i in exe["itens"]:
        det = "\n".join(Path(a).name for a in i["arquivos_finais"]) or (i["erros"][-1]["mensagem"] if i["erros"] else "")
        tab.add_row(i["escopo"], "[green]✅ ok[/]" if i["status"] == "ok" else "[red]❌ falha[/]", det)
    for esc, _ in itens[len(exe["itens"]):]:
        tab.add_row(esc, "[yellow]⏸ não rodou[/]", "")
    console.print(tab)
    console.print(f"{ok} de {len(itens)} ok · histórico em execucoes/{exe['id']}.json")
    if exe["status"] == "abortada" and exe["motivo_aborto"] == "parada de emergência":
        return 2
    return 0 if ok == len(itens) else 1


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
    p.add_argument("--modo", choices=["individual", "por_grupo", "consolidado"],
                   help="individual (1 por filial), por_grupo (1 por grupo) ou consolidado (1 só)")
    p.add_argument("--a-partir", default="E-01", metavar="ETAPA",
                   help="começa nesta etapa (E-03b, E-04, E-05, E-07, E-08...); deixe a tela no ponto certo antes")
    p.add_argument("--nome", help="nome do arquivo no servidor, sem extensão (obrigatório com --a-partir E-08)")
    p.add_argument("--depurar", action="store_true", help="tira um print a cada passo (logs/prints)")
    p.set_defaults(func=cmd_run)
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
