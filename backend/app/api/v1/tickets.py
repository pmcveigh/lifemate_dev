from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query, Depends
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import or_
from app.deps import get_db
from app import models
from app.schemas.ticket import (
    TicketRead,
    TicketCreate,
    TicketUpdate,
    CommentCreate,
    CommentUpdate,
    CommentRead,
    TaskCreate,
    TaskUpdate,
    TaskRead,
    TicketStatus,
)

router = APIRouter(prefix="/tickets", tags=["tickets"])

def _ticket_query(db: Session):
    return db.query(models.Ticket).options(
        joinedload(models.Ticket.comments),
        joinedload(models.Ticket.tasks),
    )

@router.get("/", response_model=List[TicketRead])
def get_all_tickets(
    status: Optional[TicketStatus] = Query(default=None),
    category: Optional[str] = Query(default=None),
    room: Optional[str] = Query(default=None),
    assignee: Optional[str] = Query(default=None),
    q: Optional[str] = Query(default=None),
    db: Session = Depends(get_db),
):
    query = _ticket_query(db)
    if status is not None:
        query = query.filter(models.Ticket.status == status)
    if category is not None:
        query = query.filter(models.Ticket.category == category)
    if room is not None:
        query = query.filter(models.Ticket.room == room)
    if assignee is not None:
        query = query.filter(models.Ticket.assignee == assignee)
    if q:
        like = f"%{q}%"
        query = query.filter(
            or_(
                models.Ticket.title.ilike(like),
                models.Ticket.description.ilike(like),
                models.Ticket.category.ilike(like),
                models.Ticket.room.ilike(like),
                models.Ticket.assignee.ilike(like),
            )
        )
    tickets = query.order_by(models.Ticket.status, models.Ticket.position, models.Ticket.id).all()
    return tickets

@router.get("/{ticket_id}", response_model=TicketRead)
def get_single_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = _ticket_query(db).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return ticket

@router.post("/", response_model=TicketRead, status_code=201)
def create_new_ticket(body: TicketCreate, db: Session = Depends(get_db)):
    max_pos = (
         db.query(models.Ticket.position)
         .filter(models.Ticket.status == body.status)
         .order_by(models.Ticket.position.desc())
         .first()
     )
     next_pos = (max_pos[0] + 1) if max_pos else 0
     ticket = models.Ticket(
         title=body.title,
         description=body.description,
         status=body.status,
         category=body.category,
         room=body.room,
         assignee=body.assignee,
         position=next_pos,
     )
     db.add(ticket)
     db.flush()
     for c in body.comments:
         comment = models.Comment(
             ticket_id=ticket.id,
             author=c.author,
             text=c.text,
         )
         db.add(comment)
+    next_task_pos = 0
     for t in body.tasks:
         task = models.Task(
             ticket_id=ticket.id,
             text=t.text,
             eta=t.eta,
             completed=False,
-            position=0,
+            position=next_task_pos,
         )
         db.add(task)
+        next_task_pos += 1
     db.commit()
     db.refresh(ticket)
     return ticket
 
 @router.patch("/{ticket_id}", response_model=TicketRead)
 def update_existing_ticket(ticket_id: int, body: TicketUpdate, db: Session = Depends(get_db)):
     ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
     if not ticket:
         raise HTTPException(status_code=404, detail="Ticket not found")
     if body.title is not None:
         ticket.title = body.title
     if body.description is not None:
         ticket.description = body.description
     if body.status is not None and body.status != ticket.status:
         max_pos = (
             db.query(models.Ticket.position)
             .filter(models.Ticket.status == body.status)
             .order_by(models.Ticket.position.desc())
             .first()
         )
         next_pos = (max_pos[0] + 1) if max_pos else 0
         ticket.status = body.status
         ticket.position = next_pos
     if body.category is not None:
         ticket.category = body.category
    if body.room is not None:
        ticket.room = body.room
    if body.assignee is not None:
        ticket.assignee = body.assignee
    if body.position is not None:
        ticket.position = body.position
    ticket.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(ticket)
    return ticket

@router.delete("/{ticket_id}", status_code=204)
def delete_existing_ticket(ticket_id: int, db: Session = Depends(get_db)):
    ticket = db.query(models.Ticket).filter(models.Ticket.id == ticket_id).first()
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    db.delete(ticket)
    db.commit()

@router.post("/{ticket_id}/comments", response_model=CommentRead, status_code=201)
def add_ticket_comment(ticket_id: int, body: CommentCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Ticket.id).filter(models.Ticket.id == ticket_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Ticket not found")
    comment = models.Comment(
        ticket_id=ticket_id,
        author=body.author,
        text=body.text,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment

@router.patch("/{ticket_id}/comments/{comment_id}", response_model=CommentRead)
def update_ticket_comment(ticket_id: int, comment_id: int, body: CommentUpdate, db: Session = Depends(get_db)):
    comment = (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id, models.Comment.ticket_id == ticket_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if body.author is not None:
        comment.author = body.author
    if body.text is not None:
        comment.text = body.text
    db.commit()
    db.refresh(comment)
    return comment

@router.delete("/{ticket_id}/comments/{comment_id}", status_code=204)
def delete_ticket_comment(ticket_id: int, comment_id: int, db: Session = Depends(get_db)):
    comment = (
        db.query(models.Comment)
        .filter(models.Comment.id == comment_id, models.Comment.ticket_id == ticket_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    db.delete(comment)
    db.commit()

@router.post("/{ticket_id}/tasks", response_model=TaskRead, status_code=201)
def add_ticket_task(ticket_id: int, body: TaskCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Ticket.id).filter(models.Ticket.id == ticket_id).first()
    if not exists:
        raise HTTPException(status_code=404, detail="Ticket not found")
    max_pos = (
        db.query(models.Task.position)
        .filter(models.Task.ticket_id == ticket_id)
        .order_by(models.Task.position.desc())
        .first()
    )
    next_pos = (max_pos[0] + 1) if max_pos else 0
    task = models.Task(
        ticket_id=ticket_id,
        text=body.text,
        eta=body.eta,
        completed=False,
        position=next_pos,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return task

@router.patch("/{ticket_id}/tasks/{task_id}", response_model=TaskRead)
def update_ticket_task(ticket_id: int, task_id: int, body: TaskUpdate, db: Session = Depends(get_db)):
    task = (
        db.query(models.Task)
        .filter(models.Task.ticket_id == ticket_id, models.Task.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    if body.text is not None:
        task.text = body.text
    if body.eta is not None:
        task.eta = body.eta
    if body.completed is not None:
        task.completed = body.completed
    if body.position is not None:
        task.position = body.position
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{ticket_id}/tasks/{task_id}", status_code=204)
def delete_ticket_task(ticket_id: int, task_id: int, db: Session = Depends(get_db)):
    task = (
        db.query(models.Task)
        .filter(models.Task.ticket_id == ticket_id, models.Task.id == task_id)
        .first()
    )
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()

