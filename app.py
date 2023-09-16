import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.security import check_password_hash, generate_password_hash
from flask_login import current_user

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

"""User authentications"""
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


@app.route("/logout")
@login_required
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
        if len(existing_user) != 0:
            return apology("userename is already taken. Please choose another username.", 400)

        # Generate a hash of the password.
        hashed_password = generate_password_hash(password)

        # Insert the new user into the database.
        db.execute(
            "INSERT INTO users (username, hash, mail) VALUES (?, ?, ?)",
            username,
            hashed_password,
        )

        # Query the database for newly inserted user.
        new_user = db.execute("SELECT * FROM users WHERE username = ?", username)

        # Remember user.
        session["user_id"] = new_user[0]["id"]

        # Display success message.
        flash("Registration Successful. Welcome to Book Brightness!", "success")
        return redirect("/")
    else:
        return render_template("register.html")

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
            return redirect("/")
    else:
        return render_template("remove.html")


@app.route("/change_password", methods=["GET", "POST"])
@login_required
def change_password():
    if request.method == "POST":
        old_password = request.form.get("old_password")
        new_password = request.form.get("new_password")
        confirmation = request.form.get("confirmation")

        # Validate form data
        if not old_password or not new_password or not confirmation:
            return apology("Please confirm your password.", 400)

        if not check_password_hash(current_user.password_hash, old_password):
            return apology("Please confirm your password.", 400)

        if new_password != confirmation:
            return apology("Please confirm your password.", 400)
        # Update user's password
        current_user.password_hash = generate_password_hash(new_password)
        db.commit()

        flash("Password changed successfully!", "success")
        return redirect("/profile") # Replace with your profile route
    else:
        return render_template("change_password.html")

"""display Products"""
@app.route("/")
def catalog():
    """shop catalog"""
    books = db.execute("SELECT * FROM books")

    schoolSupplies = db.execute("SELECT * FROM school_supplies")
    return render_template('catalog.html', books=books, schoolSupplies=schoolSupplies)

@app.route("/category", methods=["GET", "POST"])
def category():
    """shop catalog"""
    books = db.execute("SELECT * FROM books")

    return render_template('category.html', books=books)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    """User profile and history"""
    user_id = session["user_id"]

    # Fetch user data and order history from the database
    user_data = db.execute("SELECT * FROM users WHERE id = ?", user_id)
    orders = db.execute("SELECT * FROM orders WHERE user_id = ?", user_id)

    return render_template("profile.html", user_data=user_data[0], orders=orders)



@app.route("/grades", methods=["GET", "POST"])
def grades():

    grades = db.execute("SELECT * FROM books where category = 'grade'")

    return render_template('grades.html', grades=grades)

@app.route("/novel", methods=["GET", "POST"])
def novel():

    novels = db.execute("SELECT * FROM books where category = 'Novel'")

    return render_template('novel.html', novels=novels)

@app.route("/curriculums", methods=["GET", "POST"])
def curriculums():

    curriculums = db.execute("SELECT * FROM books where category = 'curriculum'")

    return render_template('curriculums.html', curriculums=curriculums)


@app.route("/products", methods=["GET", "POST"])
def products():

    schoolSupplies = db.execute("SELECT * FROM school_supplies")
    return render_template('products.html', schoolSupplies=schoolSupplies)

"""payment and cart
# add product
@app.route('/add_to_cart', methods=['POST'])
@login_required
def add_product_to_cart():
    if request.methodc == "POST":
        product_id = request.form.get('product_id')
        books_id = request.form.get('books_id')
        quantity = int(request.form.get('quantity'))
        user_id = 1  # Replace with the actual user's ID
        add_to_cart(product_id, books_id, quantity, user_id)
        # Display success message.
        flash("Product added to cart successfully.", "success")
        return redirect("/")
    else:
        return render_template("buy.html")


# display the cart
@app.route('/cart')
@login_required
def view_cart():
    user_id = 1  # Replace with the actual user's ID
    cart_contents = display_cart(user_id)
    return render_template('cart.html', cart_contents=cart_contents)



# Function to add a product to the cart
def add_to_cart(product_id, books_id, quantity, user_id):
    cart_item = Cart.query.filter_by(
        product_id=product_id,
        books_id=books_id,
        user_id=user_id
    ).first()

    if cart_item:
        # If the product is already in the cart, update the quantity
        cart_item.quantity += quantity
    else:
        # Otherwise, create a new cart item
        cart_item = Cart(
            product_id=product_id,
            books_id=books_id,
            quantity=quantity,
            user_id=user_id
        )

    db.session.add(cart_item)
    db.session.commit()

# Function to display the cart
def display_cart(user_id):
    cart_items = Cart.query.filter_by(user_id=user_id).all()

    # Fetch product and book details for each item in the cart
    cart_details = []
    for item in cart_items:
        product = Product.query.get(item.product_id)
        book = Book.query.get(item.books_id)
        cart_details.append({
            "product_name": product.product_name,
            "book_title": book.book_title,
            "quantity": item.quantity,
            "price": product.price
        })

    return cart_details"""

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
        return redirect("/payment")

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
            flash("Thank you for your order! We will deliver soon.", "success")
        elif selected_method == 'other':
            flash("Sorry! online payment will be implemented in a future version of books brightness.", "error")

    else:
        return render_template('payment.html')
