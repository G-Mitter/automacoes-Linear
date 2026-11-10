"""Coletor de download: acha o arquivo novo e completo na pasta Downloads (TRD §3)."""
from __future__ import annotations

import time
from pathlib import Path

TEMPORARIOS = {".crdownload", ".tmp", ".part"}


def fotografar(pasta: Path) -> set[str]:
    return {p.name for p in pasta.iterdir()} if pasta.exists() else set()


def esperar_novo(pasta: Path, antes: set[str], nome_esperado: str, timeout: float) -> Path:
    """Espera surgir um arquivo novo parecido com `nome_esperado` (aceita 'nome (1).ext').

    Considera completo quando não é temporário e o tamanho fica estável por 1 s.
    """
    base, _, ext = nome_esperado.rpartition(".")
    fim = time.monotonic() + timeout
    while time.monotonic() < fim:
        for nome in fotografar(pasta) - antes:
            arq = pasta / nome
            if arq.suffix.lower() in TEMPORARIOS or not nome.startswith(base):
                continue
            if not nome.lower().endswith("." + ext.lower()):
                continue
            tamanho = arq.stat().st_size
            time.sleep(1)
            if tamanho > 0 and arq.stat().st_size == tamanho:
                return arq
        time.sleep(0.5)
    raise TimeoutError(f"o arquivo {nome_esperado} não chegou em {pasta} em {timeout:.0f}s")
