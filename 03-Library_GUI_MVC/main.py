import json
import sys
import time
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple, Iterable, Set

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, simpledialog

# -----------------------
# Model
# -----------------------

STATUSES: Tuple[str, ...] = ("available", "lent out", "missing", "deleted")


@dataclass
class Book:
    id: int
    title: str
    author: str
    year: str
    status: str = "available"


class Library:
    def __init__(self) -> None:
        self.books: Dict[int, Book] = {}
        self.next_id: int = 1

    def count(self) -> int:
        return len(self.books)

    def add_book(self, title: str, author: str, year: str, status: str) -> Book:
        status_l = status.strip().lower()
        if status_l not in STATUSES:
            raise ValueError(f"Invalid status: {status}")
        if not year.isdigit() or len(year) not in (2, 4):
            raise ValueError("Year must be numeric (2 or 4 digits)")
        book = Book(id=self.next_id, title=title.strip(), author=author.strip(), year=year.strip(), status=status_l)
        self.books[book.id] = book
        self.next_id += 1
        return book

    def set_status(self, book_id: int, status: str) -> None:
        status_l = status.strip().lower()
        if status_l not in STATUSES:
            raise ValueError(f"Invalid status: {status}")
        book = self.books.get(book_id)
        if not book:
            raise KeyError(f"Book id {book_id} not found")
        book.status = status_l

    def mark_deleted(self, book_id: int) -> None:
        self.set_status(book_id, "deleted")

    def hard_delete(self, book_id: int) -> None:
        if book_id in self.books:
            del self.books[book_id]
        else:
            raise KeyError(f"Book id {book_id} not found")

    def search(
        self,
        title: Optional[str] = None,
        author: Optional[str] = None,
        year: Optional[str] = None,
        include_statuses: Optional[Set[str]] = None,
        exclude_statuses: Optional[Set[str]] = None,
    ) -> Dict[int, Book]:
        t = (title or "").strip().lower()
        a = (author or "").strip().lower()
        y = (year or "").strip().lower()
        inc = {s.lower() for s in include_statuses} if include_statuses else None
        exc = {s.lower() for s in exclude_statuses} if exclude_statuses else set()

        out: Dict[int, Book] = {}
        for bid, b in self.books.items():
            if t and t not in b.title.lower():
                continue
            if a and a not in b.author.lower():
                continue
            if y and y not in b.year.lower():
                continue
            if inc is not None and b.status.lower() not in inc:
                continue
            if b.status.lower() in exc:
                continue
            out[bid] = b
        return out

    def to_json_obj(self) -> dict:
        # Store as a mapping of id->book plus next_id
        return {
            "next_id": self.next_id,
            "books": {str(bid): asdict(b) for bid, b in self.books.items()},
        }

    def load_json_obj(self, data: dict) -> None:
        # Supports both new format and old flat {id:book} format
        if "books" in data and "next_id" in data:
            self.books = {}
            for k, v in data["books"].items():
                bid = int(k)
                self.books[bid] = Book(
                    id=bid,
                    title=v.get("title", ""),
                    author=v.get("author", ""),
                    year=str(v.get("year", "")),
                    status=v.get("status", "available").lower(),
                )
            self.next_id = int(data["next_id"])
        else:
            # Old format: dict[str/int] -> {title, author, year, status}
            self.books = {}
            max_id = 0
            for k, v in data.items():
                try:
                    bid = int(k)
                except Exception:
                    continue
                self.books[bid] = Book(
                    id=bid,
                    title=v.get("title", ""),
                    author=v.get("author", ""),
                    year=str(v.get("year", "")),
                    status=v.get("status", "available").lower(),
                )
                max_id = max(max_id, bid)
            self.next_id = max_id + 1

    def clear(self) -> None:
        self.books.clear()
        self.next_id = 1


# -----------------------
# Utilities
# -----------------------

ADJ = ["Dusk", "Dawn", "Ancient", "Lost", "Sacred", "Salvation"]
NOUN = ["Empress", "Roy", "Paris", "Frankfurt", "Munich", "Deggendorf", "Berlin", "Garry", "Berry"]
THEMES = ["Sun", "Moon", "Destiny", "Mars", "Neptune", "Winter", "Summer", "Time", "Abyss", "Hole", "End", "Start", "Middle", "Ground", "Sea", "Ocean"]

FIRST_NAMES = ["Rey", "Key", "Garry", "Frow", "Grpw", "Arrow", "Aron", "Baron", "Ron", "Roney"]
LAST_NAMES = ["Jerrey", "Kein", "Garry", "Frow", "Grpw", "Arrow", "Aron", "Baron", "Ron", "Roney"]


def rand_title(rng) -> str:
    return f"{rng.choice(ADJ)} in {rng.choice(NOUN)} of the {rng.choice(THEMES)}"


def rand_author(rng) -> str:
    return f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}"


def rand_year(rng) -> str:
    return str(rng.randint(1900, 2025))


def rand_status(rng) -> str:
    return rng.choice(list(STATUSES))


# -----------------------
# View/Controller (Tk App)
# -----------------------

class LibraryApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Library Management System v2.0")
        self.root.geometry("520x420")

        self.library = Library()

        # UI: Header
        ttk.Label(self.root, text="Main Menu", font=("Georgia", 16)).place(relx=0.5, rely=0.12, anchor=tk.CENTER)

        # UI: Buttons
        btn_font = ("Georgia", 13)
        ttk.Button(self.root, text="Add New Book", command=self.add_book_dialog).place(relx=0.5, rely=0.30, anchor=tk.CENTER)
        ttk.Button(self.root, text="Delete (Mark Deleted)", command=self.delete_book_dialog).place(relx=0.5, rely=0.44, anchor=tk.CENTER)
        ttk.Button(self.root, text="Lend / Receive / Search", command=self.open_list_window).place(relx=0.5, rely=0.58, anchor=tk.CENTER)
        ttk.Button(self.root, text="Generate Books", command=self.open_generate_window).place(relx=0.5, rely=0.72, anchor=tk.CENTER)
        ttk.Button(self.root, text="About", command=self.about_dialog).place(relx=0.5, rely=0.86, anchor=tk.CENTER)

        # Book count
        self.count_var = tk.StringVar(value="Current Book Count: 0")
        ttk.Label(self.root, textvariable=self.count_var, font=("Georgia", 11)).place(relx=0.03, rely=0.96, anchor=tk.SW)

        # Menu bar
        menubar = tk.Menu(self.root)
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="New", command=self.new_library)
        file_menu.add_command(label="Open...", command=self.open_library)
        file_menu.add_command(label="Save As...", command=self.save_library)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.about_dialog)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # -------------
    # Basic helpers
    # -------------
    def refresh_count(self) -> None:
        self.count_var.set(f"Current Book Count: {self.library.count()}")

    def new_library(self) -> None:
        if messagebox.askyesno("Confirm", "Clear the current library?"):
            self.library.clear()
            self.refresh_count()

    def open_library(self) -> None:
        path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.library.load_json_obj(data)
            messagebox.showinfo("Loaded", "Library loaded successfully.")
            self.refresh_count()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load library: {e}")

    def save_library(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.library.to_json_obj(), f, indent=2)
            messagebox.showinfo("Saved", "Library saved successfully.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save library: {e}")

    # -------------
    # Dialogs
    # -------------
    def about_dialog(self) -> None:
        top = tk.Toplevel(self.root)
        top.title("About")
        top.geometry("360x220")
        ttk.Label(top, text="Library Management System", font=("Georgia", 14)).pack(pady=10)
        ttk.Label(top, text="Version: 2.0", font=("Georgia", 11)).pack(pady=4)
        ttk.Label(top, text="Created by:\nRownak Deb Kabya & Marcos Blanco-Leon", font=("Georgia", 10), justify="center").pack(pady=8)
        ttk.Label(top, text="THD", font=("Georgia", 10)).pack(pady=4)
        ttk.Button(top, text="Close", command=top.destroy).pack(pady=8)

    def add_book_dialog(self) -> None:
        top = tk.Toplevel(self.root)
        top.title("Add New Book")
        top.geometry("320x300")

        ttk.Label(top, text="Title:").pack(pady=(12, 2))
        title_e = ttk.Entry(top, width=35)
        title_e.pack()

        ttk.Label(top, text="Author:").pack(pady=(10, 2))
        author_e = ttk.Entry(top, width=35)
        author_e.pack()

        ttk.Label(top, text="Year:").pack(pady=(10, 2))
        year_e = ttk.Entry(top, width=35)
        year_e.pack()

        ttk.Label(top, text="Status:").pack(pady=(10, 2))
        status_cb = ttk.Combobox(top, values=list(STATUSES), state="readonly", width=32)
        status_cb.set("available")
        status_cb.pack()

        def on_save():
            title = title_e.get().strip()
            author = author_e.get().strip()
            year = year_e.get().strip()
            status = status_cb.get().strip().lower()
            if not title or not author or not year:
                messagebox.showerror("Error", "All fields are required.")
                return
            try:
                self.library.add_book(title, author, year, status)
                self.refresh_count()
                messagebox.showinfo("Success", f"Book '{title}' added.")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(top, text="Save", command=on_save).pack(pady=16)

    def delete_book_dialog(self) -> None:
        top = tk.Toplevel(self.root)
        top.title("Delete (Mark Deleted)")
        top.geometry("320x180")

        ttk.Label(top, text="Enter Book ID to mark as deleted:").pack(pady=(16, 6))
        id_e = ttk.Entry(top, width=20)
        id_e.pack()

        def on_delete():
            try:
                bid = int(id_e.get().strip())
                self.library.mark_deleted(bid)
                self.refresh_count()
                messagebox.showinfo("Deleted", f"Book {bid} marked as deleted.")
                top.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(top, text="Mark Deleted", command=on_delete).pack(pady=12)

    # -------------
    # List/Search/Lend-Receive
    # -------------
    def open_list_window(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("Library")
        win.geometry("900x560")

        # Toolbar
        toolbar = ttk.Frame(win)
        toolbar.pack(fill=tk.X, pady=4)

        ttk.Button(toolbar, text="Search / Filter", command=lambda: self.search_dialog(win)).pack(side=tk.LEFT, padx=4)
        ttk.Button(toolbar, text="Refresh", command=lambda: self.populate_tree(win)).pack(side=tk.LEFT, padx=4)

        # Treeview
        columns = ("id", "title", "author", "year", "status")
        tree = ttk.Treeview(win, columns=columns, show="headings", height=18)
        tree.heading("id", text="ID")
        tree.heading("title", text="Title")
        tree.heading("author", text="Author")
        tree.heading("year", text="Year")
        tree.heading("status", text="Status")

        tree.column("id", width=60, anchor=tk.CENTER)
        tree.column("title", width=360)
        tree.column("author", width=200)
        tree.column("year", width=80, anchor=tk.CENTER)
        tree.column("status", width=120, anchor=tk.CENTER)

        vsb = ttk.Scrollbar(win, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Status line
        status_var = tk.StringVar(value="")
        status_lbl = ttk.Label(win, textvariable=status_var)
        status_lbl.pack(side=tk.BOTTOM, anchor=tk.W, padx=8, pady=4)

        win._tree = tree
        win._status_var = status_var
        win._current_filter = dict(title="", author="", year="", include=None, exclude={"deleted"})  # default: exclude deleted

        def on_double_click(event):
            sel = tree.selection()
            if not sel:
                return
            try:
                item = sel[0]
                bid = int(tree.item(item, "values")[0])
            except Exception:
                return
            new_status = simpledialog.askstring(
                "Change Status",
                f"Enter new status for book {bid} ({', '.join(STATUSES)}):",
                parent=win,
            )
            if not new_status:
                return
            try:
                self.library.set_status(bid, new_status.strip().lower())
                self.refresh_count()
                self.populate_tree(win)  # refresh
                messagebox.showinfo("Success", "Status updated.")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tree.bind("<Double-1>", on_double_click)
        self.populate_tree(win)

    def populate_tree(self, win: tk.Toplevel, cap: int = 10000) -> None:
        tree: ttk.Treeview = win._tree  # type: ignore
        status_var: tk.StringVar = win._status_var  # type: ignore
        filt = win._current_filter  # type: ignore

        for item in tree.get_children():
            tree.delete(item)

        include = set(filt["include"]) if filt.get("include") else None
        exclude = set(filt.get("exclude") or set())

        results = self.library.search(
            title=filt.get("title"),
            author=filt.get("author"),
            year=filt.get("year"),
            include_statuses=include,
            exclude_statuses=exclude,
        )
        total = len(results)
        shown = 0

        # Insert in batches to keep UI responsive
        items = list(results.values())
        items.sort(key=lambda b: b.id)

        batch = 1000
        idx = 0

        def insert_batch():
            nonlocal idx, shown
            end = min(idx + batch, len(items))
            for b in items[idx:end]:
                if shown >= cap:
                    break
                tree.insert("", tk.END, values=(b.id, b.title, b.author, b.year, b.status))
                shown += 1
            idx = end
            if shown >= cap or idx >= len(items):
                status_var.set(f"Showing {shown} of {total} result(s).")
                return
            win.after(5, insert_batch)

        insert_batch()

    def search_dialog(self, parent: tk.Toplevel) -> None:
        top = tk.Toplevel(parent)
        top.title("Search / Filter")
        top.geometry("380x360")

        ttk.Label(top, text="Title contains:").pack(pady=(12, 2))
        title_e = ttk.Entry(top, width=40)
        title_e.pack()

        ttk.Label(top, text="Author contains:").pack(pady=(10, 2))
        author_e = ttk.Entry(top, width=40)
        author_e.pack()

        ttk.Label(top, text="Year contains:").pack(pady=(10, 2))
        year_e = ttk.Entry(top, width=40)
        year_e.pack()

        ttk.Label(top, text="Include statuses (leave none to include all):").pack(pady=(14, 6))
        include_vars: Dict[str, tk.IntVar] = {}
        inc_frame = ttk.Frame(top)
        inc_frame.pack()
        for s in STATUSES:
            v = tk.IntVar(value=0)
            include_vars[s] = v
            ttk.Checkbutton(inc_frame, text=s, variable=v).pack(side=tk.LEFT, padx=4)

        ttk.Label(top, text="Exclude statuses:").pack(pady=(14, 6))
        exclude_vars: Dict[str, tk.IntVar] = {}
        exc_frame = ttk.Frame(top)
        exc_frame.pack()
        # Default exclude deleted
        for s in STATUSES:
            v = tk.IntVar(value=1 if s == "deleted" else 0)
            exclude_vars[s] = v
            ttk.Checkbutton(exc_frame, text=s, variable=v).pack(side=tk.LEFT, padx=4)

        def apply_search():
            include = {s for s, v in include_vars.items() if v.get() == 1}
            exclude = {s for s, v in exclude_vars.items() if v.get() == 1}
            # If no include selections, include is None => include all
            filt = dict(
                title=title_e.get().strip(),
                author=author_e.get().strip(),
                year=year_e.get().strip(),
                include=include if include else None,
                exclude=exclude if exclude else None,
            )
            parent._current_filter = filt  # type: ignore
            self.populate_tree(parent)
            top.destroy()

        ttk.Button(top, text="Apply", command=apply_search).pack(pady=18)

    # -------------
    # Generate
    # -------------
    def open_generate_window(self) -> None:
        top = tk.Toplevel(self.root)
        top.title("Generate Books")
        top.geometry("400x240")

        ttk.Label(top, text="Generate random books").pack(pady=(16, 4))

        ttk.Label(top, text="How many books? (max 1,000,000)").pack(pady=(10, 2))
        count_e = ttk.Entry(top, width=20)
        count_e.insert(0, "1000000")
        count_e.pack()

        pb = ttk.Progressbar(top, orient=tk.HORIZONTAL, length=300, mode="determinate", maximum=100)
        pb.pack(pady=16)

        info_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=info_var).pack()

        cancel_flag = {"cancel": False}
        added_ids: List[int] = []

        def do_cancel():
            cancel_flag["cancel"] = True

        def start():
            n_str = count_e.get().strip().replace("_", "")
            if not n_str.isdigit():
                messagebox.showerror("Error", "Please enter a valid integer.")
                return
            n = int(n_str)
            if n <= 0 or n > 1_000_000:
                messagebox.showerror("Error", "Please enter a number between 1 and 1,000,000.")
                return

            start_btn.config(state=tk.DISABLED)
            cancel_btn.config(state=tk.NORMAL)
            info_var.set("Starting generation...")

            rng = __import__("random").Random()
            target = n
            batch = 2000
            created = 0

            def step():
                nonlocal created
                if cancel_flag["cancel"]:
                    # Roll back newly added items
                    for bid in added_ids:
                        try:
                            self.library.hard_delete(bid)
                        except KeyError:
                            pass
                    self.refresh_count()
                    pb["value"] = 0
                    info_var.set(f"Cancelled. Reverted {len(added_ids)} added book(s).")
                    start_btn.config(state=tk.NORMAL)
                    cancel_btn.config(state=tk.DISABLED)
                    return

                # Add a batch
                to_make = min(batch, target - created)
                for _ in range(to_make):
                    b = self.library.add_book(
                        title=rand_title(rng),
                        author=rand_author(rng),
                        year=rand_year(rng),
                        status=rand_status(rng),
                    )
                    added_ids.append(b.id)
                created += to_make

                # Progress
                pb["value"] = (created / target) * 100
                info_var.set(f"Generated {created}/{target}...")

                if created >= target:
                    self.refresh_count()
                    info_var.set("Done.")
                    start_btn.config(state=tk.NORMAL)
                    cancel_btn.config(state=tk.DISABLED)
                    return

                top.after(1, step)

            step()

        start_btn = ttk.Button(top, text="Start", command=start)
        start_btn.pack(pady=6)
        cancel_btn = ttk.Button(top, text="Cancel", command=do_cancel, state=tk.DISABLED)
        cancel_btn.pack()

        ttk.Button(top, text="Close", command=top.destroy).pack(pady=10)


def main():
    root = tk.Tk()
    # Use themed widgets
    try:
        ttk.Style().theme_use("clam")
    except Exception:
        pass
    app = LibraryApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()