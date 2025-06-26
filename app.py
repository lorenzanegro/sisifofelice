import streamlit as st
from streamlit_sortables import sortables
import json
import os
from datetime import date

# Helper: Load/save tasks data to file
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
                "expanded": True,
            }
        ]

def save_tasks(tasks):
    with open(DATA_FILE, "w") as f:
        json.dump(tasks, f, indent=2)

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = load_tasks()
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "visible_count" not in st.session_state:
    st.session_state.visible_count = 5

def toggle_complete(task_id, subtask_id=None):
    tasks = st.session_state.tasks
    for t in tasks:
        if t["id"] == task_id:
            if subtask_id:
                for s in t["subtasks"]:
                    if s["id"] == subtask_id:
                        s["completed"] = not s["completed"]
                        break
            else:
                t["completed"] = not t["completed"]
            break
    st.session_state.tasks = tasks
    save_tasks(tasks)

def toggle_expand(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["expanded"] = not t.get("expanded", True)
            break
    save_tasks(st.session_state.tasks)

def add_task():
    new_id = max(t["id"] for t in st.session_state.tasks) + 1 if st.session_state.tasks else 1
    new_task = {
        "id": new_id,
        "title": "New Task",
        "completed": False,
        "dueDate": "",
        "subtasks": [],
        "expanded": True,
    }
    st.session_state.tasks.insert(0, new_task)
    save_tasks(st.session_state.tasks)

def add_subtask(task_id):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            new_sub_id = max((s["id"] for s in t["subtasks"]), default=task_id * 10) + 1
            t["subtasks"].append({"id": new_sub_id, "title": "New Subtask", "completed": False})
            t["expanded"] = True
            break
    save_tasks(st.session_state.tasks)

def edit_task_title(task_id, new_title):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["title"] = new_title
            break
    save_tasks(st.session_state.tasks)

def edit_subtask_title(task_id, subtask_id, new_title):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            for s in t["subtasks"]:
                if s["id"] == subtask_id:
                    s["title"] = new_title
                    break
            break
    save_tasks(st.session_state.tasks)

def edit_due_date(task_id, new_date):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            t["dueDate"] = new_date.isoformat() if new_date else ""
            break
    save_tasks(st.session_state.tasks)

def reorder_tasks(new_order_ids):
    id_to_task = {t["id"]: t for t in st.session_state.tasks}
    st.session_state.tasks = [id_to_task[i] for i in new_order_ids]
    save_tasks(st.session_state.tasks)

def reorder_subtasks(task_id, new_order_ids):
    for t in st.session_state.tasks:
        if t["id"] == task_id:
            id_to_subtask = {s["id"]: s for s in t["subtasks"]}
            t["subtasks"] = [id_to_subtask[i] for i in new_order_ids]
            break
    save_tasks(st.session_state.tasks)

# Dark mode toggle (simple)
st.sidebar.title("Settings")
if st.sidebar.checkbox("Dark Mode", value=st.session_state.dark_mode):
    st.session_state.dark_mode = True
    st.markdown(
        """
        <style>
        body { background-color: #121212; color: #eee; }
        .stButton>button { background-color: #1a73e8; color: white; }
        </style>
        """,
        unsafe_allow_html=True,
    )
else:
    st.session_state.dark_mode = False

st.title("📝 Infinite Scrolling To-Do List with Subtasks")

# Add task button
if st.button("➕ Add New Task"):
    add_task()

tasks_to_show = st.session_state.tasks[: st.session_state.visible_count]

# Drag-and-drop reorder tasks
task_ids = [t["id"] for t in tasks_to_show]
new_task_order = sortables(task_ids, key=lambda x: f"task_{x}", direction="vertical", drag_handle=True)

if new_task_order != task_ids:
    reorder_tasks(new_task_order)

for task in tasks_to_show:
    col1, col2, col3 = st.columns([0.05, 0.7, 0.25])
    with col1:
        completed = st.checkbox("", value=task["completed"], key=f"task_done_{task['id']}")
        if completed != task["completed"]:
            toggle_complete(task["id"])
    with col2:
        new_title = st.text_input(
            "", value=task["title"], key=f"task_title_{task['id']}", label_visibility="collapsed"
        )
        if new_title != task["title"]:
            edit_task_title(task["id"], new_title)
    with col3:
        due_date = None
        if task["dueDate"]:
            try:
                due_date = date.fromisoformat(task["dueDate"])
            except:
                due_date = None
        new_due_date = st.date_input(
            "Due Date", value=due_date if due_date else date.today(), key=f"due_date_{task['id']}"
        )
        if new_due_date and new_due_date.isoformat() != task["dueDate"]:
            edit_due_date(task["id"], new_due_date)

    # Expand/collapse toggle
    expander_key = f"expander_{task['id']}"
    expanded = st.session_state.tasks[st.session_state.tasks.index(task)].get("expanded", True)
    if st.button("▼" if expanded else "▶", key=f"toggle_expand_{task['id']}", help="Expand/Collapse"):
        toggle_expand(task["id"])
        st.experimental_rerun()

    if expanded:
        # Subtasks
        subtask_ids = [s["id"] for s in task["subtasks"]]
        new_subtask_order = sortables(
            subtask_ids, key=f"subtasks_{task['id']}", direction="vertical", drag_handle=True
        )
        if new_subtask_order != subtask_ids:
            reorder_subtasks(task["id"], new_subtask_order)

        for sub in task["subtasks"]:
            col1, col2 = st.columns([0.05, 0.9])
            with col1:
                sub_completed = st.checkbox(
                    "", value=sub["completed"], key=f"sub_done_{sub['id']}"
                )
                if sub_completed != sub["completed"]:
                    toggle_complete(task["id"], sub["id"])
            with col2:
                new_subtitle = st.text_input(
                    "", value=sub["title"], key=f"subtask_title_{sub['id']}", label_visibility="collapsed"
                )
                if new_subtitle != sub["title"]:
                    edit_subtask_title(task["id"], sub["id"], new_subtitle)

        if st.button(f"➕ Add Subtask to '{task['title']}'", key=f"add_subtask_{task['id']}"):
            add_subtask(task["id"])
            st.experimental_rerun()

# Load more button for infinite scroll simulation
if st.session_state.visible_count < len(st.session_state.tasks):
    if st.button("⬇️ Load More Tasks"):
        st.session_state.visible_count += 5
        st.experimental_rerun()
