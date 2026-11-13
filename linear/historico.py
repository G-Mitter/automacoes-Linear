"""Leitura do histórico de execuções (execucoes/*.json). Usado pelo CLI e pela UI."""
from __future__ import annotations

import json
from pathlib import Path

PASTA_EXECUCOES = Path(__file__).resolve().parent.parent / "execucoes"


def listar(limite: int = 20) -> list[dict]:
    """As execuções mais recentes primeiro, pelo nome do arquivo (= id = data_hora)."""
    if not PASTA_EXECUCOES.exists():
        return []
    arquivos = sorted(PASTA_EXECUCOES.glob("*.json"), reverse=True)[:limite]
    execs = []
    for a in arquivos:
        try:
            execs.append(json.loads(a.read_text(encoding="utf-8")))
        except (json.JSONDecodeError, OSError):
            continue
    return execs


def ultima() -> dict | None:
    execs = listar(1)
    return execs[0] if execs else None


def em_andamento() -> dict | None:
    """A última execução, só se ainda não tiver terminado."""
    ult = ultima()
    return ult if ult and ult.get("status") == "em_andamento" else None


def erros_recentes(limite: int = 30) -> list[dict]:
    """Erros de todas as filiais/itens das últimas execuções, mais recentes primeiro."""
    saida = []
    for exe in listar(10):
        for item in exe.get("itens", []):
            for erro in item.get("erros", []):
                saida.append({"execucao_id": exe["id"], "escopo": item["escopo"], **erro})
    return saida[:limite]
