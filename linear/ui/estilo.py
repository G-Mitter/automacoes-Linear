"""Tokens visuais do app, tirados do Design §2/§6/§7 (tema escuro, já que fica por cima do ERP)."""
from __future__ import annotations

COR = {
    "primaria": "#C8102E",
    "secundaria": "#1F2937",
    "fundo": "#111318",
    "superficie": "#1A1D24",
    "borda": "#2A2F3A",
    "texto": "#E5E7EB",
    "texto_secundario": "#9CA3AF",
    "sucesso": "#15803D",
    "erro": "#B91C1C",
    "aviso": "#B45309",
    "info": "#1D4ED8",
}

CORES_STATUS = {
    "ok": COR["sucesso"], "sem_dados": COR["aviso"], "falha": COR["erro"],
    "pendente": COR["texto_secundario"], "em_andamento": COR["info"], None: COR["texto_secundario"],
}

# Ícone + texto junto da cor (Design §2: "o status nunca é indicado só pela cor")
ROTULO_STATUS = {
    "ok": "✅ ok", "sem_dados": "⚠️ sem dados", "falha": "❌ falha",
    "pendente": "⏸ pendente", "em_andamento": "⏳ em andamento",
}

QSS = f"""
* {{
    font-family: "Inter", "Segoe UI", sans-serif;
    font-size: 14px;
    color: {COR["texto"]};
}}
QWidget {{ background-color: {COR["fundo"]}; }}
QLabel[papel="titulo"] {{ font-size: 18px; font-weight: 600; }}
QLabel[papel="secundario"] {{ color: {COR["texto_secundario"]}; font-size: 12px; }}

QTabWidget::pane {{ border: 1px solid {COR["borda"]}; border-radius: 8px; top: -1px; }}
QTabBar::tab {{
    background: transparent; color: {COR["texto_secundario"]};
    padding: 8px 16px; margin-right: 4px; border-top-left-radius: 6px; border-top-right-radius: 6px;
}}
QTabBar::tab:selected {{ color: {COR["texto"]}; background: {COR["superficie"]}; font-weight: 600; }}
QTabBar::tab:hover:!selected {{ color: {COR["texto"]}; }}

QPushButton {{
    background: {COR["primaria"]}; color: white; border: none;
    border-radius: 6px; padding: 8px 16px; font-weight: 600; min-height: 24px;
}}
QPushButton:hover {{ background: #AD0E28; }}
QPushButton:disabled {{ background: {COR["primaria"]}; opacity: 0.4; }}

QLineEdit, QComboBox, QDateEdit {{
    background: {COR["superficie"]}; border: 1px solid {COR["borda"]};
    border-radius: 8px; padding: 6px 8px; min-height: 22px;
}}
QLineEdit:focus, QComboBox:focus, QDateEdit:focus {{ border-color: {COR["primaria"]}; }}

QTreeWidget, QTableWidget {{
    background: {COR["superficie"]}; border: 1px solid {COR["borda"]}; border-radius: 8px;
    alternate-background-color: #20242c; gridline-color: {COR["borda"]};
}}
QTreeWidget::item, QTableWidget::item {{ padding: 6px; }}
QTreeWidget::item:selected, QTableWidget::item:selected {{
    background: {COR["primaria"]}; color: white;
}}
QHeaderView::section {{
    background: {COR["secundaria"]}; color: {COR["texto_secundario"]};
    border: none; padding: 6px; font-weight: 600;
}}

QToolTip {{
    background: {COR["secundaria"]}; color: {COR["texto"]};
    border: 1px solid {COR["borda"]}; padding: 4px 8px; border-radius: 4px;
}}
"""
