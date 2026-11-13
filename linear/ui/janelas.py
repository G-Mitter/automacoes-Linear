"""Achar e trazer para frente a janela do ERP (Windows), via ctypes — sem depender do pywin32."""
from __future__ import annotations

import ctypes
import sys

_SW_RESTORE = 9


def focar_janela(trecho_titulo: str) -> bool:
    """Procura uma janela visível cujo título contenha `trecho_titulo` e a traz para frente.

    Usado depois de iniciar uma automação, para o usuário não precisar clicar na barra de
    tarefas: o painel se esconde e o ERP volta a ocupar a tela sozinho.
    """
    if sys.platform != "win32":
        return False
    user32 = ctypes.windll.user32
    achada = None

    @ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    def callback(hwnd, _lparam):
        nonlocal achada
        if not user32.IsWindowVisible(hwnd):
            return True
        tamanho = user32.GetWindowTextLengthW(hwnd)
        if tamanho == 0:
            return True
        buf = ctypes.create_unicode_buffer(tamanho + 1)
        user32.GetWindowTextW(hwnd, buf, tamanho + 1)
        if trecho_titulo.lower() in buf.value.lower():
            achada = hwnd
            return False
        return True

    user32.EnumWindows(callback, 0)
    if not achada:
        return False
    if user32.IsIconic(achada):
        user32.ShowWindow(achada, _SW_RESTORE)
    user32.SetForegroundWindow(achada)
    return True
