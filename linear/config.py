"""Leitura e validação da configuração (docs/05-BACKEND.md §1 e §4)."""
from __future__ import annotations

import importlib
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
PASTA_CONFIG = RAIZ / "config"
PASTA_PERFIS = PASTA_CONFIG / "perfis"
PASTA_IMAGENS = RAIZ / "assets" / "imagens"

FORMATOS = {"pdf", "xlsx"}
MODOS = {"individual", "consolidado"}


def carregar_geral() -> dict:
    return yaml.safe_load((PASTA_CONFIG / "geral.yaml").read_text(encoding="utf-8"))


def carregar_perfis() -> dict[str, dict]:
    perfis = {}
    for arq in sorted(PASTA_PERFIS.glob("*.yaml")):
        dados = yaml.safe_load(arq.read_text(encoding="utf-8")) or {}
        dados["id"] = arq.stem
        perfis[arq.stem] = dados
    return perfis


def resolver_filiais(valor, geral: dict) -> list[int]:
    """Aceita 'todas', lista de inteiros ou texto '3,4,6'."""
    if valor in (None, "todas"):
        return list(geral["filiais_ativas"])
    if isinstance(valor, str):
        valor = [int(x) for x in valor.split(",") if x.strip()]
    return [int(x) for x in valor]


def validar_perfil(perfil: dict, geral: dict) -> list[str]:
    """Devolve a lista de problemas (vazia = perfil válido)."""
    erros = []
    for campo in ("nome", "processo", "rotina", "menu", "modelo_filtro", "formato", "modo_filiais"):
        if not perfil.get(campo):
            erros.append(f"campo obrigatório ausente: {campo}")
    if perfil.get("formato") not in FORMATOS:
        erros.append(f"formato inválido: {perfil.get('formato')} (use pdf ou xlsx)")
    if perfil.get("modo_filiais") not in MODOS:
        erros.append(f"modo_filiais inválido: {perfil.get('modo_filiais')}")
    if perfil.get("modelo_filtro") == "A DEFINIR":
        erros.append("modelo_filtro ainda não definido (será feito na E2)")
    try:
        fora = set(resolver_filiais(perfil.get("filiais_padrao"), geral)) - set(geral["filiais_ativas"])
        if fora:
            erros.append(f"filiais fora da lista ativa: {sorted(fora)}")
    except ValueError:
        erros.append("filiais_padrao inválido")
    try:
        rotina = importlib.import_module(f"linear.rotinas.{perfil.get('rotina')}")
        faltando = [n for n in getattr(rotina, "IMAGENS_NECESSARIAS", [])
                    if not (PASTA_IMAGENS / f"{n}.png").exists()]
        if faltando:
            erros.append(f"imagens de referência faltando: {faltando}")
    except ImportError:
        erros.append(f"rotina não existe: {perfil.get('rotina')}")
    return erros
