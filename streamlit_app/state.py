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
    "quizzes": {},     # slug -> { quiz_id -> { selected, correct, total } }
    "notes": {},       # slug -> { heading_id -> text }
    "meta": {},        # slug -> { title, url, description }
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

def get_quiz_state(slug: str) -> Dict[str, Any]:
    data = get_progress()
    return data.setdefault("quizzes", {}).setdefault(slug, {})

def set_quiz_result(slug: str, quiz_id: str, selected: Any, correct: int, total: int):
    data = get_progress()
    q = data.setdefault("quizzes", {}).setdefault(slug, {})
    q[quiz_id] = {"selected": selected, "correct": int(correct), "total": int(total)}
    save_state(data)

def get_notes(slug: str) -> Dict[str, str]:
    data = get_progress()
    return data.setdefault("notes", {}).setdefault(slug, {})

def set_note(slug: str, heading_id: str, text: str):
    data = get_progress()
    n = data.setdefault("notes", {}).setdefault(slug, {})
    n[heading_id] = text
    save_state(data)

def get_meta(slug: str) -> Dict[str, Any]:
    data = get_progress()
    return data.setdefault("meta", {}).setdefault(slug, {})

def set_meta(slug: str, meta: Dict[str, Any]):
    data = get_progress()
    data.setdefault("meta", {})[slug] = meta
    save_state(data)

# Case Studies Management
def get_case_studies(slug: str = None) -> Dict[str, Any]:
    """
    Get all case studies or just those for a specific lesson
    """
    data = get_progress()
    case_studies = data.setdefault("case_studies", {})
    if slug is not None:
        return case_studies.setdefault(slug, {})
    return case_studies

def save_case_study(slug: str, case_study_id: str, case_study_data: Dict[str, Any]):
    """
    Save a case study for a specific lesson
    """
    data = get_progress()
    cs = data.setdefault("case_studies", {}).setdefault(slug, {})
    cs[case_study_id] = case_study_data
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
