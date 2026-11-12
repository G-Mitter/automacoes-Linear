"""Rotina de relatório padrão do SGLinear (Fluxo E-01 a E-08).

Serve para relatórios com a mesma "cara" da Curva ABC: menu → Filtros/Posicionar →
De/Até → Filial(+) → Confirma → visualização → Exportar → Descarregar.
Os deslocamentos (dx/dy) foram medidos nos prints em 1920x1080.
"""
from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import date

from ..tela import ErroConfiguracao, Tela, TelaErro

IMAGENS_NECESSARIAS = [
    "inicio_icones", "menu_relatorios", "menu_relatorios_gerenciais", "menu_curva_abc",
    "abc_titulo", "abc_btn_filtros", "abc_label_de", "abc_label_ate", "abc_label_filial",
    "abc_label_analitico", "abc_label_sintetico", "abc_btn_confirma", "abc_btn_sair",
    "filtros_titulo", "filtros_btn_pesquisar", "filtros_btn_posicionar",
    "filial_label_pesquisa", "filial_btn_desmarcar_todos", "filial_btn_confirmar",
    "vis_btn_exportar", "vis_icone_impressora", "exp_titulo", "exp_concluida", "exp_concluida_ok", "exp_label_nome", "exp_label_tipo",
    "desc_titulo", "desc_label_nome", "pasta_robo",
]

EXTENSOES = {"pdf": "pdf", "xlsx": "xlsx"}
ETAPAS = ["E-01", "E-02", "E-03", "E-03b", "E-04", "E-04b", "E-05", "E-07", "E-08"]
AZUL_SELECAO = (0, 120, 215)   # faixa azul de linha selecionada no Windows


@dataclass
class Pedido:
    menu: list[str]
    modelo_filtro: str
    filiais: list[int]
    de: date
    ate: date
    formato: str                # pdf | xlsx
    nome_servidor: str          # nome do arquivo no servidor, sem extensão
    pasta_servidor: str         # ex.: robo_linear
    opcao_relatorio: str = "analitico"   # analitico | sintetico
    espera: float = 30
    espera_relatorio: float = 180


def _perto(c1, c2, tol=40) -> bool:
    return all(abs(a - b) <= tol for a, b in zip(c1, c2))


def _data(d: date) -> str:
    return d.strftime("%d%m%y")   # o campo aceita só os dígitos: 01/10/26 → 011026


def _caminho_pasta(pasta: str) -> str:
    return f"shell:Desktop\\{pasta}"   # área de trabalho real, mesmo redirecionada


# Ícone de pasta no começo da barra de endereço (clicar nele deixa o endereço editável),
# medido a partir do título da janela. A largura da janela muda, mas esse ponto não.
BARRA_ENDERECO = {"exp_titulo": (111, 40), "desc_titulo": (112, 40)}


def _ir_para_pasta(t: Tela, titulo: str, pasta: str) -> None:
    """Vai para a pasta do robô pela barra de endereço, nunca pelo campo Nome:
    um Enter no campo Nome pode salvar o arquivo com o nome da pasta."""
    tit = t.esperar(titulo, 10)
    dx, dy = BARRA_ENDERECO[titulo]
    t.clicar_xy(tit.left + dx, tit.top + dy)
    time.sleep(0.3)
    t.tecla("ctrl", "a")
    t.digitar(_caminho_pasta(pasta))
    t.tecla("enter")
    t.esperar("pasta_robo", 10)


def executar(t: Tela, p: Pedido, a_partir: str = "E-01") -> str:
    """Faz E-01..E-08 e devolve o nome do arquivo (com extensão) que foi descarregado.

    `a_partir` pula as etapas anteriores (para testes: a tela precisa já estar no ponto certo).
    """
    if a_partir not in ETAPAS:
        raise ErroConfiguracao(f"etapa '{a_partir}' não existe; use uma de {', '.join(ETAPAS)}")
    ext = EXTENSOES[p.formato]
    arquivo = f"{p.nome_servidor}.{ext}"

    def faz(etapa: str) -> bool:
        return ETAPAS.index(etapa) >= ETAPAS.index(a_partir)


    if faz("E-01"):
        # E-01 tela inicial
        t.passo("E-01 conferindo a tela inicial")
        t.esperar("inicio_icones", 10)

    if faz("E-02"):
        # E-02 menu: Relatórios → (↓) Relatórios Gerenciais → (→) Curva ABC → Enter
        t.passo("E-02 abrindo o menu do relatório")
        t.clicar(p.menu[0], 10)
        t.tecla("down")
        t.esperar(p.menu[1], 5)
        t.tecla("right")
        t.esperar(p.menu[2], 5)
        t.tecla("enter")
        t.esperar("abc_titulo", p.espera)

    if faz("E-03"):
        # E-03 modelo de filtro: Filtros → digita → Pesquisar → linha azul → Posicionar
        t.passo(f"E-03 aplicando o modelo '{p.modelo_filtro}'")
        t.clicar_e_esperar("abc_btn_filtros", "filtros_titulo", assentar=1.5)
        pesq = t.esperar("filtros_btn_pesquisar", 5)
        cx, cy = pesq.left + pesq.width // 2, pesq.top + pesq.height // 2
        t.clicar_xy(cx - 300, cy)                 # campo "Digite a descrição do Filtro"
        t.tecla("ctrl", "a")
        t.digitar(p.modelo_filtro)
        t.clicar_xy(cx, cy)                       # Pesquisar
        time.sleep(1)
        t.clicar_xy(cx - 338, cy + 37)            # 1ª linha da lista
        time.sleep(0.5)
        if not _perto(t.cor(cx - 153, cy + 37), AZUL_SELECAO):
            t.print_tela("modelo_nao_encontrado")
            raise ErroConfiguracao(f"modelo de filtro '{p.modelo_filtro}' não encontrado")
        t.clicar("filtros_btn_posicionar")
        t.esperar_sumir("filtros_titulo", 10)

    if faz("E-03b"):
        # E-03b período (depois do modelo, para sobrescrever as datas salvas nele)
        t.passo(f"E-03b período {p.de:%d/%m/%Y} a {p.ate:%d/%m/%Y}")
        t.clicar("abc_label_de", dx=12, a_partir="direita")
        t.digitar(_data(p.de))
        t.clicar("abc_label_ate", dx=10, a_partir="direita")
        t.digitar(_data(p.ate))

    if faz("E-04"):
        # E-04 filiais: + → Desmarcar todos → (digita, marca a 1ª linha) → Confirmar
        t.passo(f"E-04 marcando filiais {p.filiais}")
        rot = t.clicar_e_esperar("abc_label_filial", "filial_label_pesquisa", dx=93, a_partir="direita")
        lx, ly = rot.left + rot.width // 2, rot.top + rot.height // 2
        t.clicar("filial_btn_desmarcar_todos")
        for f in p.filiais:
            t.clicar_xy(lx, ly + 22)              # campo de pesquisa
            t.tecla("ctrl", "a")
            t.digitar(str(f))
            time.sleep(0.6)
            t.clicar_xy(lx - 68, ly + 47)         # caixinha da 1ª linha
            time.sleep(0.3)
        if t.depurar:
            t.print_tela("filiais_marcadas")
        t.clicar("filial_btn_confirmar")
        t.esperar_sumir("filial_label_pesquisa", 10)

    if faz("E-04b"):
        # Opção Relatório: o ERP volta para "Sintético" ao aplicar a filial, então marcamos de novo aqui
        t.passo(f"E-04b opção do relatório: {p.opcao_relatorio}")
        rotulo = t.esperar(f"abc_label_{p.opcao_relatorio}", 5)
        bx, by = rotulo.left - 9, rotulo.top + rotulo.height // 2      # a bolinha fica à esquerda do texto
        for _ in range(3):
            t.clicar_xy(bx, by)
            if sum(t.cor(bx, by)) < 150:                                # miolo preto = marcada
                break
        else:
            raise TelaErro(f"não consegui marcar a opção '{p.opcao_relatorio}'")

    if faz("E-05"):
        # E-05 Confirma → espera a visualização
        t.passo("E-05 gerando o relatório")
        t.clicar_e_esperar("abc_btn_confirma", "vis_btn_exportar", tentativas=1,
                           espera_cada=p.espera_relatorio)

    if faz("E-07"):
        # E-06/E-07 Exportar → pasta do robô → apaga → tipo → nome → Salvar
        t.passo(f"E-07 exportando {p.nome_servidor}.{ext}")
        # ícone de exportar (ao lado da impressora): mais seguro que o botão "Exportar Relatório"
        t.esperar("vis_btn_exportar", 10)
        t.clicar_e_esperar("vis_icone_impressora", "exp_titulo", assentar=1.5, dx=-28)
        _ir_para_pasta(t, "exp_titulo", p.pasta_servidor)       # só apaga com a pasta do robô confirmada
        tit = t.esperar("exp_titulo", 5)
        t.clicar_xy(tit.left + tit.width // 2 + 339, tit.top + tit.height // 2 + 229)  # lista de arquivos
        t.tecla("ctrl", "a")
        t.tecla("delete")
        time.sleep(1)
        t.clicar("exp_label_tipo", dx=100, a_partir="direita")   # abre a lista "Tipo"
        time.sleep(0.3)
        t.tecla("home")
        t.tecla("down", vezes=t.tipos_exportar[p.formato])
        t.tecla("enter")
        t.clicar("exp_label_nome", dx=100, a_partir="direita")
        t.tecla("ctrl", "a")
        t.digitar(p.nome_servidor)
        t.tecla("enter")                           # Salvar
        t.esperar_sumir("exp_titulo", 20)
        # "Aguarde enquanto o documento é processado" → "Exportação concluída." → OK
        t.esperar("exp_concluida", 60)
        t.clicar_e_esperar("exp_concluida_ok", "vis_btn_exportar", assentar=0.5)
        t.esperar_sumir("exp_concluida", 10)

    if faz("E-08"):
        # E-08 barra do Terminal Server → descarregar → pasta do robô → Abrir
        t.passo("E-08 descarregando para o PC")
        t.clicar_fixo("ts_aba_recolhida")
        time.sleep(1.2)
        t.clicar_fixo("ts_icone_descarregar")
        t.esperar("desc_titulo", 15)
        _ir_para_pasta(t, "desc_titulo", p.pasta_servidor)
        t.clicar("desc_label_nome", dx=100, a_partir="direita")
        t.tecla("ctrl", "a")
        t.digitar(arquivo)
        t.tecla("enter")                           # Abrir
        t.esperar_sumir("desc_titulo", 15)
    return arquivo


def fechar_visualizacao(t: Tela, espera: float = 10) -> None:
    """Fecha só a visualização e fica na tela do relatório, pronta para a próxima filial."""
    if t.localizar("exp_concluida_ok"):
        t.clicar("exp_concluida_ok")
        t.esperar_sumir("exp_concluida", espera)
    if t.localizar("vis_btn_exportar"):
        t.clicar_fixo("vis_fechar")
        t.esperar_sumir("vis_btn_exportar", espera)
    t.esperar("abc_titulo", espera)


def fechar_telas(t: Tela, espera: float = 10) -> None:
    """Fecha a visualização e a janela do relatório, voltando à tela inicial."""
    if t.localizar("exp_concluida_ok"):             # mensagem que ficou aberta
        t.clicar("exp_concluida_ok")
        t.esperar_sumir("exp_concluida", espera)
    if t.localizar("vis_btn_exportar"):
        t.clicar_fixo("vis_fechar")
        t.esperar_sumir("vis_btn_exportar", espera)
    if t.localizar("abc_btn_sair"):
        t.clicar("abc_btn_sair")
        t.esperar_sumir("abc_titulo", espera)
    t.esperar("inicio_icones", espera)


__all__ = ["ETAPAS", "IMAGENS_NECESSARIAS", "Pedido", "executar", "fechar_telas", "TelaErro"]
