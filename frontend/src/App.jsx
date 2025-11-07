import React, { useEffect, useState } from "react";

const API_URL = "http://localhost:8000";
const STATUS_COLUMNS = [
  { key: "backlog", label: "Backlog" },
  { key: "todo", label: "To do" },
  { key: "in_progress", label: "In progress" },
  { key: "done", label: "Done" },
];

const SMALL_BUTTON_STYLE = {
  padding: "0.2rem 0.45rem",
  fontSize: "0.75rem",
  borderRadius: "0.3rem",
  border: "1px solid #d1d5db",
  background: "#f3f4f6",
  color: "#111827",
  cursor: "pointer",
};

const DANGER_SMALL_BUTTON_STYLE = {
  ...SMALL_BUTTON_STYLE,
  color: "#b91c1c",
  borderColor: "#fca5a5",
  background: "#fee2e2",
};

export default function App() {
  const [tickets, setTickets] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [status, setStatus] = useState("todo");
  const [category, setCategory] = useState("");
  const [room, setRoom] = useState("");
  const [assignee, setAssignee] = useState("");
  const [creating, setCreating] = useState(false);
  const [createError, setCreateError] = useState("");
  const [selectedTicket, setSelectedTicket] = useState(null);
  const [selectedCommentError, setSelectedCommentError] = useState("");
  const [selectedCommentLoading, setSelectedCommentLoading] = useState(false);
  const [selectedCommentAuthor, setSelectedCommentAuthor] = useState("");
  const [selectedCommentText, setSelectedCommentText] = useState("");
  const [searchTerm, setSearchTerm] = useState("");
  const [activeQuery, setActiveQuery] = useState("");
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newTaskText, setNewTaskText] = useState("");
  const [newTaskEta, setNewTaskEta] = useState("");
  const [creatingTask, setCreatingTask] = useState(false);
  const [taskError, setTaskError] = useState("");
  const [draggingTicketId, setDraggingTicketId] = useState(null);
  const [editingTicket, setEditingTicket] = useState(false);
  const [ticketForm, setTicketForm] = useState({
    title: "",
    description: "",
    status: "todo",
    category: "",
    room: "",
    assignee: "",
  });
  const [ticketUpdateError, setTicketUpdateError] = useState("");
  const [ticketUpdateLoading, setTicketUpdateLoading] = useState(false);
  const [editingComment, setEditingComment] = useState(null);
  const [commentActionError, setCommentActionError] = useState("");
  const [commentActionLoading, setCommentActionLoading] = useState(false);
  const [editingTask, setEditingTask] = useState(null);
  const [taskActionLoading, setTaskActionLoading] = useState(false);

  useEffect(() => {
    fetchTickets("");
  }, []);

  useEffect(() => {
    if (selectedTicket) {
      setTicketForm({
        title: selectedTicket.title || "",
        description: selectedTicket.description || "",
        status: selectedTicket.status || "todo",
        category: selectedTicket.category || "",
        room: selectedTicket.room || "",
        assignee: selectedTicket.assignee || "",
      });
    }
  }, [selectedTicket]);

  async function fetchTickets(query) {
    try {
      setLoading(true);
      setError("");
      let url = `${API_URL}/tickets`;
      if (query && query.trim()) {
        url += `?q=${encodeURIComponent(query.trim())}`;
      }
      const res = await fetch(url);
      if (!res.ok) throw new Error(`API error: ${res.status}`);
      const data = await res.json();
      setTickets(data);
      if (selectedTicket) {
        const updated = data.find((t) => t.id === selectedTicket.id);
        if (updated) {
          setSelectedTicket(updated);
        } else {
          setSelectedTicket(null);
        }
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function handleCreate(e) {
    e.preventDefault();
    setCreateError("");
    setCreating(true);
    try {
      const res = await fetch(`${API_URL}/tickets`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title,
          description,
          status,
          category,
          room,
          assignee,
          comments: [],
          tasks: [],
        }),
      });
      if (!res.ok) {
        const text = await res.text();
        throw new Error(text || `Create failed: ${res.status}`);
      }
      setTitle("");
      setDescription("");
      setStatus("todo");
      setCategory("");
      setRoom("");
      setAssignee("");
      setShowCreateModal(false);
      await fetchTickets(activeQuery);
    } catch (err) {
      setCreateError(err.message);
    } finally {
      setCreating(false);
    }
  }

  function truncate(text, limit = 90) {
    if (!text) return "";
    if (text.length <= limit) return text;
    return text.slice(0, limit) + "...";
  }

  function handleTicketClick(ticket) {
    setSelectedTicket(ticket);
    setSelectedCommentError("");
    setSelectedCommentAuthor("");
    setSelectedCommentText("");
    setNewTaskText("");
    setNewTaskEta("");
    setTaskError("");
    setEditingTicket(false);
    setTicketUpdateError("");
    setTicketUpdateLoading(false);
    setTicketForm({
      title: ticket.title || "",
      description: ticket.description || "",
      status: ticket.status || "todo",
      category: ticket.category || "",
      room: ticket.room || "",
      assignee: ticket.assignee || "",
    });
    setEditingComment(null);
    setCommentActionError("");
    setCommentActionLoading(false);
    setEditingTask(null);
    setTaskActionLoading(false);
  }

  function handleTicketDetailChange(field, value) {
    setTicketForm((prev) => ({ ...prev, [field]: value }));
  }

  async function handleUpdateTicketDetails(e) {
    e.preventDefault();
    if (!selectedTicket) return;
    setTicketUpdateError("");
    setTicketUpdateLoading(true);
    try {
      const res = await fetch(`${API_URL}/tickets/${selectedTicket.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          title: ticketForm.title,
          description: ticketForm.description,
          status: ticketForm.status,
          category: ticketForm.category,
          room: ticketForm.room,
          assignee: ticketForm.assignee,
        }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Update failed: ${res.status}`);
      }
      setEditingTicket(false);
      await fetchTickets(activeQuery);
    } catch (err) {
      setTicketUpdateError(err.message);
    } finally {
      setTicketUpdateLoading(false);
    }
  }

  function handleCancelTicketEdit() {
    if (!selectedTicket) {
      setEditingTicket(false);
      return;
    }
    setTicketForm({
      title: selectedTicket.title || "",
      description: selectedTicket.description || "",
      status: selectedTicket.status || "todo",
      category: selectedTicket.category || "",
      room: selectedTicket.room || "",
      assignee: selectedTicket.assignee || "",
    });
    setTicketUpdateError("");
    setEditingTicket(false);
  }

  function formatDateTimeLocal(value) {
    if (!value) return "";
    const date = new Date(value);
    const offsetMs = date.getTimezoneOffset() * 60 * 1000;
    const local = new Date(date.getTime() - offsetMs);
    return local.toISOString().slice(0, 16);
  }

  function handleStartEditComment(comment) {
    setEditingComment({
      id: comment.id,
      author: comment.author || "",
      text: comment.text || "",
    });
    setCommentActionError("");
  }

  function handleCancelEditComment() {
    setEditingComment(null);
    setCommentActionError("");
  }

  async function handleSaveCommentEdit(e) {
    e.preventDefault();
    if (!selectedTicket || !editingComment) return;
    if (!editingComment.text.trim()) {
      setCommentActionError("Comment text required");
      return;
    }
    setCommentActionError("");
    setCommentActionLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/comments/${editingComment.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            author: editingComment.author ? editingComment.author : null,
            text: editingComment.text,
          }),
        }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Comment update failed: ${res.status}`);
      }
      setEditingComment(null);
      await fetchTickets(activeQuery);
    } catch (err) {
      setCommentActionError(err.message);
    } finally {
      setCommentActionLoading(false);
    }
  }

  async function handleDeleteComment(commentId) {
    if (!selectedTicket || commentActionLoading) return;
    setCommentActionError("");
    setCommentActionLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/comments/${commentId}`,
        { method: "DELETE" }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Comment delete failed: ${res.status}`);
      }
      if (editingComment && editingComment.id === commentId) {
        setEditingComment(null);
      }
      await fetchTickets(activeQuery);
    } catch (err) {
      setCommentActionError(err.message);
    } finally {
      setCommentActionLoading(false);
    }
  }

  function handleStartEditTask(task) {
    setEditingTask({
      id: task.id,
      text: task.text || "",
      eta: task.eta ? formatDateTimeLocal(task.eta) : "",
    });
    setTaskError("");
  }

  function handleCancelEditTask() {
    setEditingTask(null);
  }

  async function handleSaveTaskEdit(e) {
    e.preventDefault();
    if (!selectedTicket || !editingTask) return;
    if (!editingTask.text.trim()) {
      setTaskError("Task text required");
      return;
    }
    setTaskError("");
    setTaskActionLoading(true);
    try {
      const payload = {
        text: editingTask.text.trim(),
      };
      if (editingTask.eta === "") {
        payload.eta = null;
      } else if (editingTask.eta) {
        payload.eta = new Date(editingTask.eta).toISOString();
      }
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/tasks/${editingTask.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(payload),
        }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Task update failed: ${res.status}`);
      }
      setEditingTask(null);
      await fetchTickets(activeQuery);
    } catch (err) {
      setTaskError(err.message);
    } finally {
      setTaskActionLoading(false);
    }
  }

  async function handleDeleteTask(taskId) {
    if (!selectedTicket || taskActionLoading) return;
    setTaskError("");
    setTaskActionLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/tasks/${taskId}`,
        { method: "DELETE" }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Task delete failed: ${res.status}`);
      }
      if (editingTask && editingTask.id === taskId) {
        setEditingTask(null);
      }
      await fetchTickets(activeQuery);
    } catch (err) {
      setTaskError(err.message);
    } finally {
      setTaskActionLoading(false);
    }
  }

  async function handleAddCommentToSelected(e) {
    e.preventDefault();
    if (!selectedTicket) return;
    if (!selectedCommentText.trim()) {
      setSelectedCommentError("Comment text required");
      return;
    }
    setSelectedCommentError("");
    setSelectedCommentLoading(true);
    try {
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/comments`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            author: selectedCommentAuthor || null,
            text: selectedCommentText,
          }),
        }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Comment failed: ${res.status}`);
      }
      setSelectedCommentAuthor("");
      setSelectedCommentText("");
      await fetchTickets(activeQuery);
    } catch (err) {
      setSelectedCommentError(err.message);
    } finally {
      setSelectedCommentLoading(false);
    }
  }

  async function handleCreateTask(e) {
    e.preventDefault();
    if (!selectedTicket) return;
    if (!newTaskText.trim()) {
      setTaskError("Task text required");
      return;
    }
    setTaskError("");
    setCreatingTask(true);
    try {
      const body = {
        text: newTaskText.trim(),
      };
      if (newTaskEta) {
        body.eta = new Date(newTaskEta).toISOString();
      }
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/tasks`,
        {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Task failed: ${res.status}`);
      }
      setNewTaskText("");
      setNewTaskEta("");
      await fetchTickets(activeQuery);
    } catch (err) {
      setTaskError(err.message);
    } finally {
      setCreatingTask(false);
    }
  }

  async function handleToggleTask(task) {
    if (!selectedTicket) return;
    try {
      const res = await fetch(
        `${API_URL}/tickets/${selectedTicket.id}/tasks/${task.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            completed: !task.completed,
          }),
        }
      );
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Toggle failed: ${res.status}`);
      }
      await fetchTickets(activeQuery);
    } catch (err) {
      setTaskError(err.message);
    }
  }

  function handleSearchInput(e) {
    setSearchTerm(e.target.value);
    if (!e.target.value.trim()) {
      setActiveQuery("");
      fetchTickets("");
    }
  }

  function handleSearchSubmit(e) {
    e.preventDefault();
    const q = searchTerm.trim();
    setActiveQuery(q);
    fetchTickets(q);
  }

  function openCreateModal() {
    setShowCreateModal(true);
    setCreateError("");
  }

  function closeCreateModal() {
    if (creating) return;
    setShowCreateModal(false);
  }

  function handleDragStart(ticketId) {
    setDraggingTicketId(ticketId);
  }

  function handleDragEnd() {
    setDraggingTicketId(null);
  }

  async function persistStatusIfChanged(ticketId, oldStatus, newStatus) {
    if (oldStatus === newStatus) return;
    try {
      const res = await fetch(`${API_URL}/tickets/${ticketId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) {
        const t = await res.text();
        throw new Error(t || `Status update failed: ${res.status}`);
      }
    } catch (err) {
      fetchTickets(activeQuery);
    }
  }

  async function moveTicket(draggedId, targetStatus, beforeTicketId = null) {
    const current = [...tickets];
    const dragged = current.find((t) => t.id === draggedId);
    if (!dragged) return;
    const oldStatus = dragged.status;
    const updatedList = current.filter((t) => t.id !== draggedId);
    const ticketCopy = { ...dragged, status: targetStatus };
    if (beforeTicketId) {
      const targetIndex = updatedList.findIndex((t) => t.id === beforeTicketId);
      if (targetIndex === -1) {
        const insertIndex = lastIndexOfStatus(updatedList, targetStatus);
        updatedList.splice(insertIndex, 0, ticketCopy);
      } else {
        updatedList.splice(targetIndex, 0, ticketCopy);
      }
    } else {
      const insertIndex = lastIndexOfStatus(updatedList, targetStatus);
      updatedList.splice(insertIndex, 0, ticketCopy);
    }
    setTickets(updatedList);
    if (selectedTicket && selectedTicket.id === draggedId) {
      setSelectedTicket(ticketCopy);
    }
    await persistStatusIfChanged(draggedId, oldStatus, targetStatus);
  }

  function lastIndexOfStatus(list, status) {
    let last = -1;
    for (let i = 0; i < list.length; i++) {
      if (list[i].status === status) last = i;
    }
    if (last === -1) return list.length;
    return last + 1;
  }

  function handleColumnDragOver(e) {
    e.preventDefault();
  }

  function handleTicketDragOver(e) {
    e.preventDefault();
  }

  async function handleDropOnColumn(columnKey) {
    if (!draggingTicketId) return;
    await moveTicket(draggingTicketId, columnKey, null);
    setDraggingTicketId(null);
  }

  async function handleDropOnTicket(columnKey, targetTicketId) {
    if (!draggingTicketId) return;
    if (draggingTicketId === targetTicketId) {
      setDraggingTicketId(null);
      return;
    }
    await moveTicket(draggingTicketId, columnKey, targetTicketId);
    setDraggingTicketId(null);
  }

  if (loading && !tickets.length && !error) {
    return <div style={{ padding: "1rem" }}>Loading tickets...</div>;
  }

  if (error) {
    return (
      <div style={{ padding: "1rem", color: "red" }}>
        Error talking to API: {error}
      </div>
    );
  }

  return (
    <div style={{ padding: "1.5rem", maxWidth: "1200px", margin: "0 auto" }}>
      <div
        style={{
          display: "flex",
          gap: "1rem",
          alignItems: "center",
          marginBottom: "1rem",
        }}
      >
        <h1 style={{ margin: 0 }}>Lifemate</h1>
        <form
          onSubmit={handleSearchSubmit}
          style={{ display: "flex", gap: "0.5rem", flex: 1, maxWidth: "420px" }}
        >
          <input
            type="text"
            value={searchTerm}
            onChange={handleSearchInput}
            placeholder="Search tickets..."
            style={{ flex: 1, padding: "0.4rem" }}
          />
          <button
            type="submit"
            style={{
              padding: "0.4rem 0.7rem",
              background: "#2563eb",
              color: "white",
              border: "none",
              borderRadius: "0.3rem",
              cursor: "pointer",
            }}
          >
            Search
          </button>
        </form>
        <button
          onClick={openCreateModal}
          style={{
            padding: "0.4rem 0.7rem",
            background: "#0f766e",
            color: "white",
            border: "none",
            borderRadius: "0.3rem",
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          New ticket
        </button>
        {activeQuery ? (
          <div style={{ fontSize: "0.8rem", color: "#6b7280" }}>
            Showing results for: <strong>{activeQuery}</strong>
          </div>
        ) : null}
      </div>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, minmax(0, 1fr))",
          gap: "1rem",
          alignItems: "flex-start",
        }}
      >
        {STATUS_COLUMNS.map((col) => {
          const colTickets = tickets.filter((t) => t.status === col.key);
          return (
            <div
              key={col.key}
              onDragOver={handleColumnDragOver}
              onDrop={() => handleDropOnColumn(col.key)}
              style={{
                background: "#f3f4f6",
                borderRadius: "0.5rem",
                padding: "0.5rem",
                minHeight: "150px",
              }}
            >
              <h3 style={{ margin: "0 0 0.5rem 0" }}>
                {col.label} ({colTickets.length})
              </h3>
              <div style={{ display: "grid", gap: "0.5rem" }}>
                {colTickets.length === 0 ? (
                  <div
                    style={{
                      background: "#fff",
                      border: "1px dashed #d1d5db",
                      borderRadius: "0.5rem",
                      padding: "0.5rem",
                      fontSize: "0.8rem",
                      color: "#6b7280",
                    }}
                  >
                    No tickets
                  </div>
                ) : (
                  colTickets.map((t) => (
                    <button
                      key={t.id}
                      onClick={() => handleTicketClick(t)}
                      draggable
                      onDragStart={() => handleDragStart(t.id)}
                      onDragEnd={handleDragEnd}
                      onDragOver={handleTicketDragOver}
                      onDrop={(e) => {
                        e.stopPropagation();
                        handleDropOnTicket(col.key, t.id);
                      }}
                      style={{
                        textAlign: "left",
                        background: draggingTicketId === t.id ? "#dbeafe" : "#fff",
                        border: "1px solid #e5e7eb",
                        borderRadius: "0.5rem",
                        padding: "0.5rem 0.6rem",
                        cursor: "pointer",
                      }}
                    >
                      <div
                        style={{ fontWeight: 600, marginBottom: "0.25rem" }}
                      >
                        {t.title}
                      </div>
                      <div style={{ fontSize: "0.75rem", color: "#4b5563" }}>
                        {truncate(t.description)}
                      </div>
                      <div
                        style={{
                          fontSize: "0.7rem",
                          color: "#6b7280",
                          marginTop: "0.25rem",
                        }}
                      >
                        {t.assignee ? `Assignee: ${t.assignee}` : "Unassigned"}
                      </div>
                    </button>
                  ))
                )}
              </div>
            </div>
          );
        })}
      </div>

      {selectedTicket && (
        <div
          style={{
            marginTop: "1.5rem",
            border: "1px solid #d1d5db",
            borderRadius: "0.5rem",
            padding: "1rem",
            background: "white",
          }}
        >
          <div style={{ display: "flex", gap: "1rem" }}>
            <div style={{ flex: 2, minWidth: 0 }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "flex-start",
                  gap: "0.75rem",
                }}
              >
                <h2 style={{ marginTop: 0, marginBottom: 0 }}>
                  {selectedTicket.title}{" "}
                  <span style={{ fontSize: "0.8rem", color: "#6b7280" }}>
                    #{selectedTicket.id}
                  </span>
                </h2>
                {!editingTicket ? (
                  <button
                    type="button"
                    onClick={() => setEditingTicket(true)}
                    style={SMALL_BUTTON_STYLE}
                  >
                    Edit details
                  </button>
                ) : null}
              </div>
              {editingTicket ? (
                <form
                  onSubmit={handleUpdateTicketDetails}
                  style={{ display: "grid", gap: "0.5rem", maxWidth: "520px" }}
                >
                  <input
                    type="text"
                    value={ticketForm.title}
                    onChange={(e) => handleTicketDetailChange("title", e.target.value)}
                    required
                    style={{ padding: "0.45rem" }}
                  />
                  <textarea
                    value={ticketForm.description}
                    onChange={(e) =>
                      handleTicketDetailChange("description", e.target.value)
                    }
                    rows={3}
                    style={{ padding: "0.45rem" }}
                  />
                  <select
                    value={ticketForm.status}
                    onChange={(e) => handleTicketDetailChange("status", e.target.value)}
                    style={{ padding: "0.45rem" }}
                  >
                    {STATUS_COLUMNS.map((s) => (
                      <option key={s.key} value={s.key}>
                        {s.label}
                      </option>
                    ))}
                  </select>
                  <input
                    type="text"
                    placeholder="Category"
                    value={ticketForm.category}
                    onChange={(e) => handleTicketDetailChange("category", e.target.value)}
                    style={{ padding: "0.45rem" }}
                  />
                  <input
                    type="text"
                    placeholder="Room"
                    value={ticketForm.room}
                    onChange={(e) => handleTicketDetailChange("room", e.target.value)}
                    style={{ padding: "0.45rem" }}
                  />
                  <input
                    type="text"
                    placeholder="Assignee"
                    value={ticketForm.assignee}
                    onChange={(e) => handleTicketDetailChange("assignee", e.target.value)}
                    style={{ padding: "0.45rem" }}
                  />
                  {ticketUpdateError ? (
                    <div style={{ color: "red", fontSize: "0.85rem" }}>
                      {ticketUpdateError}
                    </div>
                  ) : null}
                  <div style={{ display: "flex", gap: "0.5rem" }}>
                    <button
                      type="submit"
                      disabled={ticketUpdateLoading}
                      style={{
                        padding: "0.45rem 0.8rem",
                        background: "#2563eb",
                        color: "white",
                        border: "none",
                        borderRadius: "0.3rem",
                        cursor: "pointer",
                      }}
                    >
                      {ticketUpdateLoading ? "Saving..." : "Save"}
                    </button>
                    <button
                      type="button"
                      onClick={handleCancelTicketEdit}
                      disabled={ticketUpdateLoading}
                      style={{
                        ...SMALL_BUTTON_STYLE,
                        background: "#e5e7eb",
                      }}
                    >
                      Cancel
                    </button>
                  </div>
                </form>
              ) : (
                <>
                  <p style={{ margin: "0.5rem 0" }}>
                    <strong>Status:</strong> {selectedTicket.status} •{" "}
                    <strong>Room:</strong> {selectedTicket.room || "n/a"} •{" "}
                    <strong>Category:</strong> {selectedTicket.category || "n/a"} •{" "}
                    <strong>Assignee:</strong>{" "}
                    {selectedTicket.assignee || "Unassigned"}
                  </p>
                  <p style={{ margin: "0.5rem 0 1rem 0" }}>
                    {selectedTicket.description || "No description"}
                  </p>
                  {ticketUpdateError ? (
                    <div style={{ color: "red", fontSize: "0.85rem" }}>
                      {ticketUpdateError}
                    </div>
                  ) : null}
                </>
              )}

              <div>
                <h3 style={{ marginBottom: "0.5rem" }}>Comments</h3>
                {commentActionError ? (
                  <div style={{ color: "red", fontSize: "0.8rem", marginBottom: "0.5rem" }}>
                    {commentActionError}
                  </div>
                ) : null}
                {selectedTicket.comments &&
                selectedTicket.comments.length > 0 ? (
                  <ul style={{ margin: 0, paddingLeft: "1rem" }}>
                    {selectedTicket.comments.map((c) => {
                      const isEditing = editingComment && editingComment.id === c.id;
                      return (
                        <li key={c.id} style={{ marginBottom: "0.6rem" }}>
                          {isEditing ? (
                            <form
                              onSubmit={handleSaveCommentEdit}
                              style={{ display: "grid", gap: "0.4rem" }}
                            >
                              <input
                                type="text"
                                placeholder="Author"
                                value={editingComment.author}
                                onChange={(e) =>
                                  setEditingComment((prev) => ({
                                    ...prev,
                                    author: e.target.value,
                                  }))
                                }
                                style={{ padding: "0.35rem" }}
                              />
                              <textarea
                                placeholder="Comment"
                                value={editingComment.text}
                                onChange={(e) =>
                                  setEditingComment((prev) => ({
                                    ...prev,
                                    text: e.target.value,
                                  }))
                                }
                                rows={2}
                                style={{ padding: "0.35rem" }}
                              />
                              <div
                                style={{
                                  display: "flex",
                                  gap: "0.4rem",
                                  justifyContent: "flex-end",
                                }}
                              >
                                <button
                                  type="submit"
                                  disabled={commentActionLoading}
                                  style={{
                                    padding: "0.35rem 0.6rem",
                                    background: "#2563eb",
                                    color: "white",
                                    border: "none",
                                    borderRadius: "0.3rem",
                                    cursor: "pointer",
                                  }}
                                >
                                  {commentActionLoading ? "Saving..." : "Save"}
                                </button>
                                <button
                                  type="button"
                                  onClick={handleCancelEditComment}
                                  disabled={commentActionLoading}
                                  style={{
                                    ...SMALL_BUTTON_STYLE,
                                    background: "#e5e7eb",
                                  }}
                                >
                                  Cancel
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleDeleteComment(c.id)}
                                  disabled={commentActionLoading}
                                  style={DANGER_SMALL_BUTTON_STYLE}
                                >
                                  Delete
                                </button>
                              </div>
                            </form>
                          ) : (
                            <div
                              style={{
                                display: "flex",
                                justifyContent: "space-between",
                                gap: "0.5rem",
                              }}
                            >
                              <div style={{ flex: 1 }}>
                                <strong>{c.author || "Anon"}:</strong> {c.text}
                              </div>
                              <div style={{ display: "flex", gap: "0.3rem" }}>
                                <button
                                  type="button"
                                  onClick={() => handleStartEditComment(c)}
                                  style={SMALL_BUTTON_STYLE}
                                  disabled={commentActionLoading}
                                >
                                  Edit
                                </button>
                                <button
                                  type="button"
                                  onClick={() => handleDeleteComment(c.id)}
                                  style={DANGER_SMALL_BUTTON_STYLE}
                                  disabled={commentActionLoading}
                                >
                                  Delete
                                </button>
                              </div>
                            </div>
                          )}
                        </li>
                      );
                    })}
                  </ul>
                ) : (
                  <p style={{ color: "#6b7280", fontSize: "0.85rem" }}>
                    No comments yet.
                  </p>
                )}
              </div>

              <form
                onSubmit={handleAddCommentToSelected}
                style={{
                  marginTop: "1rem",
                  display: "grid",
                  gap: "0.5rem",
                  maxWidth: "420px",
                }}
              >
                <input
                  type="text"
                  placeholder="Your name (optional)"
                  value={selectedCommentAuthor}
                  onChange={(e) => setSelectedCommentAuthor(e.target.value)}
                  style={{ padding: "0.4rem" }}
                />
                <input
                  type="text"
                  placeholder="Add a comment"
                  value={selectedCommentText}
                  onChange={(e) => setSelectedCommentText(e.target.value)}
                  style={{ padding: "0.4rem" }}
                />
                {selectedCommentError ? (
                  <div style={{ color: "red", fontSize: "0.8rem" }}>
                    {selectedCommentError}
                  </div>
                ) : null}
                <button
                  type="submit"
                  disabled={selectedCommentLoading}
                  style={{
                    padding: "0.5rem 0.7rem",
                    background: "#0f766e",
                    color: "#fff",
                    border: "none",
                    borderRadius: "0.3rem",
                    cursor: "pointer",
                    width: "8rem",
                  }}
                >
                  {selectedCommentLoading ? "Saving..." : "Add comment"}
                </button>
              </form>
            </div>

            <div style={{ flex: 1, minWidth: "240px" }}>
              <h3 style={{ marginTop: 0 }}>Tasks</h3>
              {selectedTicket.tasks && selectedTicket.tasks.length > 0 ? (
                <div style={{ display: "grid", gap: "0.4rem" }}>
                  {selectedTicket.tasks.map((task) => {
                    const isEditingTask = editingTask && editingTask.id === task.id;
                    return (
                      <div
                        key={task.id}
                        style={{
                          background: "#f9fafb",
                          border: "1px solid #e5e7eb",
                          borderRadius: "0.4rem",
                          padding: "0.5rem",
                          display: "grid",
                          gap: "0.4rem",
                        }}
                      >
                        {isEditingTask ? (
                          <form
                            onSubmit={handleSaveTaskEdit}
                            style={{ display: "grid", gap: "0.4rem" }}
                          >
                            <div
                              style={{
                                display: "flex",
                                gap: "0.5rem",
                                alignItems: "flex-start",
                              }}
                            >
                              <input
                                type="checkbox"
                                checked={task.completed}
                                onChange={() => handleToggleTask(task)}
                                style={{ marginTop: "0.25rem" }}
                                disabled={taskActionLoading}
                              />
                              <div style={{ flex: 1, display: "grid", gap: "0.4rem" }}>
                                <input
                                  type="text"
                                  value={editingTask.text}
                                  onChange={(e) =>
                                    setEditingTask((prev) => ({
                                      ...prev,
                                      text: e.target.value,
                                    }))
                                  }
                                  style={{ padding: "0.4rem" }}
                                />
                                <input
                                  type="datetime-local"
                                  value={editingTask.eta}
                                  onChange={(e) =>
                                    setEditingTask((prev) => ({
                                      ...prev,
                                      eta: e.target.value,
                                    }))
                                  }
                                  style={{ padding: "0.4rem" }}
                                />
                              </div>
                            </div>
                            <div
                              style={{
                                display: "flex",
                                gap: "0.4rem",
                                justifyContent: "flex-end",
                              }}
                            >
                              <button
                                type="submit"
                                disabled={taskActionLoading}
                                style={{
                                  padding: "0.4rem 0.6rem",
                                  background: "#2563eb",
                                  color: "white",
                                  border: "none",
                                  borderRadius: "0.3rem",
                                  cursor: "pointer",
                                }}
                              >
                                {taskActionLoading ? "Saving..." : "Save"}
                              </button>
                              <button
                                type="button"
                                onClick={handleCancelEditTask}
                                disabled={taskActionLoading}
                                style={{
                                  ...SMALL_BUTTON_STYLE,
                                  background: "#e5e7eb",
                                }}
                              >
                                Cancel
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDeleteTask(task.id)}
                                disabled={taskActionLoading}
                                style={DANGER_SMALL_BUTTON_STYLE}
                              >
                                Delete
                              </button>
                            </div>
                          </form>
                        ) : (
                          <div
                            style={{
                              display: "flex",
                              gap: "0.5rem",
                              alignItems: "flex-start",
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={task.completed}
                              onChange={() => handleToggleTask(task)}
                              style={{ marginTop: "0.25rem" }}
                            />
                            <div style={{ flex: 1 }}>
                              <div
                                style={{
                                  textDecoration: task.completed
                                    ? "line-through"
                                    : "none",
                                }}
                              >
                                {task.text}
                              </div>
                              {task.eta ? (
                                <div
                                  style={{ fontSize: "0.7rem", color: "#6b7280" }}
                                >
                                  ETA: {new Date(task.eta).toLocaleString()}
                                </div>
                              ) : null}
                            </div>
                            <div
                              style={{
                                display: "flex",
                                flexDirection: "column",
                                gap: "0.3rem",
                              }}
                            >
                              <button
                                type="button"
                                onClick={() => handleStartEditTask(task)}
                                style={SMALL_BUTTON_STYLE}
                                disabled={taskActionLoading}
                              >
                                Edit
                              </button>
                              <button
                                type="button"
                                onClick={() => handleDeleteTask(task.id)}
                                style={DANGER_SMALL_BUTTON_STYLE}
                                disabled={taskActionLoading}
                              >
                                Delete
                              </button>
                            </div>
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>
              ) : (
                <p style={{ color: "#6b7280", fontSize: "0.8rem" }}>
                  No tasks yet.
                </p>
              )}

              <form
                onSubmit={handleCreateTask}
                style={{ marginTop: "0.75rem", display: "grid", gap: "0.4rem" }}
              >
                <input
                  type="text"
                  placeholder="New task..."
                  value={newTaskText}
                  onChange={(e) => setNewTaskText(e.target.value)}
                  style={{ padding: "0.4rem" }}
                />
                <input
                  type="datetime-local"
                  value={newTaskEta}
                  onChange={(e) => setNewTaskEta(e.target.value)}
                  style={{ padding: "0.4rem" }}
                />
                {taskError ? (
                  <div style={{ color: "red", fontSize: "0.75rem" }}>
                    {taskError}
                  </div>
                ) : null}
                <button
                  type="submit"
                  disabled={creatingTask}
                  style={{
                    padding: "0.4rem 0.5rem",
                    background: "#2563eb",
                    color: "white",
                    border: "none",
                    borderRadius: "0.3rem",
                    cursor: "pointer",
                    width: "9rem",
                  }}
                >
                  {creatingTask ? "Adding..." : "+ Create task"}
                </button>
              </form>
            </div>
          </div>
        </div>
      )}

      {showCreateModal && (
        <div
          style={{
            position: "fixed",
            inset: 0,
            background: "rgba(0,0,0,0.3)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            zIndex: 50,
          }}
          onClick={closeCreateModal}
        >
          <div
            onClick={(e) => e.stopPropagation()}
            style={{
              background: "white",
              borderRadius: "0.5rem",
              padding: "1rem",
              width: "420px",
              maxWidth: "90vw",
              boxShadow: "0 10px 30px rgba(0,0,0,0.15)",
              display: "grid",
              gap: "0.5rem",
            }}
          >
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
              }}
            >
              <h2 style={{ margin: 0, fontSize: "1rem" }}>Create ticket</h2>
              <button
                onClick={closeCreateModal}
                style={{
                  background: "transparent",
                  border: "none",
                  fontSize: "1.1rem",
                  cursor: "pointer",
                }}
              >
                ×
              </button>
            </div>
            <form
              onSubmit={handleCreate}
              style={{ display: "grid", gap: "0.5rem" }}
            >
              <input
                type="text"
                placeholder="Title"
                value={title}
                required
                onChange={(e) => setTitle(e.target.value)}
                style={{ padding: "0.4rem" }}
              />
              <textarea
                placeholder="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                rows={3}
                style={{ padding: "0.4rem" }}
              />
              <select
                value={status}
                onChange={(e) => setStatus(e.target.value)}
                style={{ padding: "0.4rem" }}
              >
                {STATUS_COLUMNS.map((s) => (
                  <option key={s.key} value={s.key}>
                    {s.label}
                  </option>
                ))}
              </select>
              <input
                type="text"
                placeholder="Category"
                value={category}
                onChange={(e) => setCategory(e.target.value)}
                style={{ padding: "0.4rem" }}
              />
              <input
                type="text"
                placeholder="Room"
                value={room}
                onChange={(e) => setRoom(e.target.value)}
                style={{ padding: "0.4rem" }}
              />
              <input
                type="text"
                placeholder="Assignee (e.g. Phil, Courtney)"
                value={assignee}
                onChange={(e) => setAssignee(e.target.value)}
                style={{ padding: "0.4rem" }}
              />
              {createError ? (
                <div style={{ color: "red", fontSize: "0.85rem" }}>
                  {createError}
                </div>
              ) : null}
              <button
                type="submit"
                disabled={creating}
                style={{
                  padding: "0.5rem 0.7rem",
                  background: "#2563eb",
                  color: "white",
                  border: "none",
                  borderRadius: "0.3rem",
                  cursor: "pointer",
                  width: "9rem",
                }}
              >
                {creating ? "Creating..." : "Create"}
              </button>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

