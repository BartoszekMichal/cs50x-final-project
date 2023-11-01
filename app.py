import os

from datetime import datetime
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import login_required, apology
from ielist import expenses, source

# Configure application
app = Flask(__name__)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///final.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/entry")
def entry():
    return render_template("entry.html")


@app.route("/")
@login_required
def index():
    """Get user's balance and display it on the main page"""

    balance = db.execute("SELECT balance FROM users WHERE id = ?", session["user_id"])

    balance = balance[0]["balance"]

    # Change method of displaying the balance
    usd = f"${balance:,.2f}"

    # Render template with current user's balance
    return render_template("layout.html", balance=usd)


@app.route("/login", methods=["GET", "POST"])
def login():
    """ Log in the user """

    # Forget any user_id
    session.clear()

    # User reaches route via POST by submitting a form
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Must provide username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Must provide password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username exists and the password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to homepage
        return redirect("/")

    # Render login.html when user reached route via GET
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/entry")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = ?", request.form.get("username"))

        # Ensure username was submitted and check if user exists
        if not request.form.get("username"):
            return apology("Must provide username")
        elif len(rows) == 1:
            return apology("User already exists")

        # Ensure both passwords were submitted and they match
        if not request.form.get("password") or not request.form.get("confirmation"):
            return apology("Must provide password and confirmation")
        elif request.form.get("password") != request.form.get("confirmation"):
            return apology("Passwords do not match")

        # Hash password
        hashed_password = generate_password_hash(request.form.get("password"), method='pbkdf2', salt_length=16)

        # Remember registrants
        db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", request.form.get("username"), hashed_password)

        return redirect("/login")

    else:
        return render_template("register.html")


@app.route("/add_income", methods=["GET", "POST"])
@login_required
def add_income():
    """Add user's income"""

    # Import and sort source list
    source.sort()

    # User reached route via POST by submitting form
    if request.method == "POST":

        # Ensure income source was submitted
        if not request.form.get("source"):
            return apology("Missing source of income")

        # Accept only positive float numbers
        str_to_float = request.form.get("income").replace(".", "", 1).isdigit()

        # Ensure income was submitted with only positive number
        if not request.form.get("income"):
            return apology("Missing income")
        elif not str_to_float:
            return apology("Positive numbers only")

        # Insert user's income to SQL income table
        db.execute("INSERT INTO income (user_id, income_source, amount, date) \
        VALUES(?, ?, ?, ?)", session["user_id"], request.form.get("source"), request.form.get("income"), datetime.now())

        # Update user's balance
        balance = db.execute("SELECT balance FROM users WHERE id = ?", session["user_id"])
        db.execute("UPDATE users SET balance = ? WHERE id = ?", balance[0]["balance"] + float(request.form.get("income")), session["user_id"])

        # Redirect user to add another income
        return redirect("/add_income")

    # If user reached route via GET, render add_income page
    else:
        return render_template("add_income.html", source=source)


@app.route("/add_expenses", methods=["GET", "POST"])
@login_required
def add_expenses():
    """Add user's expenses"""

    # Sort list of expenses
    expenses.sort()

    # User reached route via POST by submitting form
    if request.method == "POST":

        # Ensure income source was submitted
        if not request.form.get("expense"):
            return apology("Missing expense")

        # Accept only positive float numbers
        str_to_float = request.form.get("expense_amount").replace(".", "", 1).isdigit()

        # Ensure income was submitted with only positive number
        if not request.form.get("expense_amount"):
            return apology("Missing expense")
        elif not str_to_float:
            return apology("Positive numbers only")

        # Get user's balance
        balance = db.execute("SELECT balance FROM users WHERE id = ?", session["user_id"])

        # Check if user's balance is enough for expense
        if float(request.form.get("expense_amount")) > balance[0]["balance"]:
            return apology("Can't afford. Your balance is too low.")
        else:
            # Insert user's expense to SQL expenses table
            db.execute("INSERT INTO expenses (user_id, expense_source, amount, date) \
            VALUES(?, ?, ?, ?)", session["user_id"], request.form.get("expense"), request.form.get("expense_amount"), datetime.now())

            # Update user's balance
            db.execute("UPDATE users SET balance = ? WHERE id = ?", balance[0]["balance"] - float(request.form.get("expense_amount")), session["user_id"])

        # Redirect user to add another income
        return redirect("/add_expenses")

    # If user reached route via GET, render add_income page
    else:
        return render_template("add_expenses.html", expense=expenses)


@app.route("/income_chart", methods=["GET", "POST"])
@login_required
def income_chart():
    """Show a bar chart of user's income"""

    # Get user's income data
    income = db.execute("SELECT income_source, SUM(amount) FROM income WHERE user_id = ? GROUP BY income_source", session["user_id"])

    # Get income_sources in a list
    labels = [row["income_source"]for row in income]

    # Get amounts in a list
    values = [row["SUM(amount)"]for row in income]

    # Return a chart of those data
    return render_template("income_chart.html", labels=labels, values=values)


@app.route("/expense_chart", methods=["GET", "POST"])
@login_required
def expense_chart():
    """Show a bar chart of user's expenses"""

    # Get user's expenses data
    expenses = db.execute("SELECT expense_source, SUM(amount) FROM expenses WHERE user_id = ? GROUP BY expense_source", session["user_id"])

    # Get income_sources in a list
    labels = [row["expense_source"]for row in expenses]

    # Get amounts in a list
    values = [row["SUM(amount)"]for row in expenses]

    # Return a chart of those data
    return render_template("expense_chart.html", labels=labels, values=values)


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    """Change user's password"""

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Extract the old hash value of user's password
        pwhash = db.execute("SELECT hash FROM users WHERE id = ?", session["user_id"])

        # Check if user's old password from db match with the typed one used to log in
        if check_password_hash(pwhash[0]["hash"], request.form.get("old_password")) == False:
            return apology("Old password is not correct")
        # Check if user fills all the fields and that a new password match in both fields
        elif not request.form.get("old_password") or not request.form.get("new_password") or not request.form.get("confirmation"):
            return apology("Provide old password, new password and confirmation")
        elif request.form.get("new_password") != request.form.get("confirmation"):
            return apology("New passwords do not match")
        else:
            # Hash a new password provided by the user and update it in the 'users' table
            new_pwhash = generate_password_hash(request.form.get("new_password"), method='pbkdf2', salt_length=16)
            db.execute("UPDATE users SET hash = ? WHERE id = ?", new_pwhash, session["user_id"])

        # Redirect to homepage after successfull process
        return redirect("/")

    # Render template via GET method
    else:
        return render_template("change_password.html")

