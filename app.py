import os
from flask import Flask, render_template, request, jsonify, url_for, session, redirect
from flask_mysqldb import MySQL
from werkzeug.utils import secure_filename
import uuid

app = Flask(__name__)

# Configure MySQL connection
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'VerandaCafe'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

# Upload folder and allowed extensions
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'upload')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_default_secret_key_here')

mysql = MySQL(app)

# Check if file has allowed extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def ensure_temp_user_id():
    # Check if the temporary user ID is already set in the session
    if 'temporary_user_id' not in session:
        # Generate a new UUID for the temporary user and store it in the session
        session['temporary_user_id'] = str(uuid.uuid4())

# Home route to display menu categories
@app.route("/")
def home():
    cur = mysql.connection.cursor()

    # Get all categories
    cur.execute("SELECT name FROM MenuCategories")
    categories = cur.fetchall()

    # Get menu items from 'Daily Offers' only if they are active (is_active = 1)
    cur.execute("""
        SELECT mi.id, mi.name, mi.price, mi.image_url
        FROM MenuItems mi
        JOIN MenuCategories mc ON mi.category_id = mc.id
        WHERE mc.name = 'Daily Offers' AND mi.is_active = 1
    """)
    daily_offers_items = cur.fetchall()

    # Close cursor
    cur.close()

    # Render the home page with categories and active Daily Offers items
    return render_template("client/index.html", categories=categories, daily_offers_items=daily_offers_items)

@app.route('/admin/dashboard')
def admin_dashboard():
    try:
        cursor = mysql.connection.cursor()

        # Query for total menus
        cursor.execute("SELECT COUNT(*) FROM menuitems")
        result = cursor.fetchone()
        total_menus = result['COUNT(*)']  # Accessing the count from the dictionary key

        # Query for total orders today
        cursor.execute("SELECT COUNT(*) FROM orders WHERE DATE(created_at) = CURDATE()")
        result2 = cursor.fetchone()
        total_orders_today = result2['COUNT(*)']

        cursor.execute("SELECT COUNT(DISTINCT user_id) FROM orders WHERE DATE(created_at) = CURDATE()")
        result3 = cursor.fetchone()
        total_clients_today = result3['COUNT(DISTINCT user_id)']

        # Close the cursor
        cursor.close()

        # Return the dashboard with data
        return render_template('admin/dashboard.html', total_menus=total_menus, total_orders_today=total_orders_today, total_clients_today=total_clients_today)

    except Exception as e:
        # Log the error to console and pass the exception message to the error page
        print(f"Error loading dashboard: {e}")
        return render_template('error.html', error=f"Failed to load dashboard. Error: {str(e)}")


# Daily Offers for Admin
@app.route("/admin/dailyOffers")
def daily_offers():
    cursor = mysql.connection.cursor()
    query = """
        SELECT mi.id, mi.name, mi.price, mi.discounted_price, 
               mi.image_url, mi.preparation_time, mi.is_active, 
               mc.description
        FROM menuitems mi
        LEFT JOIN menucategories mc ON mi.category_id = mc.id
    """
    cursor.execute(query)
    daily_offers = cursor.fetchall()

    offers = [
        {
            "id": row["id"],
            "name": row["name"],
            "price": row["price"],
            "discounted_price": row["discounted_price"],
            "image_url": row["image_url"],
            "preparation_time": row["preparation_time"],
            "is_active": row["is_active"],
            "description": row["description"]
        }
        for row in daily_offers
    ]
    return render_template("admin/dailyOffers.html", daily_offers=offers)

# Toggle offer status (active/inactive)
@app.route('/admin/daily-offers/toggle/<int:item_id>', methods=['POST'])
def toggle_offer(item_id):
    try:
        data = request.get_json()
        is_active = data.get('is_active', False)

        cursor = mysql.connection.cursor()
        cursor.execute("""
            UPDATE menuitems
            SET is_active = %s
            WHERE id = %s
        """, (is_active, item_id))
        mysql.connection.commit()
        cursor.close()

        return jsonify({"message": "Offer status updated successfully."})
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the offer status."}), 500
    
@app.route('/admin/AllOrders')
def admin_orders():
    try:
        # Use DictCursor to fetch data as dictionaries
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT 
                id, user_id, product_name, price, quantity, order_status, 
                created_at, updated_at, dine_in_takeout, customer_name, special_requests
            FROM orders WHERE order_status = 'Pending'
        """)
        orders = cursor.fetchall()

        grouped_orders = {}
        for order in orders:
            user_id = order['user_id']
            if user_id not in grouped_orders:
                grouped_orders[user_id] = {
                    'customer_name': order['customer_name'],
                    'special_requests': order['special_requests'],
                    'created_at': order['created_at'],
                    'dine_in_takeout': order['dine_in_takeout'],
                    'items': [],
                    'total': 0
                }
            grouped_orders[user_id]['items'].append({
                'name': order['product_name'],
                'price': order['price'],
                'quantity': order['quantity']
            })
            grouped_orders[user_id]['total'] += order['price'] * order['quantity']

        cursor.close()
        return render_template('admin/AllOrders.html', grouped_orders=grouped_orders)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error loading orders: {e}", 500

@app.route('/admin/AllOrdersOngoing')
def admin_orders_Ongoing():
    try:
        # Use DictCursor to fetch data as dictionaries
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT 
                id, user_id, product_name, price, quantity, order_status, 
                created_at, updated_at, dine_in_takeout, customer_name, special_requests
            FROM orders WHERE order_status = 'OnGoing'
        """)
        orders = cursor.fetchall()

        grouped_orders = {}
        for order in orders:
            user_id = order['user_id']
            if user_id not in grouped_orders:
                grouped_orders[user_id] = {
                    'customer_name': order['customer_name'],
                    'special_requests': order['special_requests'],
                    'created_at': order['created_at'],
                    'dine_in_takeout': order['dine_in_takeout'],
                    'order_status': order['order_status'],
                    'items': [],
                    'total': 0
                }
            grouped_orders[user_id]['items'].append({
                'name': order['product_name'],
                'price': order['price'],
                'quantity': order['quantity']
            })
            grouped_orders[user_id]['total'] += order['price'] * order['quantity']

        cursor.close()
        return render_template('admin/AllOrders ongoing.html', grouped_orders=grouped_orders)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error loading orders: {e}", 500

@app.route('/admin/AllOrdersPast')
def admin_orders_Past():
    try:
        # Use DictCursor to fetch data as dictionaries
        cursor = mysql.connection.cursor()
        cursor.execute("""
              SELECT id, user_id, product_name, price, quantity, order_status, 
              created_at, updated_at, dine_in_takeout, customer_name, special_requests
              FROM orders
            WHERE order_status IN ('Completed', 'Cancelled') ORDER BY updated_at DESC;
        """)
        orders = cursor.fetchall()

        grouped_orders = {}
        for order in orders:
            user_id = order['user_id']
            if user_id not in grouped_orders:
                grouped_orders[user_id] = {
                    'customer_name': order['customer_name'],
                    'special_requests': order['special_requests'],
                    'created_at': order['created_at'],
                    'dine_in_takeout': order['dine_in_takeout'],
                    'order_status': order['order_status'],
                    'items': [],
                    'total': 0
                }
            grouped_orders[user_id]['items'].append({
                'name': order['product_name'],
                'price': order['price'],
                'quantity': order['quantity']
            })
            grouped_orders[user_id]['total'] += order['price'] * order['quantity']

        cursor.close()
        return render_template('admin/AllOrders Past.html', grouped_orders=grouped_orders)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error loading orders: {e}", 500


@app.route('/admin/UpdateOrderStatus', methods=['POST'])
def update_order_status():
    try:
        # Retrieve user_id and new_status from the request
        user_id = request.json.get('order_id')  # This is actually the user_id
        new_status = request.json.get('new_status')

        if not user_id or not new_status:
            return jsonify({'error': 'Missing user_id or new_status'}), 400

        cursor = mysql.connection.cursor()

        # Update the order status for all orders under the user_id
        cursor.execute("""
            UPDATE orders 
            SET order_status = %s, updated_at = NOW() 
            WHERE user_id = %s
        """, (new_status, user_id))
        mysql.connection.commit()

        # If the new status is "Completed", update the sales_count
        if new_status == "Completed":
            cursor.execute("""
                SELECT product_name, SUM(quantity) as total_quantity
                FROM orders
                WHERE user_id = %s AND order_status = 'Completed'
                GROUP BY product_name
            """, (user_id,))
            orders = cursor.fetchall()

            # Increment the sales_count for each product
            for order in orders:
                product_name = order['product_name']
                quantity = order['total_quantity']
                print("Product name",product_name)
                print("Quantity",quantity)

                cursor.execute("""
                    UPDATE menuitems
                    SET sales_count = sales_count + %s
                    WHERE name = %s
                """, (quantity, product_name))
                mysql.connection.commit()

        cursor.close()
        return jsonify({'success': True, 'message': 'Order status updated successfully!'}), 200

    except Exception as e:
        print(f"Error updating order status: {e}")
        return jsonify({'error': f'Failed to update order status: {str(e)}'}), 500

# Admin menu management
@app.route("/admin/menu")
def admin_menu():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM MenuCategories")
    categories = cur.fetchall()
    
    for category in categories:
        cur.execute("SELECT * FROM MenuItems WHERE category_id = %s", [category['id']])
        category['menu_items'] = cur.fetchall()
    
    cur.close()
    return render_template("admin/menu.html", categories=categories)
    
# Add a category to the menu (Admin)
@app.route("/admin/category/add", methods=["POST"])
def add_category():
    name = request.form["name"]
    description = request.form["description"]
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO MenuCategories (name, description) VALUES (%s, %s)", (name, description))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Category added successfully!"}), 201

# Get category details
@app.route("/admin/category/<int:category_id>", methods=["GET"])
def get_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM MenuCategories WHERE id = %s", [category_id])
    category = cur.fetchone()
    cur.close()
    
    if not category:
        return jsonify({"error": "Menu Category not found"}), 404
    
    return jsonify({
        "id": category["id"],
        "name": category["name"],
        "description": category["description"]
    })

# Edit a category
@app.route("/admin/category/edit/<int:category_id>", methods=["POST"])
def edit_category(category_id):
    name = request.form["name"]
    description = request.form["description"]
    cur = mysql.connection.cursor()
    cur.execute("UPDATE MenuCategories SET name = %s, description = %s WHERE id = %s", (name, description, category_id))
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Category updated successfully!"}), 200

# Delete a category
@app.route("/admin/category/delete/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM MenuCategories WHERE id = %s", [category_id])
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Category deleted successfully!"}), 200

# Add a new menu item
@app.route("/admin/menu_item/add", methods=["POST"])
def add_menu_item():
    name = request.form["name"]
    price = request.form["price"]
    discountedPrice = request.form["discountedPrice"]
    preparation_time = request.form["preparation_time"]
    category_id = request.form["category_id"]

    file = request.files["image_url"]
    image_url = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = url_for('static', filename=f'upload/{filename}')

    cur = mysql.connection.cursor()
    cur.execute(
        "INSERT INTO MenuItems (name, price, discounted_price, preparation_time, category_id, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
        (name, price, discountedPrice, preparation_time, category_id, image_url),
    )
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Menu item added successfully!"}), 201

# Edit a menu item
@app.route("/admin/menu_item/edit/<int:item_id>", methods=["POST"])
def edit_menu_item(item_id):
    name = request.form["name"]
    price = request.form["price"]
    discountedPrice = request.form["discountedPrice"]
    preparation_time = request.form["preparation_time"]

    file = request.files["image_url"]
    image_url = ""
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        image_url = url_for('static', filename=f'upload/{filename}')

    cur = mysql.connection.cursor()
    if image_url:
        cur.execute(
            "UPDATE MenuItems SET name = %s, price = %s, discounted_price = %s, preparation_time = %s, image_url = %s WHERE id = %s",
            (name, price, discountedPrice, preparation_time, image_url, item_id),
        )
    else:
        cur.execute(
            "UPDATE MenuItems SET name = %s, price = %s, discounted_price = %s, preparation_time = %s WHERE id = %s",
            (name, price, discountedPrice, preparation_time, item_id),
        )
    mysql.connection.commit()
    cur.close()
    return jsonify({"message": "Menu item updated successfully!"}), 200

# Get a menu item details
@app.route("/admin/menu_item/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM MenuItems WHERE id = %s", [item_id])
    item = cur.fetchone()
    cur.close()
    
    if not item:
        return jsonify({"error": "Menu item not found"}), 404
    
    return jsonify({
        "id": item["id"],
        "name": item["name"],
        "price": item["price"],
        "discountedPrice": item["discounted_price"],
        "preparation_time": item["preparation_time"],
        "image_url": item["image_url"]
    })

@app.route("/admin/menu_item/delete/<int:item_id>", methods=["POST"])
def delete_menu_item(item_id):
    cur = mysql.connection.cursor()
    try:
        cur.execute("DELETE FROM MenuItems WHERE id = %s", [item_id])
        mysql.connection.commit()
        return jsonify({"message": "Menu item deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the menu item."}), 500
    finally:
        cur.close()

@app.route('/checkout')
def checkout():
    if 'temporary_user_id' not in session:
        return redirect('/')  # Redirect if no temporary user ID found

    temporary_user_id = session['temporary_user_id']

    # Fetch cart items for the temporary user
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
    cart_items = cur.fetchall()

    # Fetch categories (if needed)
    cur.execute("SELECT name FROM MenuCategories")
    categories = cur.fetchall()
    cur.close()

    # Calculate total price
    total = sum(item['price'] * item['quantity'] for item in cart_items)

    return render_template('client/checkout.html', 
                           cart_items=cart_items, 
                           total=total, 
                           categories=categories, 
                           hide_footer=True, 
                           hide_header=True,
                           temporary_user_id=temporary_user_id)  # Pass the temporary_user_id to the template

@app.route('/submit_order', methods=['POST'])
def submit_order():
    try:
        # Parse JSON data from the client
        data = request.get_json()
        print(f"Received data: {data}")  # Debugging log

        # Extract fields
        temporary_user_id = session.get('temporary_user_id')
        if not temporary_user_id:
            return jsonify({'success': False, 'error': 'Temporary user ID is missing.'}), 400

        dine_in_takeout = data.get('order_type', None)  # Default to 'Dine In'
        customer_name = data.get('customer_name', None)  # Optional field
        special_requests = data.get('special_requests', None)  # Optional field

        # Fetch cart items for the given user
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT name, price, quantity 
            FROM cart_items 
            WHERE temporary_user_id = %s
        """, (temporary_user_id,))
        cart_items = cursor.fetchall()

        if not cart_items:
            return jsonify({'success': False, 'error': 'No items found in the cart.'}), 400

        # Insert each item into the 'orders' table
        for item in cart_items:
            cursor.execute("""
                INSERT INTO orders (
                    user_id, product_name, price, quantity, order_status, 
                    dine_in_takeout, customer_name, special_requests, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (temporary_user_id, item['name'], item['price'], item['quantity'], 'Pending',
                  dine_in_takeout, customer_name, special_requests))

        # Remove items from the cart for the temporary user
        cursor.execute("""
            DELETE FROM cart_items WHERE temporary_user_id = %s
        """, (temporary_user_id,))

        # Commit changes to the database
        mysql.connection.commit()
        cursor.close()

        # Generate a new session ID
        session['temporary_user_id'] = str(uuid.uuid4())  # Generates a new unique ID

        return jsonify({'success': True, 'new_temporary_user_id': session['temporary_user_id']})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Server error occurred.'}), 500


@app.route("/menu/<category>")
def menu(category):
    try:
        cur = mysql.connection.cursor()

        # Get category ID based on category name
        cur.execute("SELECT id FROM MenuCategories WHERE name = %s", [category])
        category_data = cur.fetchone()

        # Get all categories for the menu navigation
        cur.execute("SELECT name FROM MenuCategories")
        categories = cur.fetchall()

        # If the category doesn't exist, render the menu page with a fallback
        if not category_data:
            return render_template("client/cards.html", categories=categories, menu_items=[], daily_offers_items=[], total=0)

        # Get menu items based on the category ID
        category_id = category_data['id']
        cur.execute("SELECT * FROM MenuItems WHERE category_id = %s", [category_id])
        menu_items = cur.fetchall()

        # Get cart items
        cur.execute("SELECT id, name, price, image_url, quantity FROM cart_items")
        cart_items = cur.fetchall()

        # Calculate total for the cart
        total = sum(cart_item["price"] * cart_item["quantity"] for cart_item in cart_items)

        # Get menu items from 'Daily Offers' only if they are active (is_active = 1)
        cur.execute("""
            SELECT mi.id, mi.name, mi.price, mi.image_url
            FROM MenuItems mi
            JOIN MenuCategories mc ON mi.category_id = mc.id
            WHERE mi.is_active = 1
        """)
        daily_offers_items = cur.fetchall()

        # Get the item with the highest sales count
        cur.execute("""
            SELECT id, name, sales_count
            FROM MenuItems
        """)
        menu_sales = cur.fetchall()

        # Sort the items by sales count in descending order
        sorted_menu_sales = sorted(menu_sales, key=lambda item: item['sales_count'], reverse=True)

        # Get the top 3 items (handle cases where sales counts are the same)
        best_sellers = []
        highest_sales_count = sorted_menu_sales[0]['sales_count']

        # Find all items that match the highest sales count
        for item in sorted_menu_sales:
            if item['sales_count'] == highest_sales_count:
                best_sellers.append(item['id'])
            else:
                break

        # Now, find the second-highest sales count and add items to best_sellers
        if len(best_sellers) < 3:
            second_highest_sales_count = sorted_menu_sales[len(best_sellers)]['sales_count']
            for item in sorted_menu_sales[len(best_sellers):]:
                if item['sales_count'] == second_highest_sales_count:
                    best_sellers.append(item['id'])
                else:
                    break

        # Now, find the third-highest sales count and add items to best_sellers
        if len(best_sellers) < 3:
            third_highest_sales_count = sorted_menu_sales[len(best_sellers)]['sales_count']
            for item in sorted_menu_sales[len(best_sellers):]:
                if item['sales_count'] == third_highest_sales_count:
                    best_sellers.append(item['id'])
                else:
                    break

        # Reset is_bestSeller for all items
        cur.execute("UPDATE MenuItems SET is_bestSeller = 0")

        # Mark the top 3 items (best_sellers) as the best seller
        for best_seller_id in best_sellers:
            cur.execute("""
                UPDATE MenuItems 
                SET is_bestSeller = 1 
                WHERE id = %s
            """, (best_seller_id,))

        # Commit the changes
        mysql.connection.commit()

        # Close cursor
        cur.close()

        # Render the menu page with menu items and categories
        return render_template("client/cards.html", 
                               category=category, 
                               menu_items=menu_items, 
                               categories=categories, 
                               cart_items=cart_items, 
                               total=total, 
                               daily_offers_items=daily_offers_items)
    
    except Exception as e:
        print(f"Error in fetching menu: {e}")
        return render_template("error.html", error="Failed to load menu.")

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    try:
          # Ensure the session has a temporary_user_id
        if 'temporary_user_id' not in session:
            session['temporary_user_id'] = str(uuid.uuid4())  # Generate unique ID

        temporary_user_id = session['temporary_user_id']
        # Get data from the request
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')

        if not name or not price or not image_url:
            return jsonify({'error': 'Missing required fields'}), 400

        # Convert price to float
        try:
            price = float(price)
        except ValueError:
            return jsonify({'error': 'Invalid price value'}), 400

        # Check if item already exists in the cart
        cursor = mysql.connection.cursor()
        cursor.execute("""
            SELECT id, quantity FROM cart_items 
            WHERE name = %s AND image_url = %s AND temporary_user_id = %s
        """, (name, image_url, temporary_user_id))
        existing_item = cursor.fetchone()

        if existing_item:
            # Update quantity if item exists
            new_quantity = existing_item['quantity'] + 1
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, existing_item['id']))
        else:
            # Insert new item if it doesn't exist
            cursor.execute("""
                INSERT INTO cart_items (name, price, image_url, quantity, created_at, temporary_user_id)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (name, price, image_url, 1, temporary_user_id))

        mysql.connection.commit()

        # Fetch updated cart items
        cursor.execute("""
            SELECT id, name, price, image_url, quantity 
            FROM cart_items WHERE temporary_user_id = %s
        """, (temporary_user_id,))
        cart_items = cursor.fetchall()
        cursor.close()

        # Calculate total
        total = sum(item['price'] * item['quantity'] for item in cart_items)

        # Return valid JSON response
        return jsonify({
        'cart_items': cart_items,
        'total': round(total, 2)  # Ensure total is a numeric value with two decimals
        })
    except Exception as e:
        # Print error to server logs for debugging
        print(f"Error: {e}")
        return jsonify({'error': 'Server error occurred'}), 500
    
@app.route('/cart/update/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    try:
        data = request.get_json()
        print(f"Received request to update item_id: {item_id} with data: {data}")
        action = data.get('action')

        # Validate input
        if not action or action not in ['increment', 'decrement']:
            return jsonify({'success': False, 'message': 'Invalid action.'}), 400

        # Get current quantity
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT quantity FROM cart_items WHERE id = %s", (item_id,))
        result = cursor.fetchone()

        if not result:
            return jsonify({'success': False, 'message': 'Item not found in cart.'}), 404

        current_quantity = result["quantity"]

        # Update quantity based on action
        if action == 'increment':
            new_quantity = current_quantity + 1
        elif action == 'decrement':
            new_quantity = current_quantity - 1
        else:
            return jsonify({'success': False, 'message': 'Invalid action.'}), 400

        # Delete the item if the new quantity is 0 or less
        if new_quantity <= 0:
            cursor.execute("DELETE FROM cart_items WHERE id = %s", (item_id,))
        else:
            # Update the database with the new quantity
            cursor.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, item_id))
        mysql.connection.commit()

        # Fetch updated cart items and total
        cursor.execute("SELECT id, name, price, image_url, quantity FROM cart_items")
        cart_items = cursor.fetchall()

        # Calculate total
        total = sum(item["price"] * item["quantity"] for item in cart_items)

        # Format data for response
        formatted_items = [
            {'id': item["id"], 'name': item["name"], 'price': item["price"], 'image_url': item["image_url"], 'quantity': item["quantity"]}
            for item in cart_items
        ]

        return jsonify({'success': True, 'cartItems': formatted_items, 'total': total})

    except Exception as e:
        print(f"Error updating cart: {e}")
        return jsonify({'success': False, 'message': 'An error occurred.'}), 500


@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM cart_items")
        mysql.connection.commit()
        cursor.close()
        return jsonify({'success': True})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500
    
@app.route('/cart_items', methods=['GET'])
def get_cart_items():
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT id, name, price, image_url, quantity FROM cart_items")
        cart_items = cursor.fetchall()
        cursor.close()
        return jsonify({'cart_items': cart_items})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': str(e)}), 500

# Karaoke page
@app.route("/karaoke")
def karaoke():
    cur = mysql.connection.cursor()

    # Get all categories
    cur.execute("SELECT name FROM MenuCategories")
    categories = cur.fetchall()

    # Get menu items from 'Daily Offers' only if they are active (is_active = 1)
    cur.execute("""
        SELECT mi.id, mi.name, mi.price, mi.image_url
        FROM MenuItems mi
        JOIN MenuCategories mc ON mi.category_id = mc.id
        WHERE mc.name = 'Daily Offers' AND mi.is_active = 1
    """)
    daily_offers_items = cur.fetchall()

    # Close cursor
    cur.close()

    return render_template("client/karaoke.html", hide_footer=True, categories=categories, daily_offers_items=daily_offers_items)

if __name__ == "__main__":
    app.run(debug=True)
