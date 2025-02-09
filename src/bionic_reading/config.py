from concurrent.futures import Future
from typing import List, Tuple
from anki.models import NotetypeDict
from aqt import mw
from aqt.qt import QListWidget, QListWidgetItem, QPushButton, Qt

from .ankiaddonconfig import ConfigManager, ConfigWindow
from .notetype import (
    add_script_to_note_type,
    get_note_types_have_scripts,
    remove_script_from_note_type,
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

def on_config_save(notetype_listwidget: QListWidget) -> None:
    notetype_names_states: List[Tuple[str, bool]] = []
    for i in range(notetype_listwidget.count()):
        item = notetype_listwidget.item(i)
        notetype_names_states.append(
            (item.text(), item.checkState() == Qt.CheckState.Checked)
        )

    def task() -> None:
        updated_notetypes: List[NotetypeDict] = []
        for name, checked in notetype_names_states:
            notetype = mw.col.models.by_name(name)
            changed = False
            if checked:
                changed = add_script_to_note_type(notetype)
            else:
                changed = remove_script_from_note_type(notetype)
            if changed:
                updated_notetypes.append(notetype)
        for notetype in updated_notetypes:
            mw.col.models.update_dict(notetype)

    def on_done(future: Future) -> None:
        future.result()

    mw.taskman.with_progress(
        task=task, on_done=on_done, parent=mw, label="Updating note types"
    )


def config_tab(window: ConfigWindow) -> None:
    tab = window.add_tab("General")
    tab.text("Choose note types that you want to use bionic reading on.")

    list_widget = QListWidget()
    update_note_types_list(list_widget)
    window.widget_updates.append(lambda: update_note_types_list(list_widget))
    tab.addWidget(list_widget)

    btn_lay = tab.hlayout()
    toggle_all_button = QPushButton("Toggle All Notetypes")

    def on_toggle_all(_: bool) -> None:
        all_checked = True
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            if item.checkState() != Qt.CheckState.Checked:
                all_checked = False
                break
        for i in range(list_widget.count()):
            item = list_widget.item(i)
            item.setCheckState(
                Qt.CheckState.Checked if not all_checked else Qt.CheckState.Unchecked
            )

    toggle_all_button.clicked.connect(on_toggle_all)
    btn_lay.addWidget(toggle_all_button)
    btn_lay.stretch()

    window.execute_on_save(lambda: on_config_save(list_widget))


conf.use_custom_window()
conf.add_config_tab(config_tab)
