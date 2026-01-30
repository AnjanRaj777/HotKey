
THEMES = {
    "Default Dark": """
        QMainWindow, QWidget { background-color: #1e1e1e; color: #d4d4d4; }
        QTableWidget { background-color: #1e1e1e; color: #d4d4d4; gridline-color: #333333; border: none; }
        QTableWidget::item:selected { background-color: #37373d; }
        QHeaderView::section { background-color: #252526; color: #d4d4d4; border: none; padding: 4px; }
        QPushButton { background-color: #0e639c; color: #ffffff; border: none; padding: 6px; border-radius: 2px; }
        QPushButton:hover { background-color: #1177bb; }
        QLineEdit, QComboBox { background-color: #3c3c3c; color: #cccccc; border: 1px solid #3c3c3c; padding: 4px; }
        QTabWidget::pane { border: 1px solid #252526; }
        QTabBar::tab { background-color: #2d2d2d; color: #969696; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #1e1e1e; color: #ffffff; border-top: 1px solid #007acc; }
    """,
    "Dark (VS Code)": """
        QMainWindow, QWidget { background-color: #2b2b2b; color: #ffffff; }
        QTableWidget { background-color: #3b3b3b; color: #ffffff; gridline-color: #555555; }
        QHeaderView::section { background-color: #444444; color: #ffffff; border: none; padding: 4px; }
        QPushButton { background-color: #0e639c; color: #ffffff; border: none; padding: 6px; border-radius: 3px; }
        QPushButton:hover { background-color: #1177bb; }
        QLineEdit, QComboBox { background-color: #3c3c3c; color: #cccccc; border: 1px solid #3c3c3c; padding: 4px; }
        QTabWidget::pane { border: 1px solid #444444; }
        QTabBar::tab { background-color: #2d2d2d; color: #888888; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #1e1e1e; color: #ffffff; border-top: 2px solid #007acc; }
    """,
    "Light (VS Code)": """
        QMainWindow, QWidget { background-color: #ffffff; color: #333333; }
        QTableWidget { background-color: #ffffff; color: #333333; gridline-color: #e5e5e5; }
        QHeaderView::section { background-color: #f3f3f3; color: #333333; border: none; padding: 4px; }
        QPushButton { background-color: #007acc; color: #ffffff; border: none; padding: 6px; border-radius: 3px; }
        QPushButton:hover { background-color: #0062a3; }
        QLineEdit, QComboBox { background-color: #ffffff; color: #333333; border: 1px solid #cecece; padding: 4px; }
        QTabWidget::pane { border: 1px solid #e5e5e5; }
        QTabBar::tab { background-color: #f3f3f3; color: #333333; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #ffffff; color: #333333; border-top: 2px solid #007acc; }
    """,
    "Monokai": """
        QMainWindow, QWidget { background-color: #272822; color: #f8f8f2; }
        QTableWidget { background-color: #1e1f1c; color: #f8f8f2; gridline-color: #49483e; alternate-background-color: #272822; }
        QHeaderView::section { background-color: #75715e; color: #f8f8f2; padding: 4px; border: none; }
        QPushButton { background-color: #f92672; color: #f8f8f2; border: none; padding: 6px; border-radius: 3px; }
        QPushButton:hover { background-color: #ff4081; }
        QLineEdit, QComboBox { background-color: #49483e; color: #f8f8f2; border: 1px solid #75715e; padding: 4px; }
        QTabWidget::pane { border: 1px solid #75715e; }
        QTabBar::tab { background-color: #3e3d32; color: #f8f8f2; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #272822; color: #f8f8f2; border-top: 2px solid #a6e22e; }
    """,
    "Solarized Dark": """
        QMainWindow, QWidget { background-color: #002b36; color: #839496; }
        QTableWidget { background-color: #073642; color: #93a1a1; gridline-color: #586e75; }
        QHeaderView::section { background-color: #073642; color: #93a1a1; padding: 4px; border: none; }
        QPushButton { background-color: #268bd2; color: #fdf6e3; border: none; padding: 6px; border-radius: 3px; }
        QPushButton:hover { background-color: #2aa198; }
        QLineEdit, QComboBox { background-color: #073642; color: #93a1a1; border: 1px solid #586e75; padding: 4px; }
        QTabWidget::pane { border: 1px solid #586e75; }
        QTabBar::tab { background-color: #002b36; color: #586e75; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #073642; color: #93a1a1; border-bottom: 2px solid #b58900; }
    """,
    "Dracula": """
        QMainWindow, QWidget { background-color: #282a36; color: #f8f8f2; }
        QTableWidget { background-color: #44475a; color: #f8f8f2; gridline-color: #6272a4; }
        QHeaderView::section { background-color: #44475a; color: #8be9fd; padding: 4px; border: none; }
        QPushButton { background-color: #bd93f9; color: #282a36; border: none; padding: 6px; border-radius: 3px; font-weight: bold; }
        QPushButton:hover { background-color: #ff79c6; }
        QLineEdit, QComboBox { background-color: #44475a; color: #f8f8f2; border: 1px solid #6272a4; padding: 4px; }
        QTabWidget::pane { border: 1px solid #6272a4; }
        QTabBar::tab { background-color: #21222c; color: #6272a4; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #282a36; color: #50fa7b; border-top: 2px solid #50fa7b; }
    """,
    "GitHub Dark": """
        QMainWindow, QWidget { background-color: #0d1117; color: #c9d1d9; }
        QTableWidget { background-color: #161b22; color: #c9d1d9; gridline-color: #30363d; }
        QHeaderView::section { background-color: #161b22; color: #8b949e; padding: 4px; border-bottom: 1px solid #30363d; }
        QPushButton { background-color: #238636; color: #ffffff; border: 1px solid rgba(240, 246, 252, 0.1); padding: 6px; border-radius: 6px; }
        QPushButton:hover { background-color: #2ea043; }
        QLineEdit, QComboBox { background-color: #0d1117; color: #c9d1d9; border: 1px solid #30363d; padding: 4px; }
        QTabWidget::pane { border: 1px solid #30363d; }
        QTabBar::tab { background-color: #090c10; color: #8b949e; padding: 8px 12px; }
        QTabBar::tab:selected { background-color: #0d1117; color: #c9d1d9; border-top: 2px solid #f78166; }
    """
}
