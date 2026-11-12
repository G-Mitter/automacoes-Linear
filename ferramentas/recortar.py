"""Recorta as imagens de referência a partir dos prints em capturas/ (Plano E2).

Uso: .venv\\Scripts\\python ferramentas\\recortar.py
Cada linha de RECORTES: nome, prefixo do print, (x1, y1, x2, y2), tela, descrição.
"""
from __future__ import annotations

from pathlib import Path

import yaml
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
CAPTURAS = RAIZ / "capturas"
IMAGENS = RAIZ / "assets" / "imagens"

# A barra do Terminal Server é semitransparente (o fundo muda a imagem), então
# usamos posição fixa (topo central, 1920x1080) e confirmamos pela janela seguinte.
POSICOES_FIXAS = {
    "ts_aba_recolhida": {"x": 937, "y": 61, "descricao": "Aba recolhida da barra do Terminal Server"},
    "ts_icone_descarregar": {"x": 972, "y": 81, "descricao": "Ícone descarregar (nuvem com seta para baixo)"},
    "vis_fechar": {"x": 1879, "y": 66, "descricao": "X da janela de visualização (só clicar com a visualização aberta!)"},
}

# Áreas de busca [x, y, largura, altura] para recortes que aparecem em mais de um lugar.
REGIOES = {
    "menu_relatorios": [0, 75, 900, 30],
    "abc_label_filial": [900, 320, 120, 45],
    "abc_btn_confirma": [1100, 770, 220, 70],
    "filial_btn_confirmar": [1000, 640, 250, 80],
    "vis_btn_exportar": [400, 80, 300, 30],
    "vis_icone_impressora": [0, 80, 200, 30],
}

# Janelas que podem abrir em outro lugar: a busca é feita perto do título da janela
# (deslocamento x, y, largura, altura a partir do canto superior esquerdo do título).
RELATIVOS = {
    "exp_label_nome": ["exp_titulo", 30, 347, 120, 45],
    "exp_label_tipo": ["exp_titulo", 30, 372, 120, 45],
    "desc_label_nome": ["desc_titulo", 76, 387, 120, 45],
}

# Áreas onde um encontro é descartado (ex.: o botão "Exportar Relatório" da barra,
# que tem o mesmo texto do título da janela Exportar).
IGNORAR = {
    "exp_titulo": [[440, 75, 170, 25]],
}

# Tipo de arquivo na janela Exportar: escolhido pelo teclado (posição na lista).
TIPOS_EXPORTAR = {"pdf": 0, "csv": 1, "xls": 2, "xlsx": 3}

RECORTES = [
    # E-01 tela inicial
    ("inicio_icones", "tela_inicial_164053", (5, 100, 170, 152), "inicial", "Ícones Exportação e Painel NFCe da tela inicial"),
    ("menu_relatorios", "tela_inicial_164053", (412, 80, 472, 97), "inicial", "Menu Relatórios na barra de menus"),
    # E-02 menu
    ("menu_relatorios_gerenciais", "menu_aberto_164140", (440, 103, 560, 120), "menu", "Item Relatórios Gerenciais (destacado)"),
    ("menu_curva_abc", "menu_aberto_164140", (806, 103, 1052, 120), "menu", "Item Curva ABC / Contribuição Marginal de Venda (destacado)"),
    # E-03 tela da Curva ABC
    ("abc_titulo", "tela_abc_164212", (636, 263, 790, 279), "abc", "Título da janela Relatório Curva ABC"),
    ("abc_btn_filtros", "tela_abc_164212", (1064, 291, 1108, 310), "abc", "Botão Filtros"),
    ("abc_label_de", "tela_abc_164212", (680, 334, 712, 351), "abc", "Rótulo De: (campo à direita)"),
    ("abc_label_ate", "tela_abc_164212", (811, 334, 837, 351), "abc", "Rótulo Até: (campo à direita)"),
    ("abc_label_filial", "tela_abc_164212", (946, 334, 979, 351), "abc", "Rótulo Filial: (campo e botão + à direita)"),
    ("abc_label_analitico", "tela_abc_164212", (806, 680, 858, 695), "abc", "Texto Analítico (bolinha 9 px à esquerda)"),
    ("abc_label_sintetico", "tela_abc_164212", (806, 664, 856, 679), "abc", "Texto Sintético (bolinha 9 px à esquerda)"),
    ("abc_btn_confirma", "tela_abc_164212", (1141, 797, 1214, 819), "abc", "Botão Confirma"),
    ("abc_btn_sair", "tela_abc_164212", (1217, 797, 1286, 819), "abc", "Botão Sair"),
    # E-03 janela Filtro de Relatórios
    ("filtros_titulo", "filtros_164257", (680, 424, 785, 440), "filtros", "Título Filtro de Relatórios"),
    ("filtros_btn_pesquisar", "filtros_164257", (1171, 462, 1236, 482), "filtros", "Botão Pesquisar"),
    ("filtros_btn_posicionar", "filtros_164257", (937, 639, 1017, 658), "filtros", "Botão Posicionar"),
    # E-04 lista de filiais
    ("filial_label_pesquisa", "filial_lista_164352", (689, 420, 847, 435), "filial", "Rótulo Digite o texto para pesquisa"),
    ("filial_btn_marcar_todos", "filial_lista_164352", (692, 673, 781, 692), "filial", "Botão Marcar todos"),
    ("filial_btn_desmarcar_todos", "filial_lista_164352", (786, 673, 901, 692), "filial", "Botão Desmarcar todos"),
    ("filial_btn_confirmar", "filial_lista_164352", (1082, 673, 1151, 692), "filial", "Botão Confirmar"),
    # E-06 visualização
    ("vis_btn_exportar", "visualizacao_164628", (466, 85, 581, 102), "visualizacao", "Botão Exportar Relatório (só para conferir a tela)"),
    ("vis_icone_impressora", "visualizacao_164628", (33, 84, 54, 104), "visualizacao", "Ícone impressora; o ícone de exportar fica 28 px à esquerda"),
    # E-07 janela Exportar
    ("exp_titulo", "exportar_164953", (450, 113, 572, 130), "exportar", "Título Exportar Relatório"),
    ("exp_label_nome", "exportar_164953", (525, 475, 567, 492), "exportar", "Rótulo Nome: (campo à direita)"),
    ("exp_label_tipo", "exportar_164953", (534, 500, 567, 517), "exportar", "Rótulo Tipo: (lista à direita)"),
    ("exp_concluida", "exportacao_concluida_093252", (912, 553, 1030, 569), "exportar", "Mensagem Exportação concluída."),
    ("exp_concluida_ok", "exportacao_concluida_093252", (967, 609, 1043, 632), "exportar", "Botão OK da mensagem Exportação concluída"),
    # E-08 barra do Terminal Server e Descarregar arquivo
    ("desc_titulo", "descarregar_170037", (424, 128, 536, 145), "descarregar", "Título Descarregar arquivo"),
    ("pasta_robo", "descarregar_170037", (560, 160, 700, 177), "pasta_robo", "Barra de endereço em Desktop > robo_linear (confirma a pasta antes de apagar/salvar/abrir)"),
    ("desc_label_nome", "descarregar_170037", (546, 529, 589, 546), "descarregar", "Rótulo Nome: (campo à direita)"),
    ("desc_btn_abrir", "descarregar_170037", (881, 556, 969, 581), "descarregar", "Botão Abrir"),
]


def achar(prefixo: str) -> Path:
    arqs = sorted(CAPTURAS.glob(f"{prefixo}*.png"))
    if not arqs:
        raise FileNotFoundError(prefixo)
    return arqs[-1]


def main() -> None:
    catalogo = {}
    for nome, prefixo, caixa, tela, desc in RECORTES:
        Image.open(achar(prefixo)).crop(caixa).save(IMAGENS / f"{nome}.png")
        catalogo[nome] = {"descricao": desc, "tela": tela}
        if nome in REGIOES:
            catalogo[nome]["regiao"] = REGIOES[nome]
        if nome in RELATIVOS:
            catalogo[nome]["relativo_a"] = RELATIVOS[nome]
        if nome in IGNORAR:
            catalogo[nome]["ignorar"] = IGNORAR[nome]
    texto = ("# Imagens de referência (recortes tirados em 1920x1080, escala 100%, zoom 100%)\n"
             "# Gerado por ferramentas/recortar.py\n")
    (IMAGENS / "catalogo.yaml").write_text(
        texto + yaml.safe_dump({"imagens": catalogo, "posicoes_fixas": POSICOES_FIXAS,
                        "tipos_exportar": TIPOS_EXPORTAR}, allow_unicode=True, sort_keys=False), encoding="utf-8")
    print(f"{len(RECORTES)} recortes salvos em {IMAGENS}")


if __name__ == "__main__":
    main()
