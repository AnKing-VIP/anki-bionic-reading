from typing import List
from pathlib import Path
from aqt import gui_hooks, mw
from anki.models import TemplateDict

ADDON_ID = mw.addonManager.addonFromModule(__name__)
SCRIPT_HTML = '<script src="_bionic-reading.js"></script>'

def add_script_to_template(template: TemplateDict):
    changed = False
    for side in ["qfmt", "afmt"]:
        html: str = template[side]
        if SCRIPT_HTML in html:
            continue
        html += "\n"
        html += SCRIPT_HTML
        template[side] = html
        changed = True
    return changed

def add_script_to_note_types() -> None:
    note_types = mw.col.models.all()
    for note_type in note_types:
        changed = False
        templates = note_type["tmpls"]
        for template in templates:
            if add_script_to_template(template):
                changed = True
        if changed:
            print("added bionic reading script to note type")
            mw.col.models.update_dict(note_type)

def remove_script_from_note_types() -> None:
    note_types = mw.col.models.all()
    for note_type in note_types:
        templates = note_type["tmpls"]
        changed = False
        for template in templates:
            for side in ["qfmt", "afmt"]:
                html = template[side]
                html.replace(SCRIPT_HTML, "")
                changed = True
        if changed:
            print("removed bionic reading script from note type")
            mw.col.models.update_dict(note_type)

def add_script_to_media_folder() -> None:
    # TODO: Update file when _bionic-reading.js changes
    if not mw.col.media.have("_bionic-reading.js"):
        print("adding _bionic-reading.js to collection")
        mw.col.media.add_file(str(Path(__file__).parent / "_bionic-reading.js"))


def on_delete_addon(ids: List[str]) -> None:
    if ADDON_ID not in ids:
        return
    remove_script_from_note_types()

def on_anki_start() -> None:
    print("on_anki_start")
    add_script_to_media_folder()
    add_script_to_note_types()

gui_hooks.addons_dialog_will_delete_addons.append(on_delete_addon)
gui_hooks.main_window_did_init.append(on_anki_start)