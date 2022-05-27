from typing import List
from pathlib import Path
from aqt import gui_hooks, mw

ADDON_ID = mw.addonManager.addonFromModule(__name__)


def add_script_to_note_types():
    pass

def add_script_to_media_folder():
    # TODO: Update file when _bionic-reading.js changes
    if not mw.col.media.have("_bionic-reading.js"):
        mw.col.media.add_file(str(Path(__file__).parent / "_bionic-reading.js"))


def on_delete_addon(ids: List[str]):
    if ADDON_ID not in ids:
        return
    # remove _bionic-reading.js from media folder,
    # remove <script> from note typess

gui_hooks.addons_dialog_will_delete_addons.append(on_delete_addon)
