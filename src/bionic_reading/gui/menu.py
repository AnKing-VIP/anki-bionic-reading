from aqt.qt import QAction

from .anking_menu import get_anking_menu
from ..config import conf

def setup_menu() -> None:
    menu = get_anking_menu()
    a = QAction("Bionic Reading", menu)
    menu.addAction(a)
    a.triggered.connect(conf.open_config)
