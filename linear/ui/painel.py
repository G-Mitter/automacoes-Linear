"""Painel (UI1/UI2): árvore de automações por categoria, acompanhamento e erros."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel, QLineEdit,
                                QMessageBox, QPushButton, QStackedWidget, QTabWidget,
                                QTableWidget, QTableWidgetItem, QTreeWidget, QTreeWidgetItem,
                                QVBoxLayout, QWidget)

from .. import config, historico

CORES_STATUS = {
    "ok": "#1a7f37", "sem_dados": "#9a6700", "falha": "#cf222e",
    "pendente": "#57606a", "em_andamento": "#0969da", None: "#57606a",
}
ABA_AUTOMACOES, ABA_EXECUCAO, ABA_ERROS = range(3)


class _FormularioPerfil(QWidget):
    """Filiais, modo, formato e período de um perfil, com o botão Iniciar."""

    def __init__(self, pid: str, perfil: dict, geral: dict, on_iniciar) -> None:
        super().__init__()
        self.pid, self.on_iniciar = pid, on_iniciar
        l = QVBoxLayout(self)
        l.addWidget(QLabel(f"<b>{perfil.get('nome', pid)}</b>"))

        linha2 = QHBoxLayout()
        self.ed_filiais = QLineEdit(str(perfil.get("filiais_padrao", "todas")))
        self.ed_filiais.setToolTip("Números e/ou grupos separados por vírgula, ou 'todas'. "
                                    f"Grupos: {', '.join((geral.get('grupos') or {}))}")
        linha2.addWidget(QLabel("Filiais:")); linha2.addWidget(self.ed_filiais)
        l.addLayout(linha2)

        linha3 = QHBoxLayout()
        self.cb_modo = QComboBox(); self.cb_modo.addItems(["individual", "por_grupo", "consolidado"])
        self.cb_modo.setCurrentText(perfil.get("modo_filiais", "individual"))
        self.cb_formato = QComboBox(); self.cb_formato.addItems(["xlsx", "pdf", "ambos"])
        self.cb_formato.setCurrentText(perfil.get("formato", "xlsx"))
        linha3.addWidget(QLabel("Modo:")); linha3.addWidget(self.cb_modo)
        linha3.addWidget(QLabel("Formato:")); linha3.addWidget(self.cb_formato)
        l.addLayout(linha3)

        linha4 = QHBoxLayout()
        ontem = date.today() - timedelta(days=1)
        self.dt_de = QDateEdit(ontem); self.dt_de.setCalendarPopup(True)
        self.dt_ate = QDateEdit(ontem); self.dt_ate.setCalendarPopup(True)
        linha4.addWidget(QLabel("De:")); linha4.addWidget(self.dt_de)
        linha4.addWidget(QLabel("Até:")); linha4.addWidget(self.dt_ate)
        l.addLayout(linha4)

        btn = QPushButton("Iniciar"); btn.clicked.connect(self._iniciar)
        l.addWidget(btn)
        l.addStretch(1)

    def _iniciar(self) -> None:
        if historico.em_andamento():
            QMessageBox.warning(self, "Já em execução",
                                 "Já existe uma execução em andamento. Espere terminar ou cancele pelo terminal.")
            return
        self.on_iniciar([
            "run", self.pid,
            "--filiais", self.ed_filiais.text().strip() or "todas",
            "--modo", self.cb_modo.currentText(),
            "--formato", self.cb_formato.currentText(),
            "--de", self.dt_de.date().toString("yyyy-MM-dd"),
            "--ate", self.dt_ate.date().toString("yyyy-MM-dd"),
        ])


class Painel(QWidget):
    def __init__(self, on_iniciar) -> None:
        super().__init__()
        self.on_iniciar = on_iniciar
        self.setWindowTitle("Automações Linear")
        self.resize(720, 480)

        self.abas = QTabWidget()
        self.abas.addTab(self._aba_automacoes(), "Automações")
        self.abas.addTab(self._aba_execucao(), "Execução atual")
        self.abas.addTab(self._aba_erros(), "Erros")
        layout = QVBoxLayout(self)
        layout.addWidget(self.abas)
        self.atualizar()

    # ---------- Automações: árvore Categoria → Perfil ----------
    def _aba_automacoes(self) -> QWidget:
        w = QWidget()
        linha = QHBoxLayout(w)

        self.arvore = QTreeWidget()
        self.arvore.setHeaderHidden(True)
        self.arvore.setMaximumWidth(240)
        linha.addWidget(self.arvore)

        self.pilha = QStackedWidget()
        vazio = QLabel("Escolha uma automação ao lado.")
        vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pilha.addWidget(vazio)
        linha.addWidget(self.pilha, 1)

        geral = config.carregar_geral()
        perfis = config.carregar_perfis()
        categorias: dict[str, QTreeWidgetItem] = {}
        for pid, perfil in perfis.items():
            if not perfil.get("ativo", True):
                continue
            cat_nome = perfil.get("categoria", "Outros")
            if cat_nome not in categorias:
                item_cat = QTreeWidgetItem([cat_nome])
                item_cat.setFlags(item_cat.flags() & ~Qt.ItemFlag.ItemIsSelectable)
                self.arvore.addTopLevelItem(item_cat)
                categorias[cat_nome] = item_cat
            item_perfil = QTreeWidgetItem([perfil.get("nome", pid)])
            categorias[cat_nome].addChild(item_perfil)
            formulario = _FormularioPerfil(pid, perfil, geral, self._iniciar)
            indice = self.pilha.addWidget(formulario)
            item_perfil.setData(0, Qt.ItemDataRole.UserRole, indice)
        self.arvore.expandAll()
        self.arvore.itemClicked.connect(self._escolher_perfil)
        return w

    def _escolher_perfil(self, item: QTreeWidgetItem, _coluna: int) -> None:
        indice = item.data(0, Qt.ItemDataRole.UserRole)
        if indice is not None:
            self.pilha.setCurrentIndex(indice)

    def _iniciar(self, argv: list[str]) -> None:
        self.on_iniciar(argv)
        self.abas.setCurrentIndex(ABA_EXECUCAO)

    # ---------- Execução atual ----------
    def _aba_execucao(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        self.lbl_exec = QLabel("Nenhuma execução ainda.")
        l.addWidget(self.lbl_exec)
        self.tab_itens = QTableWidget(0, 4)
        self.tab_itens.setHorizontalHeaderLabels(["Escopo", "Status", "Tentativas", "Arquivos"])
        self.tab_itens.horizontalHeader().setStretchLastSection(True)
        l.addWidget(self.tab_itens)
        return w

    # ---------- Erros ----------
    def _aba_erros(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)
        self.tab_erros = QTableWidget(0, 5)
        self.tab_erros.setHorizontalHeaderLabels(["Execução", "Escopo", "Tentativa", "Erro", "Print"])
        self.tab_erros.horizontalHeader().setStretchLastSection(True)
        l.addWidget(self.tab_erros)
        return w

    def abrir_na_aba_erros(self) -> None:
        self.atualizar()
        self.abas.setCurrentIndex(ABA_ERROS)
        self.show(); self.raise_(); self.activateWindow()

    # ---------- Atualização periódica ----------
    def atualizar(self) -> None:
        exe = historico.ultima()
        if exe:
            self.lbl_exec.setText(
                f"{exe['id']} · {exe['perfil_id']} · {exe['modo_filiais']} · {exe['status']}"
                f"{'  ⏳ em andamento' if exe['status'] == 'em_andamento' else ''}")
            itens = exe.get("itens", [])
            self.tab_itens.setRowCount(len(itens))
            for r, it in enumerate(itens):
                self.tab_itens.setItem(r, 0, QTableWidgetItem(it["escopo"]))
                self.tab_itens.setItem(r, 1, QTableWidgetItem(it["status"]))
                self.tab_itens.setItem(r, 2, QTableWidgetItem(str(it.get("tentativas", 1))))
                self.tab_itens.setItem(r, 3, QTableWidgetItem(
                    ", ".join(Path(a).name for a in it.get("arquivos_finais", []))))
        erros = historico.erros_recentes()
        self.tab_erros.setRowCount(len(erros))
        for r, e in enumerate(erros):
            self.tab_erros.setItem(r, 0, QTableWidgetItem(e["execucao_id"]))
            self.tab_erros.setItem(r, 1, QTableWidgetItem(e["escopo"]))
            self.tab_erros.setItem(r, 2, QTableWidgetItem(str(e.get("tentativa", 1))))
            self.tab_erros.setItem(r, 3, QTableWidgetItem(e.get("mensagem", "")))
            self.tab_erros.setItem(r, 4, QTableWidgetItem(e.get("print", "")))
