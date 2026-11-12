"""Organizador: move o arquivo baixado para <pasta base>\\<Processo>\\ com o nome da RN-03."""
from __future__ import annotations

import shutil
from datetime import date
from pathlib import Path


def periodo(de: date, ate: date) -> str:
    return f"{de:%Y-%m-%d}" if de == ate else f"{de:%Y-%m-%d}_a_{ate:%Y-%m-%d}"


def nome_final(processo: str, de: date, ate: date, escopo: str, ext: str) -> str:
    return f"{processo}_{periodo(de, ate)}_{escopo}.{ext}"


def livre(destino: Path) -> Path:
    """RN-05: nunca sobrescreve; acrescenta _2, _3... ao nome."""
    n, alvo = 2, destino
    while alvo.exists():
        alvo = destino.with_name(f"{destino.stem}_{n}{destino.suffix}")
        n += 1
    return alvo


def pasta_lote(processo: str, de: date, ate: date) -> str:
    """Subpasta de uma execução com vários relatórios: <Processo>_<período>."""
    return f"{processo}_{periodo(de, ate)}"


def organizar(arquivo: Path, pasta_base: Path, processo: str, de: date, ate: date, escopo: str,
              lote: bool = False) -> Path:
    pasta = pasta_base / processo
    if lote:                                   # vários relatórios: todos juntos numa pasta do período
        pasta = pasta / pasta_lote(processo, de, ate)
    pasta.mkdir(parents=True, exist_ok=True)
    ext = arquivo.suffix.lstrip(".").lower()
    alvo = livre(pasta / nome_final(processo, de, ate, escopo, ext))
    return Path(shutil.move(str(arquivo), str(alvo)))
