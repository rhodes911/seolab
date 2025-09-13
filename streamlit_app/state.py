from __future__ import annotations
import os, json
from typing import Dict, Any, List
import streamlit as st

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "."))
STATE_FILE = os.path.join(BASE_DIR, "progress.json")

DEFAULT_STATE = {
    "version": 1,
    "completed": {},   # slug -> bool
    "checklist": {},   # slug -> { item -> bool }
}

def _ensure_file():
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    if not os.path.exists(STATE_FILE):
        with open(STATE_FILE, 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_STATE, f, indent=2)

def load_state() -> Dict[str, Any]:
    _ensure_file()
    try:
        with open(STATE_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return DEFAULT_STATE.copy()

def save_state(data: Dict[str, Any]):
    with open(STATE_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

# Convenience wrappers around st.session_state
KEY = "__progress__"

def get_progress() -> Dict[str, Any]:
    if KEY not in st.session_state:
        st.session_state[KEY] = load_state()
    return st.session_state[KEY]

def set_completed(slug: str, done: bool):
    data = get_progress()
    data.setdefault("completed", {})[slug] = done
    save_state(data)

def set_checklist(slug: str, items: List[str], values: List[bool]):
    data = get_progress()
    data.setdefault("checklist", {})[slug] = {item: bool(val) for item, val in zip(items, values)}
    all_checked = all(values) if items else False
    data.setdefault("completed", {})[slug] = all_checked
    save_state(data)

def export_json() -> str:
    return json.dumps(get_progress(), indent=2)

def import_json(text: str) -> bool:
    try:
        data = json.loads(text)
        st.session_state[KEY] = data
        save_state(data)
        return True
    except Exception:
        return False

def reset_all():
    st.session_state[KEY] = DEFAULT_STATE.copy()
    save_state(st.session_state[KEY])
