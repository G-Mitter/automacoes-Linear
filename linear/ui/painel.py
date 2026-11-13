"""Painel (UI1): escolher e iniciar um perfil, acompanhar a execução atual, listar erros."""
from __future__ import annotations

from datetime import date, timedelta
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QComboBox, QDateEdit, QHBoxLayout, QLabel, QLineEdit,
                                QMessageBox, QPushButton, QTabWidget, QTableWidget,
                                QTableWidgetItem, QVBoxLayout, QWidget)

from .. import config, historico

CORES_STATUS = {
    "ok": "#1a7f37", "sem_dados": "#9a6700", "falha": "#cf222e",
    "pendente": "#57606a", "em_andamento": "#0969da", None: "#57606a",
}


class Painel(QWidget):
    def __init__(self, on_iniciar) -> None:
        super().__init__()
        self.on_iniciar = on_iniciar
        self.setWindowTitle("Automações Linear")
        self.resize(640, 440)

        abas = QTabWidget()
        abas.addTab(self._aba_iniciar(), "Iniciar")
        abas.addTab(self._aba_execucao(), "Execução atual")
        abas.addTab(self._aba_erros(), "Erros")
        layout = QVBoxLayout(self)
        layout.addWidget(abas)
        self.abas = abas
        self.atualizar()

    # ---------- Iniciar ----------
    def _aba_iniciar(self) -> QWidget:
        w = QWidget()
        l = QVBoxLayout(w)

        geral = config.carregar_geral()
        perfis = config.carregar_perfis()

        linha1 = QHBoxLayout()
        self.cb_perfil = QComboBox()
        for pid, p in perfis.items():
            if p.get("ativo", True):
                self.cb_perfil.addItem(p.get("nome", pid), pid)
        linha1.addWidget(QLabel("Perfil:")); linha1.addWidget(self.cb_perfil)
        l.addLayout(linha1)

        linha2 = QHBoxLayout()
        self.ed_filiais = QLineEdit("todas")
        self.ed_filiais.setToolTip("Números e/ou grupos separados por vírgula, ou 'todas'. "
                                    f"Grupos: {', '.join((geral.get('grupos') or {}))}")
        linha2.addWidget(QLabel("Filiais:")); linha2.addWidget(self.ed_filiais)
        l.addLayout(linha2)

        linha3 = QHBoxLayout()
        self.cb_modo = QComboBox(); self.cb_modo.addItems(["individual", "por_grupo", "consolidado"])
        self.cb_formato = QComboBox(); self.cb_formato.addItems(["xlsx", "pdf", "ambos"])
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

        self.btn_iniciar = QPushButton("Iniciar")
        self.btn_iniciar.clicked.connect(self._iniciar)
        l.addWidget(self.btn_iniciar)
        self.lbl_status_inicio = QLabel("")
        l.addWidget(self.lbl_status_inicio)
        l.addStretch(1)
        return w

    def _iniciar(self) -> None:
        if historico.em_andamento():
            QMessageBox.warning(self, "Já em execução",
                                 "Já existe uma execução em andamento. Espere terminar ou cancele pelo terminal.")
            return
        perfil = self.cb_perfil.currentData()
        argv = ["run", perfil,
                "--filiais", self.ed_filiais.text().strip() or "todas",
                "--modo", self.cb_modo.currentText(),
                "--formato", self.cb_formato.currentText(),
                "--de", self.dt_de.date().toString("yyyy-MM-dd"),
                "--ate", self.dt_ate.date().toString("yyyy-MM-dd")]
        self.lbl_status_inicio.setText("Iniciando…")
        self.on_iniciar(argv)
        self.abas.setCurrentIndex(1)

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
                cel = QTableWidgetItem(it["status"])
                cel.setForeground(Qt.GlobalColor.white)
                self.tab_itens.setItem(r, 1, cel)
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
