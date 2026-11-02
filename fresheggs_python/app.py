from datetime import date
from functools import wraps
import os
import sqlite3
import sys

from flask import Flask, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash

# When packaged as a Windows .exe (PyInstaller), templates/static live in a temporary
# bundle folder, so the database is stored in an "instance" folder next to the .exe.
FROZEN = getattr(sys, "frozen", False)
BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
    instance_path=os.path.join(os.path.dirname(sys.executable), "instance") if FROZEN else None,
)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-development-secret")
DATABASE = os.path.join(app.instance_path, "fresheggs.sqlite3")
os.makedirs(app.instance_path, exist_ok=True)


def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    db.executescript("""
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            price REAL NOT NULL CHECK(price > 0),
            stock_trays INTEGER NOT NULL DEFAULT 0 CHECK(stock_trays >= 0),
            active INTEGER NOT NULL DEFAULT 1
        );
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            customer_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT NOT NULL,
            delivery_date TEXT,
            notes TEXT,
            status TEXT NOT NULL DEFAULT 'Pending',
            total_amount REAL NOT NULL,
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS order_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id INTEGER NOT NULL REFERENCES orders(id) ON DELETE CASCADE,
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity INTEGER NOT NULL CHECK(quantity > 0),
            unit_price REAL NOT NULL
        );
        CREATE TABLE IF NOT EXISTS admins (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL
        );
    """)
    # Create the administrator if missing (also works when an older database
    # already contains a different admin such as "admin").
    admin_user = os.environ.get("ADMIN_USERNAME", "success")
    if db.execute("SELECT 1 FROM admins WHERE username = ?", (admin_user,)).fetchone() is None:
        db.execute(
            "INSERT INTO admins (username, password_hash) VALUES (?, ?)",
            (admin_user, generate_password_hash(os.environ.get("ADMIN_PASSWORD", "lungwe04!"))),
        )
    db.commit()


def admin_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("admin_id"):
            flash("Please sign in to access the administrator dashboard.", "error")
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped


@app.template_filter("mwk")
def mwk(value):
    return "MWK {:,.2f}".format(float(value))


@app.route("/")
def index():
    products = get_db().execute(
        "SELECT * FROM products WHERE active = 1 ORDER BY price"
    ).fetchall()
    return render_template("index.html", products=products, today=date.today().isoformat())


@app.route("/order", methods=["POST"])
def place_order():
    db = get_db()
    customer_name = request.form.get("customer_name", "").strip()
    phone = request.form.get("phone", "").strip()
    address = request.form.get("address", "").strip()
    delivery_date = request.form.get("delivery_date", "").strip()
    notes = request.form.get("notes", "").strip()
    try:
        product_id = int(request.form.get("product_id", ""))
        quantity = int(request.form.get("quantity", ""))
    except (TypeError, ValueError):
        flash("Choose an egg product and enter a valid quantity.", "error")
        return redirect(url_for("index") + "#order")

    if not customer_name or not phone or not address:
        flash("Please enter your name, phone number and delivery address.", "error")
        return redirect(url_for("index") + "#order")
    if len(customer_name) > 100 or len(phone) > 30 or len(address) > 500 or len(notes) > 1000:
        flash("One or more fields are too long. Please shorten them.", "error")
        return redirect(url_for("index") + "#order")
    if quantity < 1 or quantity > 500:
        flash("Quantity must be between 1 and 500 trays.", "error")
        return redirect(url_for("index") + "#order")
    if delivery_date:
        try:
            parsed_date = date.fromisoformat(delivery_date)
            if parsed_date < date.today():
                raise ValueError
        except ValueError:
            flash("Choose today or a future delivery date.", "error")
            return redirect(url_for("index") + "#order")

    try:
        db.execute("BEGIN IMMEDIATE")
        product = db.execute(
            "SELECT * FROM products WHERE id = ? AND active = 1", (product_id,)
        ).fetchone()
        if product is None:
            db.rollback()
            flash("That product is not available.", "error")
            return redirect(url_for("index") + "#order")
        if quantity > product["stock_trays"]:
            db.rollback()
            flash(f"Only {product['stock_trays']} tray(s) are currently available for {product['name']}.", "error")
            return redirect(url_for("index") + "#order")

        total = product["price"] * quantity
        cursor = db.execute(
            """INSERT INTO orders
               (customer_name, phone, address, delivery_date, notes, status, total_amount)
               VALUES (?, ?, ?, ?, ?, 'Pending', ?)""",
            (customer_name, phone, address, delivery_date or None, notes, total),
        )
        order_id = cursor.lastrowid
        db.execute(
            "INSERT INTO order_items (order_id, product_id, quantity, unit_price) VALUES (?, ?, ?, ?)",
            (order_id, product_id, quantity, product["price"]),
        )
        db.execute(
            "UPDATE products SET stock_trays = stock_trays - ? WHERE id = ?",
            (quantity, product_id),
        )
        db.commit()
    except sqlite3.Error:
        db.rollback()
        flash("We could not save your order. Please check the setup and try again.", "error")
        return redirect(url_for("index") + "#order")

    return redirect(url_for("order_success", order_id=order_id))


@app.route("/order/<int:order_id>")
def order_success(order_id):
    order = get_db().execute("SELECT * FROM orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        flash("Order not found.", "error")
        return redirect(url_for("index"))
    items = get_db().execute(
        """SELECT oi.quantity, oi.unit_price, p.name
           FROM order_items oi JOIN products p ON p.id = oi.product_id
           WHERE oi.order_id = ?""",
        (order_id,),
    ).fetchall()
    return render_template("order_success.html", order=order, items=items)


@app.route("/track", methods=["GET", "POST"])
def track_order():
    order = None
    items = []
    if request.method == "POST":
        raw_id = request.form.get("order_id", "").strip()
        phone = request.form.get("phone", "").strip()
        if raw_id.isdigit() and phone:
            order = get_db().execute(
                "SELECT * FROM orders WHERE id = ? AND phone = ?", (int(raw_id), phone)
            ).fetchone()
            if order:
                items = get_db().execute(
                    """SELECT oi.quantity, oi.unit_price, p.name
                       FROM order_items oi JOIN products p ON p.id = oi.product_id
                       WHERE oi.order_id = ?""", (order["id"],)
                ).fetchall()
            else:
                flash("No order matched that order number and phone number.", "error")
        else:
            flash("Enter your order number and the phone number used for the order.", "error")
    return render_template("track.html", order=order, items=items)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if session.get("admin_id"):
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = get_db().execute("SELECT * FROM admins WHERE username = ?", (username,)).fetchone()
        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            return redirect(url_for("admin_dashboard"))
        flash("Incorrect username or password.", "error")
    return render_template("admin_login.html")


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    session.clear()
    flash("You have signed out.", "success")
    return redirect(url_for("index"))


@app.route("/admin")
@admin_required
def admin_dashboard():
    db = get_db()
    products = db.execute("SELECT * FROM products ORDER BY id").fetchall()
    orders = db.execute(
        """SELECT o.*, GROUP_CONCAT(p.name || ' × ' || oi.quantity, ', ') AS items
           FROM orders o
           LEFT JOIN order_items oi ON oi.order_id = o.id
           LEFT JOIN products p ON p.id = oi.product_id
           GROUP BY o.id ORDER BY o.created_at DESC LIMIT 200"""
    ).fetchall()
    summary = {
        "orders": db.execute("SELECT COUNT(*) FROM orders").fetchone()[0],
        "pending": db.execute("SELECT COUNT(*) FROM orders WHERE status = 'Pending'").fetchone()[0],
        "delivered": db.execute("SELECT COUNT(*) FROM orders WHERE status = 'Delivered'").fetchone()[0],
        "revenue": db.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status != 'Cancelled'").fetchone()[0],
    }
    return render_template("admin_dashboard.html", products=products, orders=orders, summary=summary)


@app.route("/admin/product/<int:product_id>", methods=["POST"])
@admin_required
def update_product(product_id):
    try:
        price = float(request.form.get("price", ""))
        stock = int(request.form.get("stock_trays", ""))
        if price <= 0 or stock < 0 or stock > 100000:
            raise ValueError
    except ValueError:
        flash("Enter a price above zero and a stock quantity of zero or more.", "error")
        return redirect(url_for("admin_dashboard") + "#stock")
    db = get_db()
    cursor = db.execute(
        "UPDATE products SET price = ?, stock_trays = ? WHERE id = ?",
        (price, stock, product_id),
    )
    db.commit()
    flash("Product updated." if cursor.rowcount else "Product not found.", "success" if cursor.rowcount else "error")
    return redirect(url_for("admin_dashboard") + "#stock")


@app.route("/admin/product/add", methods=["POST"])
@admin_required
def add_product():
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    try:
        price = float(request.form.get("price", ""))
        stock = int(request.form.get("stock_trays", ""))
        if price <= 0 or stock < 0 or stock > 100000:
            raise ValueError
    except ValueError:
        flash("Enter a price above zero and a stock quantity of zero or more.", "error")
        return redirect(url_for("admin_dashboard") + "#stock")
    if not name or len(name) > 100 or len(description) > 300:
        flash("Enter a product name (up to 100 characters) and a short description.", "error")
        return redirect(url_for("admin_dashboard") + "#stock")
    db = get_db()
    db.execute(
        "INSERT INTO products (name, description, price, stock_trays) VALUES (?, ?, ?, ?)",
        (name, description or name, price, stock),
    )
    db.commit()
    flash("Product added.", "success")
    return redirect(url_for("admin_dashboard") + "#stock")


@app.route("/admin/product/<int:product_id>/toggle", methods=["POST"])
@admin_required
def toggle_product(product_id):
    db = get_db()
    cursor = db.execute("UPDATE products SET active = 1 - active WHERE id = ?", (product_id,))
    db.commit()
    flash("Product visibility changed." if cursor.rowcount else "Product not found.",
          "success" if cursor.rowcount else "error")
    return redirect(url_for("admin_dashboard") + "#stock")


@app.route("/admin/order/<int:order_id>/status", methods=["POST"])
@admin_required
def update_order_status(order_id):
    allowed = {"Pending", "Confirmed", "Out for delivery", "Delivered", "Cancelled"}
    status = request.form.get("status", "")
    if status not in allowed:
        flash("Choose a valid order status.", "error")
        return redirect(url_for("admin_dashboard") + "#orders")
    db = get_db()
    cursor = db.execute("UPDATE orders SET status = ? WHERE id = ?", (status, order_id))
    db.commit()
    flash("Order status updated." if cursor.rowcount else "Order not found.", "success" if cursor.rowcount else "error")
    return redirect(url_for("admin_dashboard") + "#orders")


@app.cli.command("init-db")
def init_db_command():
    """Create the tables and the administrator account."""
    init_db()
    print(f"Database initialized at {DATABASE}")


with app.app_context():
    init_db()


if __name__ == "__main__":
    app.run(debug=True)
