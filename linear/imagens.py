"""Catálogo de imagens de referência e captura de tela (Plano E2)."""
from __future__ import annotations

import time
from datetime import datetime

import pyautogui
import yaml

from . import config

CATALOGO = config.PASTA_IMAGENS / "catalogo.yaml"
PASTA_CAPTURAS = config.RAIZ / "capturas"


def carregar_catalogo() -> dict[str, dict]:
    """{nome: {descricao, tela, regiao?}}"""
    if not CATALOGO.exists():
        return {}
    return (yaml.safe_load(CATALOGO.read_text(encoding="utf-8")) or {}).get("imagens", {})


def contagem(segundos: int, msg: str, avisar=print) -> None:
    for s in range(segundos, 0, -1):
        avisar(f"{msg} em {s}s…")
        time.sleep(1)


def capturar(nome: str, atraso: int, avisar=print):
    """Tira um print da tela inteira depois de `atraso` segundos."""
    PASTA_CAPTURAS.mkdir(exist_ok=True)
    contagem(atraso, "Capturando", avisar)
    destino = PASTA_CAPTURAS / f"{nome}_{datetime.now():%H%M%S}.png"
    pyautogui.screenshot().save(destino)
    return destino


def procurar_na_tela(tela: str | None, confianca: float) -> list[tuple[str, bool, str]]:
    """Procura cada imagem do catálogo (filtrando pela tela) sem clicar."""
    res = []
    for nome, info in carregar_catalogo().items():
        if tela and info.get("tela") != tela:
            continue
        arq = config.PASTA_IMAGENS / f"{nome}.png"
        if not arq.exists():
            res.append((nome, False, "arquivo PNG não existe"))
            continue
        try:
            pos = pyautogui.locateOnScreen(str(arq), confidence=confianca,
                                           region=tuple(info["regiao"]) if info.get("regiao") else None)
        except pyautogui.ImageNotFoundException:
            pos = None
        res.append((nome, pos is not None,
                    f"encontrada em x={pos.left}, y={pos.top}" if pos else "não encontrada"))
    return res
