"""Camada de tela: achar imagens, clicar, digitar e esperar (TRD §2, camada 1).

Toda espera tem tempo máximo. Nada de sleep fixo longo: sempre "esperar a imagem X".
"""
from __future__ import annotations

import time
from datetime import datetime
from pathlib import Path

import pyautogui

from . import config, imagens

pyautogui.FAILSAFE = True   # mouse no canto superior esquerdo = parada de emergência
pyautogui.PAUSE = 0.15      # pequena pausa entre ações do pyautogui

PASTA_PRINTS = config.RAIZ / "logs" / "prints"


class TelaErro(Exception):
    """Algo não apareceu/sumiu a tempo. A tentativa pode ser repetida."""


class ErroConfiguracao(TelaErro):
    """Erro de configuração (ex.: modelo de filtro não existe). Não adianta repetir."""


class Tela:
    def __init__(self, confianca: float, depurar: bool = False, avisar=print):
        cat = imagens.carregar_catalogo_completo()
        self.imagens = cat.get("imagens", {})
        self.fixas = cat.get("posicoes_fixas", {})
        self.tipos_exportar = cat.get("tipos_exportar", {})
        self.confianca = confianca
        self.depurar = depurar
        self.avisar = avisar
        self._passo = 0

    # ---------- procurar ----------
    def localizar(self, nome: str):
        """Posição (Box) da imagem na tela agora, ou None."""
        info = self.imagens.get(nome)
        if info is None:
            raise KeyError(f"imagem não cadastrada no catálogo: {nome}")
        regiao = tuple(info["regiao"]) if info.get("regiao") else None
        try:
            return pyautogui.locateOnScreen(str(config.PASTA_IMAGENS / f"{nome}.png"),
                                            confidence=self.confianca, region=regiao)
        except pyautogui.ImageNotFoundException:
            return None

    def esperar(self, nome: str, timeout: float = 30):
        fim = time.monotonic() + timeout
        while True:
            pos = self.localizar(nome)
            if pos:
                return pos
            if time.monotonic() > fim:
                raise TelaErro(f"'{nome}' não apareceu em {timeout:.0f}s")
            time.sleep(0.4)

    def esperar_sumir(self, nome: str, timeout: float = 30) -> None:
        fim = time.monotonic() + timeout
        while self.localizar(nome):
            if time.monotonic() > fim:
                raise TelaErro(f"'{nome}' não sumiu em {timeout:.0f}s")
            time.sleep(0.4)

    # ---------- agir ----------
    def clicar(self, nome: str, timeout: float = 30, dx: int = 0, dy: int = 0,
               a_partir: str = "centro", cliques: int = 1):
        """Clica na imagem. a_partir='direita' mede dx a partir da borda direita."""
        pos = self.esperar(nome, timeout)
        x = (pos.left + pos.width if a_partir == "direita" else pos.left + pos.width // 2) + dx
        y = pos.top + pos.height // 2 + dy
        pyautogui.click(x, y, clicks=cliques, interval=0.1)
        return pos

    def clicar_xy(self, x: int, y: int, cliques: int = 1) -> None:
        pyautogui.click(x, y, clicks=cliques, interval=0.1)

    def clicar_fixo(self, nome: str) -> None:
        p = self.fixas[nome]
        pyautogui.click(p["x"], p["y"])

    def digitar(self, texto: str) -> None:
        pyautogui.write(texto, interval=0.03)

    def tecla(self, *teclas: str, vezes: int = 1) -> None:
        for _ in range(vezes):
            if len(teclas) > 1:
                pyautogui.hotkey(*teclas)
            else:
                pyautogui.press(teclas[0])

    def cor(self, x: int, y: int) -> tuple[int, int, int]:
        return pyautogui.pixel(x, y)

    # ---------- registro ----------
    def print_tela(self, motivo: str) -> Path:
        PASTA_PRINTS.mkdir(parents=True, exist_ok=True)
        destino = PASTA_PRINTS / f"{datetime.now():%Y-%m-%d_%H%M%S}_{motivo}.png"
        pyautogui.screenshot().save(destino)
        return destino

    def passo(self, descricao: str) -> None:
        """Marca o início de um passo; no modo depurar, tira um print."""
        self._passo += 1
        self.avisar(f"  · {descricao}")
        if self.depurar:
            self.print_tela(f"passo{self._passo:02d}")
