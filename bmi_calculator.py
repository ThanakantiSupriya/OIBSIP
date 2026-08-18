import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

DB_PATH = "bmi_records.db"

INCHES_TO_METERS = 0.0254


# ---------------------------------------------------------------------------
# Database layer
# ---------------------------------------------------------------------------
class BMIDatabase:
    """Handles all SQLite read/write operations for BMI records."""

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _connect(self):
        return sqlite3.connect(self.db_path)

    def _init_db(self):
        try:
            with self._connect() as conn:
                conn.execute(
                    """
                    CREATE TABLE IF NOT EXISTS bmi_records (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT NOT NULL,
                        weight REAL NOT NULL,
                        height REAL NOT NULL,
                        bmi REAL NOT NULL,
                        category TEXT NOT NULL,
                        recorded_at TEXT NOT NULL
                    )
                    """
                )
                conn.commit()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not initialize database:\n{e}")
            raise

    def add_record(self, username, weight, height, bmi, category):
        try:
            with self._connect() as conn:
                conn.execute(
                    """INSERT INTO bmi_records
                       (username, weight, height, bmi, category, recorded_at)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (username, weight, height, bmi, category,
                     datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
                )
                conn.commit()
            return True
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not save record:\n{e}")
            return False

    def get_users(self):
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    "SELECT DISTINCT username FROM bmi_records ORDER BY username COLLATE NOCASE"
                )
                return [row[0] for row in cur.fetchall()]
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not read users:\n{e}")
            return []

    def get_history(self, username):
        try:
            with self._connect() as conn:
                cur = conn.execute(
                    """SELECT recorded_at, bmi, category, weight, height
                       FROM bmi_records WHERE username = ? ORDER BY recorded_at""",
                    (username,),
                )
                return cur.fetchall()
        except sqlite3.Error as e:
            messagebox.showerror("Database Error", f"Could not read history:\n{e}")
            return []


# ---------------------------------------------------------------------------
# BMI logic
# ---------------------------------------------------------------------------
def classify_bmi(bmi: float) -> str:
    if bmi < 18.5:
        return "Underweight"
    elif bmi < 25:
        return "Normal"
    elif bmi < 30:
        return "Overweight"
    else:
        return "Obese"


CATEGORY_COLORS = {
    "Underweight": "#3b82f6",  # blue
    "Normal": "#22c55e",       # green
    "Overweight": "#f59e0b",   # amber
    "Obese": "#ef4444",        # red
}


# ---------------------------------------------------------------------------
# GUI application
# ---------------------------------------------------------------------------
class BMIApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BMI Calculator - Advanced")
        self.geometry("460x520")
        self.resizable(False, False)
        self.configure(bg="#f3f4f6")

        self.db = BMIDatabase()

        self._build_input_section()
        self._build_result_section()
        self._build_history_section()

    # -- UI construction -----------------------------------------------
    def _build_input_section(self):
        frame = tk.Frame(self, bg="#f3f4f6", padx=20, pady=20)
        frame.pack(fill="x")

        tk.Label(frame, text="BMI Calculator", font=("Segoe UI", 18, "bold"),
                  bg="#f3f4f6").grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(frame, text="Name:", bg="#f3f4f6", anchor="w").grid(
            row=1, column=0, sticky="w", pady=5)
        self.name_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.name_var, width=25).grid(
            row=1, column=1, pady=5)

        tk.Label(frame, text="Weight (kg):", bg="#f3f4f6", anchor="w").grid(
            row=2, column=0, sticky="w", pady=5)
        self.weight_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.weight_var, width=25).grid(
            row=2, column=1, pady=5)

        tk.Label(frame, text="Height (in):", bg="#f3f4f6", anchor="w").grid(
            row=3, column=0, sticky="w", pady=5)
        self.height_var = tk.StringVar()
        tk.Entry(frame, textvariable=self.height_var, width=25).grid(
            row=3, column=1, pady=5)

        tk.Button(frame, text="Calculate", command=self.calculate,
                  bg="#2563eb", fg="white", font=("Segoe UI", 11, "bold"),
                  activebackground="#1d4ed8", activeforeground="white",
                  relief="flat", padx=10, pady=6).grid(
            row=4, column=0, columnspan=2, pady=(15, 0), sticky="ew")

    def _build_result_section(self):
        self.result_frame = tk.Frame(self, bg="#e5e7eb", padx=20, pady=15)
        self.result_frame.pack(fill="x", padx=20)

        self.result_label = tk.Label(
            self.result_frame, text="Enter your details and click Calculate",
            font=("Segoe UI", 12), bg="#e5e7eb", wraplength=380, justify="center")
        self.result_label.pack()

    def _build_history_section(self):
        frame = tk.Frame(self, bg="#f3f4f6", padx=20, pady=15)
        frame.pack(fill="both", expand=True)

        tk.Label(frame, text="View History", font=("Segoe UI", 12, "bold"),
                  bg="#f3f4f6").grid(row=0, column=0, sticky="w")

        self.user_select_var = tk.StringVar()
        self.user_dropdown = ttk.Combobox(
            frame, textvariable=self.user_select_var, state="readonly", width=22)
        self.user_dropdown.grid(row=1, column=0, pady=8, sticky="w")
        self._refresh_user_list()

        tk.Button(frame, text="Show BMI Trend Graph", command=self.show_graph,
                  bg="#374151", fg="white", relief="flat", padx=8, pady=4).grid(
            row=1, column=1, padx=10)

    # -- behaviour --------------------------------------------------------
    def _refresh_user_list(self):
        users = self.db.get_users()
        self.user_dropdown["values"] = users
        if users and not self.user_select_var.get():
            self.user_select_var.set(users[0])

    def calculate(self):
        name = self.name_var.get().strip()
        weight_raw = self.weight_var.get().strip()
        height_raw = self.height_var.get().strip()

        if not name:
            self._show_error("Please enter a name.")
            return

        try:
            weight = float(weight_raw)
            height_in = float(height_raw)
        except ValueError:
            self._show_error("Weight and height must be numeric values.")
            return

        if weight <= 0 or height_in <= 0:
            self._show_error("Weight and height must be positive numbers.")
            return

        # Sanity-check the ranges so a value typed in the wrong unit
        # (e.g. meters like 1.75 typed into the inches field) is caught
        # instead of silently producing a nonsense BMI.
        if not (20 <= height_in <= 100):
            self._show_error(
                "Height must be in inches (e.g. 65), between 20 and 100."
            )
            return

        if not (20 <= weight <= 400):
            self._show_error(
                "Weight must be in kilograms, between 20 and 400."
            )
            return

        # Convert height from inches to meters for the BMI formula
        height_m = height_in * INCHES_TO_METERS

        bmi = round(weight / (height_m ** 2), 2)
        category = classify_bmi(bmi)
        color = CATEGORY_COLORS[category]

        self.result_frame.configure(bg=color)
        self.result_label.configure(
            bg=color, fg="white",
            text=f"{name}'s BMI: {bmi}\nCategory: {category}"
        )

        # Store the original height in inches, as entered
        saved = self.db.add_record(name, weight, height_in, bmi, category)
        if saved:
            self._refresh_user_list()
            self.user_select_var.set(name)

    def _show_error(self, message):
        self.result_frame.configure(bg="#e5e7eb")
        self.result_label.configure(bg="#e5e7eb", fg="#b91c1c", text=f"⚠ {message}")

    def show_graph(self):
        username = self.user_select_var.get()
        if not username:
            messagebox.showinfo("No user selected", "Please select a user first.")
            return

        history = self.db.get_history(username)
        if not history:
            messagebox.showinfo("No data", f"No BMI history found for {username}.")
            return

        dates = [row[0] for row in history]
        bmis = [row[1] for row in history]

        graph_win = tk.Toplevel(self)
        graph_win.title(f"BMI Trend - {username}")
        graph_win.geometry("640x480")

        fig = Figure(figsize=(6, 4.2), dpi=100)
        ax = fig.add_subplot(111)
        ax.plot(range(len(bmis)), bmis, marker="o", color="#2563eb", linewidth=2)
        ax.set_title(f"BMI Trend for {username}")
        ax.set_xlabel("Record #")
        ax.set_ylabel("BMI")
        ax.set_xticks(range(len(dates)))
        ax.set_xticklabels([d.split(" ")[0] for d in dates], rotation=45, ha="right", fontsize=8)
        ax.axhspan(18.5, 25, color="#22c55e", alpha=0.08)
        ax.grid(True, linestyle="--", alpha=0.4)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=graph_win)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)


if __name__ == "__main__":
    app = BMIApp()
    app.mainloop()