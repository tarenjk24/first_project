import os

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user
from cs50 import SQL

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


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

''' user authentication routes '''
# login
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
        return redirect("/")
    else:
        return render_template("login.html")


# register
@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    # Forget any user_id.
    session.clear()

    if request.method == "POST":
        # Get user name and password.
        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Validate user input.
        if not username:
            return apology("must provide username", 400)

        elif not password:
            return apology("must provide password", 400)

        elif not confirmation:
            return apology("must confirm password", 400)

        elif password != confirmation:
            return apology("must confirm password", 400)

        # Query the database to check if the username is already taken.
        existing_user = db.execute("SELECT * FROM users WHERE username = ?", username)
        if len(existing_user) != 0:
            return apology("userename taken", 400)

        # Generate a hash of the password.
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database.
        db.execute(
            "INSERT INTO users (username, hash) VALUES (?, ?)",
            username,
            hashed_password,
        )

        # Query the database for newly inserted user.
        new_user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember user.
        session["user_id"] = new_user[0]["id"]

        # Display success message.
        flash("Registration successful.", "success")
        return redirect("/")
    else:
        return render_template("register.html")



# logout
@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


# remove

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
            return apology("must provide username", 400)

        elif not password:
            return apology("must provide password", 400)

        elif not confirmation:
            return apology("must confirm password", 400)

        elif password != confirmation:
            return apology("must confirm password", 400)

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
            db.execute("DELETE FROM account WHERE user_id = ?", (user_id,))
            db.execute("DELETE FROM USERS WHERE username = ?", (username,))

            # Display success message.
            flash("Account deleted successfully.", "success")

            # Forget any user_id
            session.clear()

            # Redirect user to login form
            return redirect("/")
    else:
        return render_template("remove.html")



@app.route('/submit', methods=['POST'])
def submit():
    if request.method == "POST":
        email = request.form.get('email')
        db.execute(
            "INSERT INTO users (email) VALUES (?)",
            mail
        )
    else:
        return render_template('layout.html', email=email)

''' link routes '''
@app.route('/about_us')
def about_us():
    return render_template('campany/aboutus.html')

@app.route('/delivery_information')
def delivery_information():
    return render_template('campany/deliveryinformation.html')

@app.route('/privacy_policy')
def privacy_policy():
    return render_template('campany/privacypolicy.html')

@app.route('/terms_conditions')
def terms_conditions():
    return render_template('campany/termsconditions.html')

@app.route('/comingsoon')
def comingsoon():
    return render_template('campany/comingsoon.html')



''' displaying routes '''
# display a sample of product in main page
@app.route("/", methods=["GET", "POST"])
def index():

    """shop catalog"""
    books = db.execute("SELECT * FROM products")

    supplies = db.execute("SELECT * FROM products")
    return render_template('index.html', books=books, supplies=supplies)


# display books ( 4 categories )
@app.route("/books", methods=["GET", "POST"])
def books():
    books = db.execute("SELECT * FROM products WHERE type='books' ")

    return render_template('books.html', books=books)



# categories books:
@app.route("/grades", methods=["GET", "POST"])
def grades():

    products = db.execute("SELECT * FROM products where category = 'grade'")

    return render_template('grades.html', products=products)

@app.route("/novel", methods=["GET", "POST"])
def novel():

    products = db.execute("SELECT * FROM products where category = 'Novel'")

    return render_template('novel.html', products=products)

@app.route("/curriculums", methods=["GET", "POST"])
def curriculums():

    products = db.execute("SELECT * FROM products where category = 'curriculum'")

    return render_template('curriculums.html', products=products)

# display products ( school supplies )
@app.route("/products", methods=["GET", "POST"])
def products():
    products = db.execute("SELECT * FROM products WHERE type='supplies'")

    return render_template('products.html', products=products)


# profile
@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile and history"""
    user_id = session["user_id"]

    # Fetch user data and order history from the database
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.execute("SELECT * FROM orders WHERE user_id = ?", user_id)
    information = db.execute("SELECT * FROM addresses WHERE user_id = ?", user_id)

    return render_template("profile.html", user_data=user_data[0], orders=orders, information=information)


"""cart"""

@app.route("/productdetails/<int:id>", methods=["GET", "POST"])
def productdetails(id):

    product = db.execute("SELECT id FROM products WHERE id=?", (id,))
    details = db.execute("SELECT * FROM products WHERE id=?", (id,))

    print("Product:", details)

    return render_template('productdetails.html', details=details, product=product)


def get_product_details_by_id(id):

        product = db.execute("SELECT * FROM products WHERE id=?", (product_id,))

        # Print for debugging
        print("Product:", product)
        return product

@app.route('/addtocart/<int:id>', methods=["GET","POST"])
@login_required
def addtocart(id):
    if request.method == "POST":
        quantity = request.form.get('quantity')
        product = get_product_details_by_id(id)
        if not product:
            return apology("must provide a symbol", 400)
        elif not quantity:
            return apology("must provide shares", 400)
        elif not quantity.isdigit() or int(quantity) <= 0:
            return apology("invalid  shares", 400)
        db.execute(
                "INSERT INTO cart (productid, quantity) VALUES (?, ?)",
                (product, quantity)
                )
        flash("Added to cart!", "success")
        return redirect("/")

    else:
        product = db.execute("SELECT * FROM products WHERE id=?", (id,)).fetchone()
        return render_template("productdetails.html", details=[product])

# checkout
@app.route("/cart", methods=["GET", "POST"])
@login_required
def cart():

    user_id = session["user_id"]


    query = """
    SELECT p.id, p.name, p.price, p.availability, p.cover, c.quantity
    FROM products p
    INNER JOIN cart c ON p.id = c.productid
    """
    rows = db.execute(query)

    return render_template("cart.html", rows=rows)


''' paryment and checkout routes '''
# checkout
@app.route("/checkout", methods=["GET", "POST"])
def checkout():
    if request.method == "POST":
        # Get user input data from the form
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        postal_code = request.form.get("postal_code")
        phone_number = request.form.get("phone_number")

        # Validate user input
        if not city or not state or not address or not postal_code or not phone_number:
            return apology("Please provide all required information.", 400)

        elif not postal_code.isdigit() or int(postal_code) <= 0:
            return apology("Invalid postal code. Please provide a valid postal code.", 400)

        elif not phone_number.isdigit() or int(phone_number) <= 0:
            return apology("Invalid phone number. Please provide a valid phone number.", 400)

        try:
            db.execute(
                "INSERT INTO orders (city, state, address, postal_code, phone_number, note) VALUES (?, ?, ?, ?, ?)",
                (city, state, address, postal_code, phone_number)
            )


            # Display success message to the user
            flash("Address saved successfully.", "success")

            # Redirect the user to the payment page
            return redirect("/cart")

        except Exception as e:
            # Print the exception for debugging purposes
            print("Error:", str(e))

            # Display an apology message or redirect as needed
            return apology("An error occurred while saving the address.", 500)

    else:
        # Render the checkout template when the request method is GET
        return render_template("checkout.html")



# payment
@app.route("/payment", methods=["GET", "POST"])
@login_required
def payment():
        return render_template('payment.html')

