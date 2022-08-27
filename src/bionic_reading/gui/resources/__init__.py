from pathlib import Path
from aqt.qt import QDir


def initialize_qt_resources():
    QDir.addSearchPath("AnKing", str(Path(__file__).parent / "AnKing"))


initialize_qt_resources()
