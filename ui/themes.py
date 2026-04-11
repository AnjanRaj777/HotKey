
# Glassmorphism base styles shared across all frosted themes
_GLASS_BASE = """
    /* ===== WINDOW & WIDGET BASE ===== */
    QMainWindow {{
        background: transparent;
    }}
    QWidget {{
        background: transparent;
        color: #f0f0f0;
        font-family: 'Segoe UI', 'Arial', sans-serif;
    }}

    /* ===== LABELS ===== */
    QLabel {{
        background: transparent;
        color: #e8e8e8;
        font-size: 13px;
    }}

    /* ===== INPUTS ===== */
    QLineEdit, QComboBox, QSpinBox {{
        background-color: rgba(255, 255, 255, 0.08);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.18);
        border-radius: 10px;
        padding: 8px 12px;
        font-size: 13px;
        selection-background-color: {accent_transparent};
    }}
    QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
        border: 1px solid {accent};
    }}
    QLineEdit::placeholder {{
        color: rgba(255, 255, 255, 0.35);
    }}
    QComboBox::drop-down {{
        border: none;
        width: 24px;
        border-top-right-radius: 10px;
        border-bottom-right-radius: 10px;
    }}
    QComboBox::down-arrow {{
        image: none;
        border-left: 4px solid transparent;
        border-right: 4px solid transparent;
        border-top: 5px solid rgba(255, 255, 255, 0.5);
        margin-right: 8px;
    }}
    QComboBox QAbstractItemView {{
        background-color: rgba(30, 30, 30, 0.95);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 8px;
        selection-background-color: {accent_transparent};
        padding: 4px;
    }}

    /* ===== BUTTONS ===== */
    QPushButton {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {accent_dark}, stop:1 {accent});
        color: #ffffff;
        border: none;
        border-radius: 10px;
        padding: 8px 18px;
        font-size: 13px;
        font-weight: 600;
    }}
    QPushButton:hover {{
        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
            stop:0 {accent}, stop:1 {accent_light});
    }}
    QPushButton:pressed {{
        background: {accent_dark};
    }}
    QPushButton:disabled {{
        background: rgba(255, 255, 255, 0.08);
        color: rgba(255, 255, 255, 0.3);
    }}

    /* ===== CHECKBOXES ===== */
    QCheckBox {{
        color: #e0e0e0;
        spacing: 8px;
        font-size: 13px;
    }}
    QCheckBox::indicator {{
        width: 18px;
        height: 18px;
        border-radius: 4px;
        border: 1px solid rgba(255, 255, 255, 0.25);
        background-color: rgba(255, 255, 255, 0.06);
    }}
    QCheckBox::indicator:checked {{
        background-color: {accent};
        border: 1px solid {accent};
    }}
    QCheckBox::indicator:hover {{
        border: 1px solid {accent};
    }}

    /* ===== TABS ===== */
    QTabWidget::pane {{
        border: none;
        background: transparent;
    }}
    QTabWidget::right-corner {{
        right: -8px;
    }}
    QTabBar {{
        background: transparent;
        margin-left: 9px;
    }}
    QTabBar::tab {{
        background: transparent;
        color: rgba(255, 255, 255, 0.5);
        border: none;
        border-bottom: 2px solid transparent;
        padding: 10px 18px;
        margin-right: 2px;
        font-size: 13px;
        border-top-left-radius: 8px;
        border-top-right-radius: 8px;
    }}
    QTabBar::tab:selected {{
        background: rgba(255, 255, 255, 0.05); /* very subtle highlight */
        color: #ffffff;
        border-bottom: 2px solid {accent};
    }}
    QTabBar::tab:hover:!selected {{
        background: rgba(255, 255, 255, 0.08);
        color: #d0d0d0;
    }}

    /* ===== TABLES ===== */
    QTableWidget {{
        background: transparent; /* fully transparent so backdrop blur shows through */
        alternate-background-color: rgba(255, 255, 255, 0.03);
        color: #e0e0e0;
        gridline-color: rgba(255, 255, 255, 0.08);
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 10px;
        selection-background-color: {accent_transparent};
        selection-color: #ffffff;
    }}
    QTableWidget::item {{
        padding: 6px;
    }}
    QTableWidget::item:selected {{
        background-color: {accent_transparent};
    }}
    QHeaderView {{
        background: transparent;
    }}
    QHeaderView::section {{
        background-color: rgba(255, 255, 255, 0.06);
        color: rgba(255, 255, 255, 0.7);
        border: none;
        border-bottom: 1px solid rgba(255, 255, 255, 0.10);
        padding: 8px;
        font-size: 12px;
        font-weight: 600;
    }}
    QTableCornerButton::section {{
        background: rgba(255, 255, 255, 0.04);
        border: none;
    }}

    /* ===== LIST WIDGET ===== */
    QListWidget {{
        background: transparent;
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.10);
        border-radius: 10px;
        padding: 4px;
    }}
    QListWidget::item {{
        padding: 8px;
        border-radius: 6px;
    }}
    QListWidget::item:selected {{
        background-color: {accent_transparent};
    }}
    QListWidget::item:hover:!selected {{
        background-color: rgba(255, 255, 255, 0.06);
    }}

    /* ===== SLIDERS ===== */
    QSlider::groove:horizontal {{
        height: 6px;
        background: rgba(255, 255, 255, 0.12);
        border-radius: 3px;
    }}
    QSlider::handle:horizontal {{
        background: {accent};
        width: 16px;
        height: 16px;
        margin: -5px 0;
        border-radius: 8px;
    }}
    QSlider::sub-page:horizontal {{
        background: {accent};
        border-radius: 3px;
    }}

    /* ===== SCROLLBARS ===== */
    QScrollBar:vertical {{
        background: transparent;
        width: 8px;
        margin: 0;
    }}
    QScrollBar::handle:vertical {{
        background: rgba(255, 255, 255, 0.2);
        min-height: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:vertical:hover {{
        background: rgba(255, 255, 255, 0.35);
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0;
    }}
    QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {{
        background: transparent;
    }}
    QScrollBar:horizontal {{
        background: transparent;
        height: 8px;
        margin: 0;
    }}
    QScrollBar::handle:horizontal {{
        background: rgba(255, 255, 255, 0.2);
        min-width: 30px;
        border-radius: 4px;
    }}
    QScrollBar::handle:horizontal:hover {{
        background: rgba(255, 255, 255, 0.35);
    }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
        width: 0;
    }}
    QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {{
        background: transparent;
    }}

    /* ===== DIALOGS ===== */
    QDialog {{
        background: transparent;
    }}

    /* ===== MESSAGE BOX ===== */
    QMessageBox {{
        background-color: rgba(25, 25, 25, 0.95);
    }}
    QMessageBox QLabel {{
        color: #e0e0e0;
    }}
    QMessageBox QPushButton {{
        min-width: 80px;
    }}

    /* ===== TOOLTIPS ===== */
    QToolTip {{
        background-color: rgba(30, 30, 30, 0.95);
        color: #e0e0e0;
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 6px;
        padding: 6px 10px;
        font-size: 12px;
    }}

    /* ===== DIALOG BUTTON BOX ===== */
    QDialogButtonBox QPushButton {{
        min-width: 80px;
    }}

    /* ===== FILE DIALOG (limited styling) ===== */
    QFileDialog {{
        background-color: rgba(25, 25, 25, 0.95);
    }}
"""

def _build_theme(accent, accent_dark, accent_light, accent_transparent):
    """Build a glassmorphism theme with a given accent color."""
    return _GLASS_BASE.format(
        accent=accent,
        accent_dark=accent_dark,
        accent_light=accent_light,
        accent_transparent=accent_transparent
    )

THEMES = {
    "Frost Glass": _build_theme(
        accent="#2ecc71",
        accent_dark="#1a9c54",
        accent_light="#55efc4",
        accent_transparent="rgba(46, 204, 113, 0.3)"
    ),
    "Frost Glass Blue": _build_theme(
        accent="#3498db",
        accent_dark="#2176ae",
        accent_light="#74b9ff",
        accent_transparent="rgba(52, 152, 219, 0.3)"
    ),
    "Frost Glass Purple": _build_theme(
        accent="#9b59b6",
        accent_dark="#7d3c98",
        accent_light="#c39bd3",
        accent_transparent="rgba(155, 89, 182, 0.3)"
    ),
}
