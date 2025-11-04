import json
import os
import threading
import uuid
from datetime import datetime
from typing import List, Optional
from app.schemas import (
    TicketRead,
    TicketCreate,
    TicketUpdate,
    CommentCreate,
    CommentRead,
    CommentUpdate,
    TaskCreate,
    TaskRead,
    TaskUpdate,
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
DATA_FILE = os.path.join(BASE_DIR, "data", "tickets.json")

_write_lock = threading.Lock()

def _load_raw() -> List[dict]:
    if not os.path.exists(DATA_FILE):
        return []
    for _ in range(3):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except json.JSONDecodeError:
            continue
    return []

def _save_raw(data: List[dict]) -> None:
    with _write_lock:
        tmp_file = DATA_FILE + f".{uuid.uuid4().hex}.tmp"
        with open(tmp_file, "w") as f:
            json.dump(data, f, indent=2)
        os.replace(tmp_file, DATA_FILE)

def list_tickets() -> List[TicketRead]:
    data = _load_raw()
    fixed = []
    for t in data:
        if "comments" not in t:
            t["comments"] = []
        if "tasks" not in t:
            t["tasks"] = []
        fixed.append(TicketRead(**t))
    return fixed

def get_ticket(ticket_id: int) -> Optional[TicketRead]:
    data = _load_raw()
    for t in data:
        if t["id"] == ticket_id:
            if "comments" not in t:
                t["comments"] = []
            if "tasks" not in t:
                t["tasks"] = []
            return TicketRead(**t)
    return None

def _next_ticket_id(tickets: List[dict]) -> int:
    if not tickets:
        return 1
    return max(t["id"] for t in tickets) + 1

def _next_comment_id(ticket: dict) -> int:
    if not ticket.get("comments"):
        return 1
    return max(c["id"] for c in ticket["comments"]) + 1

def _next_task_id(ticket: dict) -> int:
    if not ticket.get("tasks"):
        return 1
    return max(c["id"] for c in ticket["tasks"]) + 1

def create_ticket(body: TicketCreate) -> TicketRead:
    tickets = _load_raw()
    now = datetime.utcnow().isoformat()
    new_id = _next_ticket_id(tickets)
    comments = []
    for c in body.comments:
      comments.append(
          {
              "id": len(comments) + 1,
              "author": c.author,
              "text": c.text,
              "created_at": now,
          }
      )
    tasks = []
    for task in body.tasks:
        tasks.append(
            {
                "id": len(tasks) + 1,
                "text": task.text,
                "eta": task.eta.isoformat() if task.eta else None,
                "completed": False,
                "created_at": now,
            }
        )
    ticket = {
        "id": new_id,
        "title": body.title,
        "description": body.description,
        "status": body.status,
        "category": body.category,
        "room": body.room,
        "assignee": body.assignee,
        "comments": comments,
        "tasks": tasks,
        "created_at": now,
        "updated_at": now,
    }
    tickets.append(ticket)
    _save_raw(tickets)
    return TicketRead(**ticket)

def update_ticket(ticket_id: int, body: TicketUpdate) -> Optional[TicketRead]:
    tickets = _load_raw()
    updated = None
    for t in tickets:
        if t["id"] == ticket_id:
            if body.title is not None:
                t["title"] = body.title
            if body.description is not None:
                t["description"] = body.description
            if body.status is not None:
                t["status"] = body.status
            if body.category is not None:
                t["category"] = body.category
            if body.room is not None:
                t["room"] = body.room
            if body.assignee is not None:
                t["assignee"] = body.assignee
            if "comments" not in t:
                t["comments"] = []
            if "tasks" not in t:
                t["tasks"] = []
            t["updated_at"] = datetime.utcnow().isoformat()
            updated = t
            break
    if updated is None:
        return None
    _save_raw(tickets)
    return TicketRead(**updated)

def delete_ticket(ticket_id: int) -> bool:
    tickets = _load_raw()
    new_tickets = [t for t in tickets if t["id"] != ticket_id]
    if len(new_tickets) == len(tickets):
        return False
    _save_raw(new_tickets)
    return True

def add_comment(ticket_id: int, body: CommentCreate) -> Optional[CommentRead]:
    tickets = _load_raw()
    for t in tickets:
        if t["id"] == ticket_id:
            now = datetime.utcnow().isoformat()
            cid = _next_comment_id(t)
            comment = {
                "id": cid,
                "author": body.author,
                "text": body.text,
                "created_at": now,
            }
            if "comments" not in t:
                t["comments"] = []
            t["comments"].append(comment)
            t["updated_at"] = now
            _save_raw(tickets)
            return CommentRead(**comment)
    return None

def update_comment(ticket_id: int, comment_id: int, body: CommentUpdate) -> Optional[CommentRead]:
    tickets = _load_raw()
    for t in tickets:
        if t["id"] == ticket_id:
            if "comments" not in t:
                t["comments"] = []
            found = None
            for c in t["comments"]:
                if c["id"] == comment_id:
                    if body.author is not None:
                        c["author"] = body.author
                    if body.text is not None:
                        c["text"] = body.text
                    t["updated_at"] = datetime.utcnow().isoformat()
                    found = c
                    break
            if found is None:
                return None
            _save_raw(tickets)
            return CommentRead(**found)
    return None

def delete_comment(ticket_id: int, comment_id: int) -> bool:
    tickets = _load_raw()
    for t in tickets:
        if t["id"] == ticket_id:
            if "comments" not in t:
                t["comments"] = []
            new_comments = [c for c in t["comments"] if c["id"] != comment_id]
            if len(new_comments) == len(t["comments"]):
                return False
            t["comments"] = new_comments
            t["updated_at"] = datetime.utcnow().isoformat()
            _save_raw(tickets)
            return True
    return False

def add_task(ticket_id: int, body: TaskCreate) -> Optional[TaskRead]:
    tickets = _load_raw()
    for t in tickets:
        if t["id"] == ticket_id:
            now = datetime.utcnow().isoformat()
            tid = _next_task_id(t)
            task = {
                "id": tid,
                "text": body.text,
                "eta": body.eta.isoformat() if body.eta else None,
                "completed": False,
                "created_at": now,
            }
            if "tasks" not in t:
                t["tasks"] = []
            t["tasks"].append(task)
            t["updated_at"] = now
            _save_raw(tickets)
            return TaskRead(**task)
    return None

def update_task(ticket_id: int, task_id: int, body: TaskUpdate) -> Optional[TaskRead]:
    tickets = _load_raw()
    for t in tickets:
        if t["id"] == ticket_id:
            if "tasks" not in t:
                t["tasks"] = []
            found = None
            for k in t["tasks"]:
                if k["id"] == task_id:
                    if body.text is not None:
                        k["text"] = body.text
                    if body.eta is not None:
                        k["eta"] = body.eta.isoformat()
                    if body.completed is not None:
                        k["completed"] = body.completed
                    t["updated_at"] = datetime.utcnow().isoformat()
                    found = k
                    break
            if found is None:
                return None
            _save_raw(tickets)
            return TaskRead(**found)
    return None

def delete_task(ticket_id: int, task_id: int) -> bool:
    tickets = _load_raw()
    for t in tickets:
        if t["id"] == ticket_id:
            if "tasks" not in t:
                t["tasks"] = []
            new_tasks = [c for c in t["tasks"] if c["id"] != task_id]
            if len(new_tasks) == len(t["tasks"]):
                return False
            t["tasks"] = new_tasks
            t["updated_at"] = datetime.utcnow().isoformat()
            _save_raw(tickets)
            return True
    return False

