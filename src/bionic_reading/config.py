from aqt.qt import QListWidget, QListWidgetItem, Qt, QPushButton
from aqt import mw

from .ankiaddonconfig import ConfigManager, ConfigWindow
from .notetype import (
    get_note_types_have_scripts,
    add_script_to_note_type,
    add_script_to_all_note_types,
    remove_script_from_note_type,
    remove_script_from_all_note_types,
)

conf = ConfigManager()


def all_notetypes_are_checked(list_widget: QListWidget) -> bool:
    cnt = list_widget.count()
    for i in range(cnt):
        item = list_widget.item(i)
        if item.checkState() != Qt.CheckState.Checked:
            return False
    return True


def update_note_types_list(list_widget: QListWidget) -> None:
    list_widget.clear()
    note_types = get_note_types_have_scripts()
    for note_type in note_types:
        item = QListWidgetItem(note_type)
        item.setCheckState(note_types[note_type])
        list_widget.addItem(item)


def on_item_checked(item: QListWidgetItem) -> None:
    name = item.text()
    note_type = mw.col.models.get(mw.col.models.id_for_name(name))
    if item.checkState() == Qt.CheckState.Checked:
        add_script_to_note_type(note_type)
    elif item.checkState() == Qt.CheckState.Unchecked:
        remove_script_from_note_type(note_type)


def config_tab(window: ConfigWindow) -> None:
    tab = window.add_tab("General")
    tab.text("Choose note types that you want to use bionic reading on.")

    list_widget = QListWidget()
    update_note_types_list(list_widget)
    list_widget.itemChanged.connect(on_item_checked)
    window.widget_updates.append(lambda: update_note_types_list(list_widget))
    tab.addWidget(list_widget)

    btn_lay = tab.hlayout()
    button = QPushButton("Toggle All Notetypes")

    def on_click(_: bool) -> None:
        if all_notetypes_are_checked(list_widget):
            remove_script_from_all_note_types()
        else:
            add_script_to_all_note_types()
        window.update_widgets()

    button.clicked.connect(on_click)
    btn_lay.addWidget(button)
    btn_lay.stretch()


conf.use_custom_window()
conf.add_config_tab(config_tab)
