from flask import Flask, render_template, request, redirect, url_for, flash
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secretkey'

ADMIN_EMAIL = "admin@gmail.com"
ADMIN_PASSWORD = "admin123"
ITEMS_FILE = "items.txt"

def read_items():
    items = []
    with open(ITEMS_FILE, "r", encoding="utf-8") as file:
        for line in file:
            parts = line.strip().split(",")
            if len(parts) == 3:
                try:
                    name, stock, price = parts[0], int(parts[1]), float(parts[2])
                    items.append({"name": name, "stock": stock, "price": price})
                except ValueError:
                    print(f"Skipping invalid line: {line.strip()}")
    return items

def write_items(items):
    with open(ITEMS_FILE, "w", encoding="utf-8") as file:
        for item in items:
            file.write(f"{item['name']},{item['stock']},{item['price']}\n")

def send_email(name, phone, house, location, item, quantity):
    sender = "aaravd362@gmail.com"
    app_password = "ephw rehn vtye nadv"
    receiver = "aaravd362@gmail.com"

    subject = "\U0001F6D2 New Customer Details"
    body = f"""
\U0001F4E9 New order details:

\U0001F464 Name: {name}
\U0001F4DE Phone: {phone}
\U0001F3E0 House No.: {house}
\U0001F3E2 location: {location}

\U0001F9FE Ordered: {quantity} x {item}
    """

    message = MIMEText(body)
    message["From"] = sender
    message["To"] = receiver
    message["Subject"] = subject

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as smtp:
            smtp.starttls()
            smtp.login(sender, app_password)
            smtp.sendmail(sender, receiver, message.as_string())
        return True
    except Exception as e:
        print("❌ Error sending email:", e)
        return False

@app.route("/")
def index():
    items = read_items()
    return render_template("index.html", shop_name="Aarav's General Shop", shop_items=items)

@app.route('/confirm', methods=['POST'])
def confirm():
    item_name = request.form['item_name']
    quantity = int(request.form['quantity'])
    items = read_items()

    for item in items:
        if item['name'] == item_name and item['stock'] >= quantity:
            item['stock'] -= quantity
            write_items(items)
            return redirect(url_for('details', item=item_name, quantity=quantity))

    flash("❌ Not enough stock!")
    return redirect(url_for('index'))

@app.route("/details", methods=["GET", "POST"])
def details():
    if request.method == "POST":
        # Get item and quantity from the submitted form (hidden fields)
        item = request.form.get("item", "")
        quantity = request.form.get("quantity", "")
        name = request.form.get("name")
        phone = request.form.get("phone")
        house = request.form.get("house")
        location = request.form.get("location")

        success = send_email(name, phone, house, location , item, quantity)

        if success:
            flash(f"✅ You have successfully ordered {quantity} x {item}!", "success")
        else:
            flash("❌ Error sending email!", "error")

        return render_template(
            "confirmation.html",
            shop_name="Aarav's General Shop",
            item=item,
            quantity=quantity
        )

    # For GET request — item and quantity from URL
    item = request.args.get("item", "")
    quantity = request.args.get("quantity", "")
    return render_template(
        "details.html",
        shop_name="Aarav's General Shop",
        item=item,
        quantity=quantity
    )


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            return redirect(url_for('admin'))
        else:
            flash("❌ Incorrect email or password!", "error")
            return redirect(url_for('login'))
    return render_template('login.html', shop_name="Aarav's General Shop")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        item_name = request.form.get("item_name")
        stock = request.form.get("stock")
        price = request.form.get("price")

        if item_name and stock.isdigit() and price.isdigit():
            items = read_items()
            items.append({"name": item_name, "stock": int(stock), "price": int(price)})
            write_items(items)
            flash("✅ Item added successfully!", "success")
        else:
            flash("❌ Invalid input. Please enter valid data.", "error")

    shop_items = read_items()
    return render_template("admin.html", shop_items=shop_items, shop_name="Aarav's General Shop")

@app.route("/update_item", methods=["POST"])
def update_stock():
    item_name = request.form.get("item_name")
    new_stock = request.form.get("new_stock")
    new_price = request.form.get("new_price")

    if not item_name or not new_stock.isdigit() or not new_price.replace(".", "", 1).isdigit():
        flash("❌ Invalid input. Stock must be a number!", "error")
        return redirect(url_for("admin"))

    new_stock = int(new_stock)
    new_price = float(new_price)

    items = read_items()
    item_found = False

    for item in items:
        if item["name"].lower() == item_name.lower():
            item["stock"] = new_stock
            item["price"] = new_price
            item_found = True
            break

    if item_found:
        write_items(items)
        flash("✅ Item updated successfully!", "success")
    else:
        flash("❌ Item not found!", "error")

    return redirect(url_for("admin"))

@app.route("/add_item", methods=["POST"])
def add_item():
    item_name = request.form.get("item_name")
    stock = request.form.get("stock")
    price = request.form.get("price")

    if not item_name or not stock.isdigit() or not price.isdigit():
        flash("❌ Invalid input. Please enter valid data.", "error")
        return redirect(url_for("admin"))

    items = read_items()
    items.append({"name": item_name, "stock": int(stock), "price": int(price)})
    write_items(items)

    flash("✅ Item added successfully!", "success")
    return redirect(url_for("admin"))

@app.route("/delete_item", methods=["POST"])
def delete_item():
    item_name = request.form.get("item_name")
    items = read_items()
    new_items = [item for item in items if item["name"].lower() != item_name.lower()]

    if len(items) == len(new_items):
        flash("❌ Item not found!", "error")
    else:
        write_items(new_items)
        flash(f"\U0001F5D1️ '{item_name}' deleted successfully!", "success")

    return redirect(url_for("admin"))

@app.route('/robots.txt')
def robots():
    return send_from_directory('static', 'robots.txt')

@app.route('/sitemap.xml')
def sitemap():
    return send_from_directory('static', 'sitemap.xml')

if __name__=="__main__":
    app.run(debug=True)
