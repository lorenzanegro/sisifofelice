# Streamlit To-Do App with Nested Subtasks and Drag-and-Drop Sorting
pip install -r requirements.txt
import streamlit as st
from streamlit_sortables import sortables
import json
import os
from datetime import date

DATA_FILE = "tasks.json"

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    else:
        return [
            {
                "id": 1,
                "title": "Plan weekly schedule",
                "completed": False,
                "dueDate": "2025-06-30",
                "subtasks": [
                    {"id": 11, "title": "Work blocks", "completed": True},
                    {"id": 12, "title": "Personal goals", "completed": False},
                ],
            }
        ]

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "visible_count" not in st.session_state:
    st.session_state.visible_count = 5

def toggle_complete(task_id, subtask_id=None):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            if subtask_id:
                for s in t["subtasks"]:
                    if s["id"] == subtask_id:
                        s["completed"] = not s["completed"]
                        break
            else:
                t["completed"] = not t["completed"]
            break
    save_tasks(st.session_state.tasks)

def reorder_tasks(new_titles):
    id_map = {t["title"]: t for t in st.session_state.tasks}
    st.session_state.tasks = [id_map[title] for title in new_titles if title in id_map]
    save_tasks(st.session_state.tasks)

def reorder_subtasks(task_id, new_titles):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            id_map = {s["title"]: s for s in t["subtasks"]}
            t["subtasks"] = [id_map[title] for title in new_titles if title in id_map]
            break
    save_tasks(st.session_state.tasks)

def add_task():
    new_id = max([t["id"] for t in st.session_state.tasks] + [0]) + 1
    new_task = {
        "id": new_id,
        "title": "New Task",
        "completed": False,
        "dueDate": "",
        "subtasks": []
    }
    st.session_state.tasks.insert(0, new_task)
    save_tasks(st.session_state.tasks)

def add_subtask(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            new_id = max([s["id"] for s in t["subtasks"]] + [task_id * 10]) + 1
            t["subtasks"].append({"id": new_id, "title": "New Subtask", "completed": False})
            break
    save_tasks(st.session_state.tasks)

st.title("📋 Streamlit To-Do List with Subtasks")

if st.button("➕ Add Task"):
    add_task()

# Drag-and-drop sorting of tasks
task_titles = [t["title"] for t in st.session_state.tasks[:st.session_state.visible_count]]
new_order = sortables(task_titles, direction="vertical", key="task_sort")
if new_order != task_titles:
    reorder_tasks(new_order)

for t in st.session_state.tasks[:st.session_state.visible_count]:
    col1, col2 = st.columns([0.05, 0.95])
    with col1:
        st.checkbox("", value=t["completed"], key=f"done_{t['id']}", on_change=toggle_complete, args=(t["id"],))
    with col2:
        new_title = st.text_input("Task", value=t["title"], key=f"title_{t['id']}")
        if new_title != t["title"]:
            t["title"] = new_title
            save_tasks(st.session_state.tasks)

        due = date.fromisoformat(t["dueDate"]) if t["dueDate"] else date.today()
        new_due = st.date_input("Due Date", value=due, key=f"due_{t['id']}")
        t["dueDate"] = new_due.isoformat()
        save_tasks(st.session_state.tasks)

        st.markdown("**Subtasks:**")
        sub_titles = [s["title"] for s in t["subtasks"]]
        new_sub_order = sortables(sub_titles, direction="vertical", key=f"sub_{t['id']}")
        if new_sub_order != sub_titles:
            reorder_subtasks(t["id"], new_sub_order)

        for s in t["subtasks"]:
            scol1, scol2 = st.columns([0.1, 0.9])
            with scol1:
                st.checkbox("", value=s["completed"], key=f"done_{s['id']}", on_change=toggle_complete, args=(t["id"], s["id"]))
            with scol2:
                new_subtitle = st.text_input("Subtask", value=s["title"], key=f"title_{s['id']}")
                if new_subtitle != s["title"]:
                    s["title"] = new_subtitle
                    save_tasks(st.session_state.tasks)

        if st.button(f"➕ Add Subtask to '{t['title']}'", key=f"addsub_{t['id']}"):
            add_subtask(t["id"])
            st.experimental_rerun()

if st.session_state.visible_count < len(st.session_state.tasks):
    if st.button("⬇️ Load More"):
        st.session_state.visible_count += 5
