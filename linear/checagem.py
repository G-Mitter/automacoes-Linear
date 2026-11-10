"""Pré-checagem: confere o ambiente sem clicar em nada (Plano E1)."""
from __future__ import annotations

import ctypes
from pathlib import Path

import pyautogui

from . import config


def escala_windows() -> int:
    """Escala de tela do Windows em % (100, 125, 150...)."""
    ctypes.windll.user32.SetProcessDPIAware()
    return round(ctypes.windll.user32.GetDpiForSystem() * 100 / 96)


def checar() -> list[tuple[str, bool, str]]:
    """Devolve [(item, ok, detalhe)]."""
    geral = config.carregar_geral()
    res = []

    esperado = str(geral["resolucao"])
    largura, altura = pyautogui.size()
    atual = f"{largura}x{altura}"
    res.append(("Resolução", atual == esperado, f"{atual} (esperado {esperado})"))

    escala = escala_windows()
    res.append(("Escala do Windows", escala == geral["escala_windows"],
                f"{escala}% (esperado {geral['escala_windows']}%)"))

    base = Path(geral["pasta_base"])
    pode = base.exists() or Path(base.anchor).exists()
    res.append(("Pasta base", pode, f"{base} ({'existe' if base.exists() else 'será criada' if pode else 'unidade não existe'})"))

    dl = Path(geral["pasta_downloads"])
    res.append(("Pasta Downloads", dl.exists(), str(dl)))

    perfis = config.carregar_perfis()
    res.append(("Perfis", bool(perfis), f"{len(perfis)} encontrado(s)"))
    for pid, perfil in perfis.items():
        erros = config.validar_perfil(perfil, geral)
        res.append((f"Perfil {pid}", not erros, "; ".join(erros) or "ok"))
    return res
