from __future__ import annotations
import json
import os
from dataclasses import dataclass, asdict, field
from datetime import datetime, date
from typing import List, Optional
import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry

DATA_FILE = os.path.join(os.path.dirname(__file__), "tasks_gui.json")
PRIORITIES = ("low", "medium", "high")
STATUSES = ("pending", "in-progress", "completed")

@dataclass
class Task:
    id: int
    title: str
    description: str = ""
    due_date: Optional[str] = None
    priority: str = "medium"
    status: str = "pending"
    created_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat(timespec="seconds"))

    def update(self, **kwargs):
        for k, v in kwargs.items():
            if v is None:
                continue
            setattr(self, k, v)
        self.updated_at = datetime.now().isoformat(timespec="seconds")

class Store:
    def __init__(self, path: str = DATA_FILE):
        self.path = path
        self.tasks: List[Task] = []
        self._next_id = 1
        self.load()

    def load(self):
        if not os.path.exists(self.path):
            self.tasks = []
            self._next_id = 1
            return
        with open(self.path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        self.tasks = [Task(**t) for t in raw.get("tasks", [])]
        self._next_id = raw.get("next_id", (max((t.id for t in self.tasks), default=0) + 1))

    def save(self):
        data = {"tasks": [asdict(t) for t in self.tasks], "next_id": self._next_id}
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def add(self, title, description="", due_date=None, priority="medium"):
        t = Task(
            id=self._next_id,
            title=title.strip(),
            description=description.strip(),
            due_date=due_date,
            priority=priority,
        )
        self.tasks.append(t)
        self._next_id += 1
        self.save()
        return t

    def delete(self, task_id: int):
        before = len(self.tasks)
        self.tasks = [t for t in self.tasks if t.id != task_id]
        if len(self.tasks) == before:
            raise ValueError("Task not found")
        self.save()

    def get(self, task_id: int) -> Task:
        for t in self.tasks:
            if t.id == task_id:
                return t
        raise ValueError("Task not found")

    def search(self, query: str):
        q = query.lower()
        return [t for t in self.tasks if q in t.title.lower() or q in t.description.lower()]

    def filtered(self, status=None, priority=None):
        items = self.tasks
        if status:
            items = [t for t in items if t.status == status]
        if priority:
            items = [t for t in items if t.priority == priority]
        return sorted(
            items,
            key=lambda t: (
                {"high": 0, "medium": 1, "low": 2}[t.priority],
                t.due_date or "9999-12-31",
                t.id,
            ),
        )

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("To-Do List")
        self.geometry("980x560")
        self.minsize(920, 520)

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.style.configure("Treeview", font=("Segoe UI", 11), rowheight=28)
        self.style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        self.style.map("Treeview", background=[("selected", "#4CAF50")], foreground=[("selected", "white")])

        self.store = Store()
        self._build_ui()
        self._populate()

    def _build_ui(self):
        form = ttk.LabelFrame(self, text="Task Details", padding=10)
        form.pack(fill="x", padx=10, pady=10)

        ttk.Label(form, text="Title").grid(row=0, column=0, sticky="w")
        self.title_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.title_var, width=40).grid(row=0, column=1, sticky="w")

        ttk.Label(form, text="Description").grid(row=1, column=0, sticky="w")
        self.desc_var = tk.StringVar()
        ttk.Entry(form, textvariable=self.desc_var, width=60).grid(row=1, column=1, sticky="w", columnspan=3)

        ttk.Label(form, text="Due Date").grid(row=0, column=2, sticky="e")
        self.due_var = tk.StringVar()
        self.date_entry = DateEntry(
            form,
            textvariable=self.due_var,
            width=15,
            date_pattern="yyyy-mm-dd",
            state="readonly",
            showweeknumbers=False,
            mindate=date(1900, 1, 1),
        )
        self.date_entry.grid(row=0, column=3, sticky="w")

        self.no_due_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form, text="No due date", variable=self.no_due_var, command=self._toggle_due).grid(
            row=0, column=4, sticky="w", padx=(6, 0)
        )

        ttk.Label(form, text="Priority").grid(row=0, column=5, sticky="e")
        self.pri_var = tk.StringVar(value="medium")
        ttk.Combobox(form, textvariable=self.pri_var, values=list(PRIORITIES), state="readonly", width=10).grid(
            row=0, column=6, sticky="w"
        )

        ttk.Label(form, text="Status").grid(row=0, column=7, sticky="e")
        self.status_var = tk.StringVar(value="pending")
        ttk.Combobox(form, textvariable=self.status_var, values=list(STATUSES), state="readonly", width=12).grid(
            row=0, column=8, sticky="w"
        )

        ttk.Button(form, text="Add Task", command=self.add_task).grid(row=0, column=9, padx=6)
        ttk.Button(form, text="Update Selected", command=self.update_selected).grid(row=1, column=9, padx=6, sticky="e")

        tools = ttk.Frame(self, padding=(10, 0))
        tools.pack(fill="x")
        ttk.Label(tools, text="Search").pack(side="left")
        self.search_var = tk.StringVar()
        ttk.Entry(tools, textvariable=self.search_var, width=30).pack(side="left", padx=6)
        ttk.Button(tools, text="Go", command=self.search_tasks).pack(side="left")
        ttk.Button(tools, text="Show All", command=self._populate).pack(side="left", padx=6)

        ttk.Label(tools, text="Filter:").pack(side="left", padx=(20, 0))
        self.filter_status = tk.StringVar(value="")
        self.filter_priority = tk.StringVar(value="")
        ttk.Combobox(tools, textvariable=self.filter_status, values=("",) + STATUSES, width=14, state="readonly").pack(
            side="left", padx=4
        )
        ttk.Combobox(tools, textvariable=self.filter_priority, values=("",) + PRIORITIES, width=10, state="readonly").pack(
            side="left", padx=4
        )
        ttk.Button(tools, text="Apply", command=self.apply_filters).pack(side="left", padx=6)

        columns = ("id", "title", "priority", "status", "due", "updated")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", selectmode="browse")
        for col, w in zip(columns, (60, 300, 100, 140, 140, 200)):
            self.tree.heading(col, text=col.title())
            self.tree.column(col, width=w, anchor="w", stretch=True)

        vsb = ttk.Scrollbar(self, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscroll=vsb.set)
        self.tree.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        vsb.pack(side="right", fill="y")

        bottom = ttk.Frame(self, padding=10)
        bottom.pack(fill="x")
        ttk.Button(bottom, text="Mark Completed", command=self.complete_selected).pack(side="left")
        ttk.Button(bottom, text="Delete", command=self.delete_selected).pack(side="left", padx=10)
        ttk.Button(bottom, text="Refresh", command=self._populate).pack(side="left", padx=10)

        self.bind("<Delete>", lambda e: self.delete_selected())
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _toggle_due(self):
        if self.no_due_var.get():
            self.due_var.set("")
            self.date_entry.configure(state="disabled")
        else:
            self.date_entry.configure(state="readonly")
            try:
                self.date_entry.set_date(date.today())
            except Exception:
                pass

    def _on_select(self, event=None):
        item = self._selected_task()
        if not item:
            return
        t = self.store.get(item["id"])
        self.title_var.set(t.title)
        self.desc_var.set(t.description)
        if t.due_date:
            self.no_due_var.set(False)
            self.date_entry.configure(state="readonly")
            try:
                self.date_entry.set_date(t.due_date)
            except Exception:
                self.due_var.set(t.due_date)
        else:
            self.no_due_var.set(True)
            self._toggle_due()
        self.pri_var.set(t.priority)
        self.status_var.set(t.status)

    def _selected_task(self):
        sel = self.tree.selection()
        if not sel:
            return None
        vals = self.tree.item(sel[0], "values")
        return {"id": int(vals[0])}

    def _populate(self, items: Optional[List['Task']] = None):
        for row in self.tree.get_children():
            self.tree.delete(row)
        items = items or self.store.filtered()
        for i, t in enumerate(items):
            tag = "evenrow" if i % 2 == 0 else "oddrow"
            if t.status == "completed":
                tag = "completed"
            self.tree.insert(
                "", "end",
                values=(t.id, t.title, t.priority, t.status, t.due_date or "-", t.updated_at),
                tags=(tag,),
            )
        self.tree.tag_configure("evenrow", background="#f9f9f9")
        self.tree.tag_configure("oddrow", background="#ffffff")
        self.tree.tag_configure("completed", background="#e6f4ea")

    def add_task(self):
        title = self.title_var.get().strip()
        if not title:
            messagebox.showwarning("Title Required", "Please enter a title")
            return
        if self.no_due_var.get():
            due = None
        else:
            due = self.due_var.get().strip() or None
        t = self.store.add(title, self.desc_var.get().strip(), due, self.pri_var.get())
        t.update(status=self.status_var.get())
        self.store.save()
        self._populate()
        self._clear_form()

    def update_selected(self):
        item = self._selected_task()
        if not item:
            messagebox.showinfo("Select Task", "Pick a task to update")
            return
        t = self.store.get(item["id"])
        if self.no_due_var.get():
            due = None
        else:
            due = self.due_var.get().strip() or None
        t.update(
            title=self.title_var.get().strip() or t.title,
            description=self.desc_var.get().strip(),
            due_date=due,
            priority=self.pri_var.get(),
            status=self.status_var.get(),
        )
        self.store.save()
        self._populate()

    def complete_selected(self):
        item = self._selected_task()
        if not item:
            messagebox.showinfo("Select Task", "Pick a task to mark completed")
            return
        t = self.store.get(item["id"])
        t.update(status="completed")
        self.store.save()
        self._populate()

    def delete_selected(self):
        item = self._selected_task()
        if not item:
            messagebox.showinfo("Select Task", "Pick a task to delete")
            return
        if messagebox.askyesno("Confirm Delete", "Delete selected task?"):
            self.store.delete(item["id"])
            self._populate()
            self._clear_form()

    def search_tasks(self):
        q = self.search_var.get().strip()
        if not q:
            self._populate()
            return
        self._populate(self.store.search(q))

    def apply_filters(self):
        status = self.filter_status.get() or None
        priority = self.filter_priority.get() or None
        self._populate(self.store.filtered(status=status, priority=priority))

    def _clear_form(self):
        self.title_var.set("")
        self.desc_var.set("")
        self.no_due_var.set(False)
        self.date_entry.configure(state="readonly")
        try:
            self.date_entry.set_date(date.today())
        except Exception:
            self.due_var.set("")
        self.pri_var.set("medium")
        self.status_var.set("pending")

if __name__ == "__main__":
    App().mainloop()
