import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
import sqlite3


from helpers import apology, login_required, usd



# Configure application
app = Flask(__name__)
# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///library.db")
# Connect to the SQLite database
db_connection = sqlite3.connect('library.db')
db_cursor = db_connection.cursor()


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("Please provide a username.", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("Please provide a password.", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/main")
    else:
        return render_template("login.html")


@app.route("/remove", methods=["GET", "POST"])
@login_required
def remove():
    """Delete user account"""
    if request.method == "POST":
        # Get user name and password.
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate user input.
        if not username:
            return apology("Please provide a username.", 400)

        elif not password:
            return apology("Please provide a password.", 400)

        elif not confirmation:
            return apology("Please confirm your password.", 400)

        elif password != confirmation:
            return apology("Passwords do not match.", 400)

        # Query the database to check if the username is already taken.
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if not existing_user:
            return apology("Wrong user", 403)
        else:
            # Get user id.
            user_id_data = db.execute(
                "SELECT id FROM users WHERE username = ?", (username,)
            )
            user_id = user_id_data[0]["id"]

            # Delete user's account and related data from the database.
            db.execute("DELETE FROM orders WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM address WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM USERS WHERE username = ?", (username,))

            # Display success message.
            flash("Account deleted successfully.", "success")

            # Forget any user_id
            session.clear()

            # Redirect user to login form
            return redirect("/main")
    else:
        return render_template("remove.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id.
    session.clear()

    if request.method == "POST":
        # Get user name and password.
        username = request.form.get("username")
        mail = request.form.get("mail")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate user input.
        if not mail:
            return apology("Please provide your email.", 400)
        elif not username:
            return apology("Please provide a username.", 400)

        elif not password:
            return apology("Please provide a password.", 400)

        elif not confirmation:
            return apology("Please confirm your password.", 400)

        elif password != confirmation:
            return apology("Passwords do not match.", 400)

        # Query the database to check if the username is already taken.
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(existing_user) != 0:
            return apology("userename is already taken. Please choose another username.", 400)

        # Generate a hash of the password.
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database.
        db.execute(
            "INSERT INTO users (username, hash, mail) VALUES (?, ?, ?)",
            username,
            hashed_password,
            mail
        )

        # Query the database for newly inserted user.
        new_user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember user.
        session["user_id"] = new_user[0]["id"]

        # Display success message.
        flash("Registration Successful. Welcome to Book Brightness!", "success")
        return redirect("/login")
    else:
        return render_template("register.html")

@app.route("/catalog", methods=["GET", "POST"])
def catalog():
    """shop catalog"""
    books = db.execute("SELECT * FROM books")

    schoolSupplies = db.excuse("SELECT * FROM school_supplies")
    return render_template('catalog.html', books=books, schoolSupplies=schoolSupplies)



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile and history"""
    user_id = session["user_id"]

    # Fetch user data and order history from the database
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.execute("SELECT * FROM orders WHERE user_id = ?", user_id)

    return render_template("profile.html", user_data=user_data[0], orders=orders)

@app.route("/checkout", methods=["GET", "POST"])
@login_required
def checkout():
    if request.method == "POST":
        # Get user input data from the form
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        postal_code = request.form.get("postal_code")
        phone_number = request.form.get("phone_number")
        note = request.form.get("note", "Default Note")

        # Validate user input
        if not city or not state or not address or not postal_code or not phone_number:
            return apology("Please provide all required information.", 400)

        if not postal_code.isdigit() or int(postal_code) <= 0:
            return apology("Invalid postal code. Please provide a valid postal code.", 400)

        if not phone_number.isdigit() or int(phone_number) <= 0:
            return apology("Invalid phone number. Please provide a valid phone number.", 400)

        # Insert user data into the database
        db.execute(
            "INSERT INTO address (city, state, address, postal_code, phone_number, note) VALUES (?, ?, ?, ?, ?, ?)",
            (city, state, address, postal_code, phone_number, note)
        )
        db.commit()

        # Display success message to the user
        flash("Address saved successfully.", "success")

        # Redirect the user to the payment page
        return redirect("/payment")  # Use the route name here

    else:
        # Render the checkout template when the request method is GET
        return render_template("checkout.html")


@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
    if request.method == 'POST':
        selected_method = request.form.get('method_paying')

        if selected_method == 'cash':
            # Perform actions for cash payment
            return "Thank you for your order! We will deliver soon."
        elif selected_method == 'other':
            # Perform actions for other payment methods
            return "Please proceed to the payment gateway."

    return render_template('payment_form.html')


""" not done possible routes to add : admin route/ promotions route / bonus piont route
missing routes product route
about template
contact us template"""
