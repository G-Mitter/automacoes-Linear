"""Leitura e validação da configuração (docs/05-BACKEND.md §1 e §4)."""
from __future__ import annotations

import importlib
from pathlib import Path

import yaml

RAIZ = Path(__file__).resolve().parent.parent
PASTA_CONFIG = RAIZ / "config"
PASTA_PERFIS = PASTA_CONFIG / "perfis"
PASTA_IMAGENS = RAIZ / "assets" / "imagens"

FORMATOS = {"pdf", "xlsx", "ambos"}
MODOS = {"individual", "por_grupo", "consolidado"}


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
    """Aceita 'todas', ou lista/texto com números e nomes de grupo: '3,seneto,60'.

    Lança ValueError para grupo desconhecido.
    """
    if valor in (None, "todas"):
        return list(geral["filiais_ativas"])
    if isinstance(valor, str):
        valor = [x.strip() for x in valor.split(",") if x.strip()]
    grupos = {nome.lower(): filiais for nome, filiais in (geral.get("grupos") or {}).items()}
    filiais: list[int] = []
    for item in valor:
        texto = str(item).strip()
        if texto.lower() == "todas":
            novas = geral["filiais_ativas"]
        elif texto.isdigit():
            novas = [int(texto)]
        elif texto.lower() in grupos:
            novas = grupos[texto.lower()]
        else:
            raise ValueError(f"grupo ou filial desconhecido: {texto}")
        filiais += [f for f in novas if f not in filiais]
    return filiais


def montar_itens(valor, geral: dict, modo: str) -> list[tuple[str, list[int]]]:
    """Divide o pedido em relatórios: [(escopo, filiais)].

    individual → um por filial (F03...); consolidado → um só com todas;
    por_grupo → um por grupo citado ('todas' = todos os grupos); números soltos saem individuais.
    """
    filiais = resolver_filiais(valor, geral)
    if modo == "individual":
        return [(f"F{f:02d}", [f]) for f in filiais]
    if modo == "consolidado":
        return [("Consolidado", filiais)]
    grupos = {n.lower(): (n, fs) for n, fs in (geral.get("grupos") or {}).items()}
    if valor in (None, "todas"):
        valor = ["todas"]
    elif isinstance(valor, str):
        valor = [x.strip() for x in valor.split(",") if x.strip()]
    itens: list[tuple[str, list[int]]] = []
    for item in valor:
        texto = str(item).strip().lower()
        if texto == "todas":
            itens += [(n, list(fs)) for n, fs in grupos.values()]
        elif texto in grupos:
            itens.append((grupos[texto][0], list(grupos[texto][1])))
        else:
            itens.append((f"F{int(texto):02d}", [int(texto)]))
    vistos, unicos = set(), []
    for esc, fs in itens:
        if esc not in vistos:
            vistos.add(esc)
            unicos.append((esc, fs))
    return unicos


def validar_geral(geral: dict) -> list[str]:
    """Cada filial de grupo precisa estar em filiais_ativas."""
    ativas = set(geral["filiais_ativas"])
    return [f"grupo {nome}: filiais fora da lista ativa {sorted(set(fs) - ativas)}"
            for nome, fs in (geral.get("grupos") or {}).items() if set(fs) - ativas]


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
    except ValueError as e:
        erros.append(f"filiais_padrao inválido: {e}")
    try:
        rotina = importlib.import_module(f"linear.rotinas.{perfil.get('rotina')}")
        faltando = [n for n in getattr(rotina, "IMAGENS_NECESSARIAS", [])
                    if not (PASTA_IMAGENS / f"{n}.png").exists()]
        if faltando:
            erros.append(f"imagens de referência faltando: {faltando}")
    except ImportError:
        erros.append(f"rotina não existe: {perfil.get('rotina')}")
    return erros
