"""UI1: app sempre ligado — ícone na bandeja + bolinha flutuante + painel.

Roda em paralelo ao robô, sem mudar nada nele: só lê execucoes/*.json e, para
iniciar, chama o mesmo `python -m linear run ...` como processo separado.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

from PySide6.QtCore import QPoint, Qt, QTimer
from PySide6.QtGui import QAction, QColor, QGuiApplication, QIcon, QPainter, QPixmap
from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon, QWidget

from .. import historico
from .painel import CORES_STATUS, Painel

RAIZ = Path(__file__).resolve().parent.parent.parent
DIAMETRO = 48
MARGEM = 16
SEGUNDOS_MOSTRANDO_FIM = 20   # depois de terminar, a bolinha fica visível mais um tempo


def _bolinha(cor: str, diametro: int = DIAMETRO) -> QPixmap:
    pix = QPixmap(diametro, diametro)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor(cor))
    p.setPen(QColor("#ffffff"))
    p.drawEllipse(1, 1, diametro - 2, diametro - 2)
    p.end()
    return pix


class Bolinha(QWidget):
    """Círculo sem moldura, translúcido, sempre no topo, no canto superior direito."""

    def __init__(self, ao_clicar) -> None:
        super().__init__()
        self.ao_clicar = ao_clicar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint
                             | Qt.WindowType.Tool)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setFixedSize(DIAMETRO, DIAMETRO)
        tela = QGuiApplication.primaryScreen().availableGeometry()
        self.move(tela.right() - DIAMETRO - MARGEM, tela.top() + MARGEM)
        self._cor_atual = "#57606a"

    def pintar(self, cor: str) -> None:
        self._cor_atual = cor
        self.setPixmap_ = None  # placeholder, sem uso
        self.update()

    def paintEvent(self, _evento) -> None:  # noqa: N802 (nome do Qt)
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor(self._cor_atual))
        p.setPen(QColor("#ffffff"))
        p.drawEllipse(1, 1, DIAMETRO - 3, DIAMETRO - 3)

    def mousePressEvent(self, _evento) -> None:  # noqa: N802
        self.ao_clicar()


class App:
    def __init__(self) -> None:
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)

        self.painel = Painel(on_iniciar=self._iniciar_execucao)
        self.bolinha = Bolinha(ao_clicar=self._abrir_painel)

        self.tray = QSystemTrayIcon(QIcon(_bolinha("#57606a", 22)))
        self.tray.setToolTip("Automações Linear")
        menu = QMenu()
        acao_abrir = QAction("Abrir painel"); acao_abrir.triggered.connect(self._abrir_painel)
        acao_sair = QAction("Sair"); acao_sair.triggered.connect(self.app.quit)
        menu.addAction(acao_abrir); menu.addSeparator(); menu.addAction(acao_sair)
        self.tray.setContextMenu(menu)
        self.tray.activated.connect(lambda motivo: self._abrir_painel()
                                     if motivo == QSystemTrayIcon.ActivationReason.Trigger else None)
        self.tray.show()

        self._ultimo_status_terminado: str | None = None
        self._escondendo_em: int | None = None
        self.relogio = QTimer()
        self.relogio.setInterval(1500)
        self.relogio.timeout.connect(self._tick)
        self.relogio.start()
        self._tick()

    def _abrir_painel(self) -> None:
        self.painel.atualizar()
        self.painel.show()
        self.painel.raise_()
        self.painel.activateWindow()

    def _iniciar_execucao(self, argv: list[str]) -> None:
        import subprocess
        ambiente = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}
        subprocess.Popen([sys.executable, "-m", "linear", *argv], cwd=str(RAIZ), env=ambiente,
                          creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0)

    def _tick(self) -> None:
        exe = historico.ultima()
        if self.painel.isVisible():
            self.painel.atualizar()
        if not exe:
            self.bolinha.hide()
            return
        status = exe.get("status")
        if status == "em_andamento":
            self.bolinha.pintar(CORES_STATUS["em_andamento"])
            self.bolinha.show()
            self._escondendo_em = None
        else:
            cor = CORES_STATUS["ok"] if status == "concluida" else CORES_STATUS["falha"]
            self.bolinha.pintar(cor)
            self.bolinha.show()
            if self._escondendo_em is None:
                self._escondendo_em = SEGUNDOS_MOSTRANDO_FIM
            else:
                self._escondendo_em -= self.relogio.interval() / 1000
                if self._escondendo_em <= 0:
                    self.bolinha.hide()

    def executar(self) -> int:
        return self.app.exec()


def main() -> int:
    return App().executar()


if __name__ == "__main__":
    sys.exit(main())
