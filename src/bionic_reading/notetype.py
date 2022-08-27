from typing import List, Dict
from pathlib import Path
from aqt import  mw
import anki.models
from aqt.qt import Qt

SCRIPT_HTML = '<script src="_bionic-reading.js"></script>'

def get_note_types_have_scripts() -> Dict[str, Qt.CheckState]:
    note_types = mw.col.models.all()
    note_types_have_script: Dict[str, Qt.CheckState]  = {}
    for note_type in note_types:
        templates = note_type["tmpls"]
        has_script = 0
        for template in templates:
            for side in ["qfmt", "afmt"]:
                html: str = template[side] # type: ignore
                if SCRIPT_HTML in html:
                    has_script += 1

        value: Qt.CheckState
        if has_script == 2 * len(templates):
            value = Qt.CheckState.Checked
        elif has_script == 0:
            value = Qt.CheckState.Unchecked
        else:
            value = Qt.CheckState.PartiallyChecked
        note_types_have_script[note_type["name"]] = value
    return note_types_have_script


def add_script_to_note_type(note_type: "anki.models.NoteTypeDict") -> bool:
    changed = False
    for side in ["qfmt", "afmt"]:
        templates = note_type["tmpls"]
        for template in templates:
            html: str = template[side] # type: ignore
            if SCRIPT_HTML in html:
                continue
            html += "\n"
            html += SCRIPT_HTML
            template[side] = html
            changed = True
    return changed

def add_script_to_all_note_types() -> None:
    note_types = mw.col.models.all()
    for note_type in note_types:
        changed = add_script_to_note_type(note_type)
        if changed:
            print("added bionic reading script to note type")
            mw.col.models.update_dict(note_type)

def remove_script_from_note_type(note_type: "anki.models.NoteTypeDict") -> bool:
    templates = note_type["tmpls"]
    changed = False
    for template in templates:
        for side in ["qfmt", "afmt"]:
            html: str = template[side]
            template[side] = html.replace(SCRIPT_HTML, "")    
    mw.col.models.update_dict(note_type)
    return changed

def remove_script_from_all_note_types() -> None:
    note_types = mw.col.models.all()
    for note_type in note_types:
        remove_script_from_note_type(note_type)
    print("removed bionic reading script from all note types")

def add_or_replace_script_in_media() -> None:
    if mw.col.media.have("_bionic-reading.js"):
        mw.col.media.trash_files(["_bionic-reading.js"])
    print("adding _bionic-reading.js to collection")
    mw.col.media.add_file(str(Path(__file__).parent / "_bionic-reading.js"))
