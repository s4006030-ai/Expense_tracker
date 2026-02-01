import os


from flask import Flask, render_template, request, redirect
import sqlite3
from datetime import date






def get_db():
    return sqlite3.connect("expense.db")

def create_tables():
    conn = get_db()
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY,
        amount REAL,
        paid_by TEXT,
        description TEXT,
        date TEXT,
        month TEXT
    )
    """)

    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.executemany(
            "INSERT INTO users (name) VALUES (?)",
            [("Rohit",), ("Friend1",), ("Friend2",)]
        )

    conn.commit()
    conn.close()

create_tables()
app=Flask(__name__)
@app.route("/")
def index():
    conn = get_db()
    cur = conn.cursor()

    current_month = date.today().strftime("%Y-%m")
    cur.execute("SELECT * FROM expenses WHERE month=?", (current_month,))
    expenses = cur.fetchall()

    cur.execute("SELECT name FROM users")
    users = [u[0] for u in cur.fetchall()]

    total = sum(e[1] for e in expenses)
    share = round(total / len(users), 2) if users else 0

    paid = {u: 0 for u in users}
    for e in expenses:
        paid[e[2]] += e[1]

    balance = {u: round(paid[u] - share, 2) for u in users}

    conn.close()
    return render_template("index.html", expenses=expenses, total=total, share=share, balance=balance)
app=Flask(__name__)
@app.route("/add", methods=["GET","POST"])
def add_expense():
    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT name FROM users")
    users = [u[0] for u in cur.fetchall()]

    if request.method == "POST":
        amount = float(request.form["amount"])
        paid_by = request.form["paid_by"]
        desc = request.form["description"]
        today = date.today().strftime("%d-%m-%Y")
        month = date.today().strftime("%Y-%m")

        cur.execute(
            "INSERT INTO expenses VALUES (NULL,?,?,?,?,?)",
            (amount, paid_by, desc, today, month)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    conn.close()
    return render_template("add_expense.html", users=users)
app=Flask(__name__)
@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == "POST":
        amount = float(request.form["amount"])
        paid_by = request.form["paid_by"]
        desc = request.form["description"]
        cur.execute(
            "UPDATE expenses SET amount=?, paid_by=?, description=? WHERE id=?",
            (amount, paid_by, desc, id)
        )
        conn.commit()
        conn.close()
        return redirect("/")

    cur.execute("SELECT * FROM expenses WHERE id=?", (id,))
    expense = cur.fetchone()
    cur.execute("SELECT name FROM users")
    users = [u[0] for u in cur.fetchall()]
    conn.close()

    return render_template("edit_expense.html", expense=expense, users=users)
app=Flask(__name__)
@app.route("/delete/<int:id>")
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id=?", (id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__=="__main":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port)


