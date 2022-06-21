from typing import List, Any
from aqt import gui_hooks, mw

from .notetype import remove_script_from_note_types, add_script_to_media_folder, add_script_to_all_note_types

ADDON_ID = mw.addonManager.addonFromModule(__name__)

def on_delete_addon(dial: Any, ids: List[str]) -> None:
    if ADDON_ID not in ids:
        return
    remove_script_from_note_types()

def on_anki_start(_: Any) -> None:
    add_script_to_media_folder()
    # add_script_to_all_note_types()

gui_hooks.addons_dialog_will_delete_addons.append(on_delete_addon)
gui_hooks.collection_did_load.append(on_anki_start)