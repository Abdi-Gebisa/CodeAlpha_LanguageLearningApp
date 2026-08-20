import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import random

DB_NAME = "language_learning.db"

SAMPLE_WORDS = [
    ("Hello", "Akkam", "HEL-oh", "Vocabulary"),
    ("Good morning", "Akkam bulte", "gud MOR-ning", "Phrases"),
    ("Thank you", "Galatoomi", "THANK yoo", "Phrases"),
    ("Please", "Maaloo", "pleez", "Phrases"),
    ("Water", "Bishaan", "WAW-ter", "Vocabulary"),
    ("Food", "Nyaata", "food", "Vocabulary"),
    ("House", "Mana", "hows", "Vocabulary"),
    ("School", "Mana barumsaa", "skool", "Vocabulary"),
    ("Teacher", "Barsiisaa", "TEE-cher", "Vocabulary"),
    ("Student", "Barataa", "STOO-dent", "Vocabulary"),
    ("Book", "Kitaaba", "book", "Vocabulary"),
    ("Friend", "Hiriyyaa", "frend", "Vocabulary"),
    ("Family", "Maatii", "FAM-uh-lee", "Vocabulary"),
    ("How are you?", "Akkam jirta?", "how ar yoo", "Phrases"),
    ("I am fine", "Nagaan jira", "ai am fain", "Phrases"),
    ("What is your name?", "Maqaan kee eenyu?", "wot iz yor neym", "Phrases"),
    ("My name is...", "Maqaan koo...", "mai neym iz", "Phrases"),
    ("Yes", "Eeyyee", "yes", "Vocabulary"),
    ("No", "Lakki", "noh", "Vocabulary"),
    ("Today", "Har'a", "tuh-DEY", "Vocabulary"),
]

def connect():
    return sqlite3.connect(DB_NAME)

def setup_database():
    with connect() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS lessons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL,
                translation TEXT NOT NULL,
                pronunciation TEXT NOT NULL,
                category TEXT NOT NULL
            )
        """)
        con.execute("""
            CREATE TABLE IF NOT EXISTS progress (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                studied INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                total_quizzes INTEGER DEFAULT 0
            )
        """)
        row = con.execute("SELECT COUNT(*) FROM lessons").fetchone()
        if row[0] == 0:
            con.executemany(
                "INSERT INTO lessons(word, translation, pronunciation, category) VALUES (?, ?, ?, ?)",
                SAMPLE_WORDS
            )
        con.execute("INSERT OR IGNORE INTO progress(id, studied, correct, total_quizzes) VALUES (1,0,0,0)")

class LanguageLearningApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CodeAlpha Language Learning App")
        self.geometry("1050x700")
        self.minsize(900, 620)

        self.bg = "#F4F7FB"
        self.primary = "#3157D5"
        self.dark = "#17233C"
        self.card = "#FFFFFF"
        self.configure(bg=self.bg)

        self.current_index = 0
        self.flashcards = []
        self.answer_visible = False
        self.quiz_questions = []
        self.quiz_index = 0
        self.quiz_score = 0

        self.build_style()
        self.build_layout()
        self.load_flashcards()
        self.show_home()

    def build_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 11), padding=9)
        style.configure("Primary.TButton", font=("Segoe UI", 11, "bold"),
                        padding=10, foreground="white", background=self.primary)
        style.map("Primary.TButton", background=[("active", "#2545B0")])
        style.configure("TLabel", background=self.bg, foreground=self.dark)
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))

    def build_layout(self):
        header = tk.Frame(self, bg=self.dark, height=75)
        header.pack(fill="x")
        tk.Label(header, text="🌍 Language Learning App",
                 bg=self.dark, fg="white", font=("Segoe UI", 22, "bold")).pack(side="left", padx=25, pady=18)
        tk.Label(header, text="English ↔ Afaan Oromo",
                 bg=self.dark, fg="#D9E2FF", font=("Segoe UI", 11)).pack(side="right", padx=25)

        self.nav = tk.Frame(self, bg="white", height=55)
        self.nav.pack(fill="x")
        buttons = [
            ("🏠 Home", self.show_home),
            ("📚 Vocabulary", self.show_vocabulary),
            ("🃏 Flashcards", self.show_flashcards),
            ("📝 Quiz", self.show_quiz),
            ("📊 Progress", self.show_progress),
        ]
        for text, command in buttons:
            ttk.Button(self.nav, text=text, command=command).pack(side="left", padx=8, pady=9)

        self.content = tk.Frame(self, bg=self.bg)
        self.content.pack(fill="both", expand=True, padx=25, pady=20)

    def clear_content(self):
        for widget in self.content.winfo_children():
            widget.destroy()

    def title(self, text, subtitle=""):
        tk.Label(self.content, text=text, bg=self.bg, fg=self.dark,
                 font=("Segoe UI", 24, "bold")).pack(anchor="w")
        if subtitle:
            tk.Label(self.content, text=subtitle, bg=self.bg, fg="#5C6B82",
                     font=("Segoe UI", 11)).pack(anchor="w", pady=(3, 18))

    def card(self, parent, title, value, command=None):
        frame = tk.Frame(parent, bg=self.card, highlightbackground="#DDE3EE",
                         highlightthickness=1)
        frame.pack(side="left", fill="both", expand=True, padx=8, pady=8)
        tk.Label(frame, text=title, bg=self.card, fg="#64748B",
                 font=("Segoe UI", 11)).pack(pady=(20, 5))
        tk.Label(frame, text=value, bg=self.card, fg=self.primary,
                 font=("Segoe UI", 25, "bold")).pack(pady=(0, 20))
        if command:
            ttk.Button(frame, text="Open", command=command).pack(pady=(0, 15))

    def show_home(self):
        self.clear_content()
        self.title("Welcome 👋", "Learn useful English words and phrases with Afaan Oromo translations.")

        with connect() as con:
            words = con.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
            p = con.execute("SELECT studied, correct, total_quizzes FROM progress WHERE id=1").fetchone()

        stats = tk.Frame(self.content, bg=self.bg)
        stats.pack(fill="x")
        self.card(stats, "Learning Items", str(words), self.show_vocabulary)
        self.card(stats, "Cards Studied", str(p[0]), self.show_flashcards)
        self.card(stats, "Quiz Score", f"{p[1]}/{p[2]}" if p[2] else "0/0", self.show_quiz)

        box = tk.Frame(self.content, bg=self.card, highlightbackground="#DDE3EE", highlightthickness=1)
        box.pack(fill="x", pady=20, padx=8)
        tk.Label(box, text="How to use", bg=self.card, fg=self.dark,
                 font=("Segoe UI", 17, "bold")).pack(anchor="w", padx=20, pady=(18, 10))
        tips = [
            "1. Open Vocabulary to browse words and phrases.",
            "2. Use Flashcards to reveal translations and pronunciation.",
            "3. Take the Quiz to test your knowledge.",
            "4. Check Progress to see your learning statistics.",
        ]
        for tip in tips:
            tk.Label(box, text=tip, bg=self.card, fg="#475569",
                     font=("Segoe UI", 11)).pack(anchor="w", padx=25, pady=4)
        tk.Label(box, text="Tip: Review flashcards regularly to improve retention.",
                 bg=self.card, fg=self.primary, font=("Segoe UI", 11, "bold")).pack(
                     anchor="w", padx=25, pady=(12, 20))

    def show_vocabulary(self):
        self.clear_content()
        self.title("Vocabulary & Phrases", "Browse learning items by category.")

        toolbar = tk.Frame(self.content, bg=self.bg)
        toolbar.pack(fill="x", pady=(0, 10))
        tk.Label(toolbar, text="Category:", bg=self.bg, font=("Segoe UI", 11)).pack(side="left")
        category = ttk.Combobox(toolbar, values=["All", "Vocabulary", "Phrases", "Grammar"],
                                state="readonly", width=15)
        category.set("All")
        category.pack(side="left", padx=8)
        ttk.Button(toolbar, text="Add Item", command=self.add_item).pack(side="right")

        tree_frame = tk.Frame(self.content, bg="white")
        tree_frame.pack(fill="both", expand=True)
        columns = ("id", "word", "translation", "pronunciation", "category")
        tree = ttk.Treeview(tree_frame, columns=columns, show="headings")
        headings = {"id":"ID", "word":"English", "translation":"Afaan Oromo",
                    "pronunciation":"Pronunciation", "category":"Category"}
        widths = {"id":50, "word":180, "translation":220, "pronunciation":190, "category":120}
        for col in columns:
            tree.heading(col, text=headings[col])
            tree.column(col, width=widths[col], anchor="center")
        scroll = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scroll.set)
        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        def refresh(*_):
            for item in tree.get_children():
                tree.delete(item)
            selected = category.get()
            with connect() as con:
                if selected == "All":
                    rows = con.execute("SELECT id,word,translation,pronunciation,category FROM lessons ORDER BY id").fetchall()
                else:
                    rows = con.execute(
                        "SELECT id,word,translation,pronunciation,category FROM lessons WHERE category=? ORDER BY id",
                        (selected,)).fetchall()
            for row in rows:
                tree.insert("", "end", values=row)

        def edit_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select item", "Please select an item first.")
                return
            data = tree.item(selected[0], "values")
            self.edit_item(data)

        def delete_selected():
            selected = tree.selection()
            if not selected:
                messagebox.showwarning("Select item", "Please select an item first.")
                return
            item_id = tree.item(selected[0], "values")[0]
            if messagebox.askyesno("Delete", "Delete this learning item?"):
                with connect() as con:
                    con.execute("DELETE FROM lessons WHERE id=?", (item_id,))
                refresh()
                self.load_flashcards()

        category.bind("<<ComboboxSelected>>", refresh)
        actions = tk.Frame(self.content, bg=self.bg)
        actions.pack(fill="x", pady=10)
        ttk.Button(actions, text="Edit Selected", command=edit_selected).pack(side="left", padx=5)
        ttk.Button(actions, text="Delete Selected", command=delete_selected).pack(side="left", padx=5)
        refresh()

    def add_item(self):
        self.item_form("Add Learning Item")

    def edit_item(self, data):
        self.item_form("Edit Learning Item", data)

    def item_form(self, heading, data=None):
        win = tk.Toplevel(self)
        win.title(heading)
        win.geometry("450x400")
        win.configure(bg=self.bg)
        win.transient(self)
        win.grab_set()

        tk.Label(win, text=heading, bg=self.bg, fg=self.dark,
                 font=("Segoe UI", 18, "bold")).pack(pady=20)

        labels = ["English word/phrase", "Afaan Oromo translation", "Pronunciation", "Category"]
        entries = []
        for label in labels[:3]:
            tk.Label(win, text=label, bg=self.bg, font=("Segoe UI", 10)).pack(anchor="w", padx=35)
            e = ttk.Entry(win, width=45)
            e.pack(padx=35, pady=(3, 12))
            entries.append(e)

        tk.Label(win, text="Category", bg=self.bg, font=("Segoe UI", 10)).pack(anchor="w", padx=35)
        combo = ttk.Combobox(win, values=["Vocabulary", "Phrases", "Grammar"],
                             state="readonly", width=42)
        combo.set("Vocabulary")
        combo.pack(padx=35, pady=(3, 15))

        if data:
            entries[0].insert(0, data[1])
            entries[1].insert(0, data[2])
            entries[2].insert(0, data[3])
            combo.set(data[4])

        def save():
            vals = [e.get().strip() for e in entries]
            if not all(vals):
                messagebox.showwarning("Missing data", "Please complete all fields.")
                return
            if data:
                with connect() as con:
                    con.execute("""UPDATE lessons SET word=?, translation=?, pronunciation=?, category=?
                                   WHERE id=?""", (*vals, combo.get(), data[0]))
            else:
                with connect() as con:
                    con.execute("""INSERT INTO lessons(word,translation,pronunciation,category)
                                   VALUES (?,?,?,?)""", (*vals, combo.get()))
            win.destroy()
            self.load_flashcards()
            self.show_vocabulary()

        ttk.Button(win, text="Save", style="Primary.TButton", command=save).pack(pady=10)

    def load_flashcards(self):
        with connect() as con:
            self.flashcards = con.execute(
                "SELECT id,word,translation,pronunciation,category FROM lessons ORDER BY id"
            ).fetchall()
        if self.flashcards:
            self.current_index %= len(self.flashcards)
        else:
            self.current_index = 0

    def show_flashcards(self):
        self.clear_content()
        self.title("Flashcards", "Study a card, reveal the translation, then move to the next one.")
        self.load_flashcards()
        if not self.flashcards:
            tk.Label(self.content, text="No flashcards available.", bg=self.bg,
                     font=("Segoe UI", 14)).pack(pady=50)
            return

        self.answer_visible = False
        card = self.flashcards[self.current_index]
        box = tk.Frame(self.content, bg=self.card, highlightbackground="#DDE3EE", highlightthickness=1)
        box.pack(fill="both", expand=True, padx=100, pady=10)

        tk.Label(box, text=f"Card {self.current_index + 1} of {len(self.flashcards)}",
                 bg=self.card, fg="#64748B", font=("Segoe UI", 11)).pack(pady=(25, 5))
        tk.Label(box, text=card[1], bg=self.card, fg=self.dark,
                 font=("Segoe UI", 32, "bold"), wraplength=700).pack(pady=20)

        self.answer_label = tk.Label(box, text="••••••••", bg=self.card, fg=self.primary,
                                     font=("Segoe UI", 23, "bold"), wraplength=700)
        self.answer_label.pack(pady=10)

        self.pron_label = tk.Label(box, text="", bg=self.card, fg="#64748B",
                                   font=("Segoe UI", 12))
        self.pron_label.pack(pady=5)

        tk.Label(box, text=f"Category: {card[4]}", bg=self.card, fg="#64748B",
                 font=("Segoe UI", 10)).pack(pady=5)

        controls = tk.Frame(box, bg=self.card)
        controls.pack(pady=25)
        ttk.Button(controls, text="◀ Previous", command=self.previous_card).pack(side="left", padx=8)
        ttk.Button(controls, text="Show Answer", style="Primary.TButton",
                   command=self.show_answer).pack(side="left", padx=8)
        ttk.Button(controls, text="Next ▶", command=self.next_card).pack(side="left", padx=8)

    def show_answer(self):
        if not self.flashcards:
            return
        card = self.flashcards[self.current_index]
        self.answer_visible = True
        self.answer_label.config(text=card[2])
        self.pron_label.config(text=f"Pronunciation: {card[3]}")
        with connect() as con:
            con.execute("UPDATE progress SET studied = studied + 1 WHERE id=1")

    def next_card(self):
        if not self.flashcards:
            return
        self.current_index = (self.current_index + 1) % len(self.flashcards)
        self.show_flashcards()

    def previous_card(self):
        if not self.flashcards:
            return
        self.current_index = (self.current_index - 1) % len(self.flashcards)
        self.show_flashcards()

    def show_quiz(self):
        self.clear_content()
        self.title("Practice Quiz", "Choose the Afaan Oromo translation for the English word or phrase.")

        with connect() as con:
            rows = con.execute("SELECT word,translation FROM lessons").fetchall()

        if len(rows) < 2:
            tk.Label(self.content, text="Add at least two learning items to start a quiz.",
                     bg=self.bg, font=("Segoe UI", 13)).pack(pady=50)
            return

        self.quiz_questions = random.sample(rows, min(10, len(rows)))
        self.quiz_index = 0
        self.quiz_score = 0
        self.render_quiz_question()

    def render_quiz_question(self):
        for widget in self.content.winfo_children():
            if widget != None:
                widget.destroy()

        question = self.quiz_questions[self.quiz_index]
        correct = question[1]
        all_answers = list({r[1] for r in self.quiz_questions})
        while len(all_answers) < 4:
            all_answers.append(correct)
            all_answers = list(dict.fromkeys(all_answers))
        options = random.sample(all_answers, min(4, len(all_answers)))
        if correct not in options:
            options[0] = correct
            random.shuffle(options)

        box = tk.Frame(self.content, bg=self.card, highlightbackground="#DDE3EE", highlightthickness=1)
        box.pack(fill="both", expand=True, padx=100, pady=10)
        tk.Label(box, text=f"Question {self.quiz_index+1} of {len(self.quiz_questions)}",
                 bg=self.card, fg="#64748B", font=("Segoe UI", 11)).pack(pady=(35, 10))
        tk.Label(box, text=question[0], bg=self.card, fg=self.dark,
                 font=("Segoe UI", 30, "bold"), wraplength=700).pack(pady=20)
        tk.Label(box, text="Select the correct translation:",
                 bg=self.card, fg="#475569", font=("Segoe UI", 12)).pack(pady=5)

        for option in options:
            ttk.Button(box, text=option, command=lambda x=option: self.answer_quiz(x, correct)
                       ).pack(fill="x", padx=170, pady=7)

    def answer_quiz(self, selected, correct):
        if selected == correct:
            self.quiz_score += 1
            messagebox.showinfo("Correct!", "Excellent! Your answer is correct.")
        else:
            messagebox.showerror("Incorrect", f"The correct answer is:\n{correct}")

        self.quiz_index += 1
        if self.quiz_index >= len(self.quiz_questions):
            with connect() as con:
                con.execute("""UPDATE progress
                               SET correct = correct + ?, total_quizzes = total_quizzes + ?
                               WHERE id=1""", (self.quiz_score, len(self.quiz_questions)))
            messagebox.showinfo("Quiz Complete",
                                f"You scored {self.quiz_score}/{len(self.quiz_questions)}.")
            self.show_progress()
        else:
            self.render_quiz_question()

    def show_progress(self):
        self.clear_content()
        self.title("Learning Progress", "Track your study activity and quiz performance.")

        with connect() as con:
            words = con.execute("SELECT COUNT(*) FROM lessons").fetchone()[0]
            studied, correct, total = con.execute(
                "SELECT studied, correct, total_quizzes FROM progress WHERE id=1"
            ).fetchone()

        percent = round((correct / total) * 100) if total else 0
        stats = tk.Frame(self.content, bg=self.bg)
        stats.pack(fill="x")
        self.card(stats, "Learning Items", str(words))
        self.card(stats, "Cards Studied", str(studied))
        self.card(stats, "Quiz Accuracy", f"{percent}%")

        box = tk.Frame(self.content, bg=self.card, highlightbackground="#DDE3EE", highlightthickness=1)
        box.pack(fill="x", padx=8, pady=25)
        tk.Label(box, text="Your Progress", bg=self.card, fg=self.dark,
                 font=("Segoe UI", 18, "bold")).pack(anchor="w", padx=20, pady=(20, 10))
        ttk.Progressbar(box, maximum=100, value=percent, length=700).pack(padx=20, pady=10)
        tk.Label(box, text=f"Quiz answers: {correct} correct out of {total}",
                 bg=self.card, fg="#475569", font=("Segoe UI", 11)).pack(anchor="w", padx=20, pady=(5, 20))
        ttk.Button(box, text="Take Another Quiz", command=self.show_quiz).pack(padx=20, pady=(0, 20), anchor="w")

if __name__ == "__main__":
    setup_database()
    app = LanguageLearningApp()
    app.mainloop()
