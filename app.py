# Streamlit To-Do App with Nested Subtasks and Manual Ordering (Compatible with Streamlit Cloud)

import streamlit as st
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

def reorder_tasks():
    order = {}
    for t in st.session_state.tasks:
        order[t["id"]] = st.session_state.get(f"order_{t['id']}", 0)
    st.session_state.tasks.sort(key=lambda t: order.get(t["id"], 0))
    save_tasks(st.session_state.tasks)

def reorder_subtasks(task):
    order = {}
    for s in task["subtasks"]:
        order[s["id"]] = st.session_state.get(f"order_sub_{s['id']}", 0)
    task["subtasks"].sort(key=lambda s: order.get(s["id"], 0))

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

st.write("\n### Tasks")
for i, t in enumerate(st.session_state.tasks[:st.session_state.visible_count]):
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

        st.number_input("Order", min_value=0, max_value=100, value=i, key=f"order_{t['id']}", on_change=reorder_tasks)

        st.markdown("**Subtasks:**")
        for j, s in enumerate(t["subtasks"]):
            scol1, scol2 = st.columns([0.1, 0.9])
            with scol1:
                st.checkbox("", value=s["completed"], key=f"done_{s['id']}", on_change=toggle_complete, args=(t["id"], s["id"]))
            with scol2:
                new_subtitle = st.text_input("Subtask", value=s["title"], key=f"title_{s['id']}")
                if new_subtitle != s["title"]:
                    s["title"] = new_subtitle
                    save_tasks(st.session_state.tasks)
                st.number_input("Subtask Order", min_value=0, max_value=100, value=j, key=f"order_sub_{s['id']}")

        reorder_subtasks(t)

        if st.button(f"➕ Add Subtask to '{t['title']}'", key=f"addsub_{t['id']}"):
            add_subtask(t["id"])
            st.experimental_rerun()

if st.session_state.visible_count < len(st.session_state.tasks):
    if st.button("⬇️ Load More"):
        st.session_state.visible_count += 5
