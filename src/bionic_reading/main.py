from typing import List, Any
from aqt import gui_hooks, mw
from aqt.utils import askUser, showText

from .gui.menu import setup_menu
from .firstrun import check_update
from .notetype import get_note_types_have_scripts, remove_script_from_all_note_types

ADDON_ID = mw.addonManager.addonFromModule(__name__)


def on_delete_addon(dial: Any, ids: List[str]) -> None:
    if ADDON_ID not in ids:
        return
    try:
        note_types_have_scripts = get_note_types_have_scripts()
        has_script = False
        for note_type in note_types_have_scripts:
            if note_types_have_scripts[note_type]:
                has_script = True
                break
        if has_script:
            remove = askUser(
                "Remove Bionic Reading scripts from all note types?",
                title="Bionic Reading",
            )
            if remove:
                remove_script_from_all_note_types()
    except Exception as e:
        showText(
            "Error occured while deleting add-on Bionic Reading.\n"
            "The add-on has been deleted, you may need to manually remove bionic reading scripts from note types.\n",
            title="Error",
        )
        print(e)


def on_anki_start(_: Any) -> None:
    check_update()


gui_hooks.addons_dialog_will_delete_addons.append(on_delete_addon)
gui_hooks.collection_did_load.append(on_anki_start)
setup_menu()
