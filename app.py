import os
import uuid
from dotenv import load_dotenv
from flask import Flask, render_template, request, jsonify, url_for, session, redirect
import psycopg2
from psycopg2.extras import RealDictCursor
from werkzeug.utils import secure_filename
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your_default_secret_key_here')

# --- Supabase Configuration ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize Supabase Client (for Storage)
# This will now work because load_dotenv() runs first
if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in your .env file")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def get_db_connection():
    conn = psycopg2.connect(DATABASE_URL)
    return conn

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.before_request
def ensure_temp_user_id():
    if 'temporary_user_id' not in session:
        session['temporary_user_id'] = str(uuid.uuid4())

# --- Routes ---

@app.route("/")
def home():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT name FROM menucategories")
        categories = cur.fetchall()

        # In Postgres, TRUE/FALSE is used for boolean. 
        cur.execute("""
            SELECT mi.id, mi.name, mi.price, mi.image_url
            FROM menuitems mi
            JOIN menucategories mc ON mi.category_id = mc.id
            WHERE mc.name = 'Daily Offers' AND mi.is_active = TRUE
        """)
        daily_offers_items = cur.fetchall()
        return render_template("client/index.html", categories=categories, daily_offers_items=daily_offers_items)
    finally:
        cur.close()
        conn.close()

@app.route('/admin/dashboard')
def admin_dashboard():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Total Menus
        cur.execute("SELECT COUNT(*) as count FROM menuitems")
        total_menus = cur.fetchone()['count']

        # Total Orders Today (Postgres uses CURRENT_DATE)
        cur.execute("SELECT COUNT(*) as count FROM orders WHERE DATE(created_at) = CURRENT_DATE")
        total_orders_today = cur.fetchone()['count']

        # Total Clients Today
        cur.execute("SELECT COUNT(DISTINCT user_id) as count FROM orders WHERE DATE(created_at) = CURRENT_DATE")
        total_clients_today = cur.fetchone()['count']

        return render_template('admin/dashboard.html', total_menus=total_menus, total_orders_today=total_orders_today, total_clients_today=total_clients_today)
    except Exception as e:
        print(f"Error loading dashboard: {e}")
        return render_template('error.html', error=f"Failed to load dashboard. Error: {str(e)}")
    finally:
        cur.close()
        conn.close()

@app.route("/admin/dailyOffers")
def daily_offers():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        query = """
            SELECT mi.id, mi.name, mi.price, mi.discounted_price, 
                   mi.image_url, mi.preparation_time, mi.is_active, 
                   mc.description
            FROM menuitems mi
            LEFT JOIN menucategories mc ON mi.category_id = mc.id
        """
        cur.execute(query)
        daily_offers = cur.fetchall()
        return render_template("admin/dailyOffers.html", daily_offers=daily_offers)
    finally:
        cur.close()
        conn.close()

@app.route('/admin/daily-offers/toggle/<int:item_id>', methods=['POST'])
def toggle_offer(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        data = request.get_json()
        is_active = data.get('is_active', False)
        
        # Postgres uses %s placeholder
        cur.execute("""
            UPDATE menuitems
            SET is_active = %s
            WHERE id = %s
        """, (is_active, item_id))
        conn.commit()
        return jsonify({"message": "Offer status updated successfully."})
    except Exception as e:
        return jsonify({"message": "An error occurred while updating the offer status."}), 500
    finally:
        cur.close()
        conn.close()

# Helper function to fetch grouped orders
def fetch_grouped_orders(status_condition):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if isinstance(status_condition, tuple):
             # For 'IN' clause
            query = """
                SELECT id, user_id, product_name, price, quantity, order_status, 
                created_at, updated_at, dine_in_takeout, customer_name, special_requests
                FROM orders WHERE order_status IN %s ORDER BY updated_at DESC
            """
            cur.execute(query, (status_condition,))
        else:
            query = """
                SELECT id, user_id, product_name, price, quantity, order_status, 
                created_at, updated_at, dine_in_takeout, customer_name, special_requests
                FROM orders WHERE order_status = %s
            """
            cur.execute(query, (status_condition,))
            
        orders = cur.fetchall()

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
                'price': float(order['price']),
                'quantity': order['quantity']
            })
            grouped_orders[user_id]['total'] += float(order['price']) * order['quantity']
        return grouped_orders
    finally:
        cur.close()
        conn.close()

@app.route('/admin/AllOrders')
def admin_orders():
    try:
        grouped_orders = fetch_grouped_orders('Pending')
        return render_template('admin/AllOrders.html', grouped_orders=grouped_orders)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error loading orders: {e}", 500

@app.route('/admin/AllOrdersOngoing')
def admin_orders_Ongoing():
    try:
        grouped_orders = fetch_grouped_orders('OnGoing')
        return render_template('admin/AllOrders ongoing.html', grouped_orders=grouped_orders)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error loading orders: {e}", 500

@app.route('/admin/AllOrdersPast')
def admin_orders_Past():
    try:
        grouped_orders = fetch_grouped_orders(('Completed', 'Cancelled'))
        return render_template('admin/AllOrders Past.html', grouped_orders=grouped_orders)
    except Exception as e:
        print(f"Error: {e}")
        return f"Error loading orders: {e}", 500

@app.route('/admin/UpdateOrderStatus', methods=['POST'])
def update_order_status():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        user_id = request.json.get('order_id')
        new_status = request.json.get('new_status')

        if not user_id or not new_status:
            return jsonify({'error': 'Missing user_id or new_status'}), 400

        cur.execute("""
            UPDATE orders 
            SET order_status = %s, updated_at = NOW() 
            WHERE user_id = %s
        """, (new_status, user_id))
        conn.commit()

        if new_status == "Completed":
            cur.execute("""
                SELECT product_name, SUM(quantity) as total_quantity
                FROM orders
                WHERE user_id = %s AND order_status = 'Completed'
                GROUP BY product_name
            """, (user_id,))
            orders = cur.fetchall()

            for order in orders:
                cur.execute("""
                    UPDATE menuitems
                    SET sales_count = sales_count + %s
                    WHERE name = %s
                """, (order['total_quantity'], order['product_name']))
                conn.commit()

        return jsonify({'success': True, 'message': 'Order status updated successfully!'}), 200
    except Exception as e:
        print(f"Error updating order status: {e}")
        return jsonify({'error': f'Failed to update order status: {str(e)}'}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/admin/menu")
def admin_menu():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM menucategories")
        categories = cur.fetchall()
        
        for category in categories:
            cur.execute("SELECT * FROM menuitems WHERE category_id = %s", [category['id']])
            category['menu_items'] = cur.fetchall()
        
        return render_template("admin/menu.html", categories=categories)
    finally:
        cur.close()
        conn.close()

@app.route("/admin/category/add", methods=["POST"])
def add_category():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        name = request.form["name"]
        description = request.form["description"]
        cur.execute("INSERT INTO menucategories (name, description) VALUES (%s, %s)", (name, description))
        conn.commit()
        return jsonify({"message": "Category added successfully!"}), 201
    finally:
        cur.close()
        conn.close()

@app.route("/admin/category/<int:category_id>", methods=["GET"])
def get_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM menucategories WHERE id = %s", [category_id])
        category = cur.fetchone()
        
        if not category:
            return jsonify({"error": "Menu Category not found"}), 404
        
        return jsonify(category)
    finally:
        cur.close()
        conn.close()

@app.route("/admin/category/edit/<int:category_id>", methods=["POST"])
def edit_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        name = request.form["name"]
        description = request.form["description"]
        cur.execute("UPDATE menucategories SET name = %s, description = %s WHERE id = %s", (name, description, category_id))
        conn.commit()
        return jsonify({"message": "Category updated successfully!"}), 200
    finally:
        cur.close()
        conn.close()

@app.route("/admin/category/delete/<int:category_id>", methods=["POST"])
def delete_category(category_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM menucategories WHERE id = %s", [category_id])
        conn.commit()
        return jsonify({"message": "Category deleted successfully!"}), 200
    finally:
        cur.close()
        conn.close()

@app.route("/admin/menu_item/add", methods=["POST"])
def add_menu_item():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        name = request.form["name"]
        price = request.form["price"]
        discountedPrice = request.form["discountedPrice"]
        preparation_time = request.form["preparation_time"]
        category_id = request.form["category_id"]

        file = request.files.get("image_url")
        image_url = ""
        
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # --- SUPABASE STORAGE UPLOAD ---
            file_content = file.read()
            # Upload to 'menu-images' bucket
            res = supabase.storage.from_("menu-images").upload(
                file=file_content,
                path=filename,
                file_options={"content-type": file.content_type, "upsert": "true"}
            )
            # Get Public URL
            image_url = supabase.storage.from_("menu-images").get_public_url(filename)

        cur.execute(
            "INSERT INTO menuitems (name, price, discounted_price, preparation_time, category_id, image_url) VALUES (%s, %s, %s, %s, %s, %s)",
            (name, price, discountedPrice, preparation_time, category_id, image_url),
        )
        conn.commit()
        return jsonify({"message": "Menu item added successfully!"}), 201
    except Exception as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/admin/menu_item/edit/<int:item_id>", methods=["POST"])
def edit_menu_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        name = request.form["name"]
        price = request.form["price"]
        discountedPrice = request.form["discountedPrice"]
        preparation_time = request.form["preparation_time"]

        file = request.files.get("image_url")
        image_url = ""

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_content = file.read()
            res = supabase.storage.from_("menu-images").upload(
                file=file_content,
                path=filename,
                file_options={"content-type": file.content_type, "upsert": "true"}
            )
            image_url = supabase.storage.from_("menu-images").get_public_url(filename)

        if image_url:
            cur.execute(
                "UPDATE menuitems SET name = %s, price = %s, discounted_price = %s, preparation_time = %s, image_url = %s WHERE id = %s",
                (name, price, discountedPrice, preparation_time, image_url, item_id),
            )
        else:
            cur.execute(
                "UPDATE menuitems SET name = %s, price = %s, discounted_price = %s, preparation_time = %s WHERE id = %s",
                (name, price, discountedPrice, preparation_time, item_id),
            )
        conn.commit()
        return jsonify({"message": "Menu item updated successfully!"}), 200
    finally:
        cur.close()
        conn.close()

@app.route("/admin/menu_item/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM menuitems WHERE id = %s", [item_id])
        item = cur.fetchone()
        
        if not item:
            return jsonify({"error": "Menu item not found"}), 404
        
        return jsonify({
            "id": item["id"],
            "name": item["name"],
            "price": float(item["price"]), # Convert Decimal to float for JSON
            "discountedPrice": item["discounted_price"],
            "preparation_time": item["preparation_time"],
            "image_url": item["image_url"]
        })
    finally:
        cur.close()
        conn.close()

@app.route("/admin/menu_item/delete/<int:item_id>", methods=["POST"])
def delete_menu_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("DELETE FROM menuitems WHERE id = %s", [item_id])
        conn.commit()
        return jsonify({"message": "Menu item deleted successfully!"}), 200
    except Exception as e:
        return jsonify({"error": "An error occurred while deleting the menu item."}), 500
    finally:
        cur.close()
        conn.close()

@app.route('/checkout')
def checkout():
    if 'temporary_user_id' not in session:
        return redirect('/')

    temporary_user_id = session['temporary_user_id']
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT * FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
        cart_items = cur.fetchall()

        cur.execute("SELECT name FROM menucategories")
        categories = cur.fetchall()

        total = sum(float(item['price']) * item['quantity'] for item in cart_items)

        return render_template('client/checkout.html', 
                               cart_items=cart_items, 
                               total=total, 
                               categories=categories, 
                               hide_footer=True, 
                               hide_header=True,
                               temporary_user_id=temporary_user_id)
    finally:
        cur.close()
        conn.close()

@app.route('/submit_order', methods=['POST'])
def submit_order():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        data = request.get_json()
        temporary_user_id = session.get('temporary_user_id')
        if not temporary_user_id:
            return jsonify({'success': False, 'error': 'Temporary user ID is missing.'}), 400

        dine_in_takeout = data.get('order_type', 'Dine In')
        customer_name = data.get('customer_name')
        special_requests = data.get('special_requests')

        cur.execute("SELECT name, price, quantity FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
        cart_items = cur.fetchall()

        if not cart_items:
            return jsonify({'success': False, 'error': 'No items found in the cart.'}), 400

        for item in cart_items:
            cur.execute("""
                INSERT INTO orders (
                    user_id, product_name, price, quantity, order_status, 
                    dine_in_takeout, customer_name, special_requests, created_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
            """, (temporary_user_id, item['name'], item['price'], item['quantity'], 'Pending',
                  dine_in_takeout, customer_name, special_requests))

        cur.execute("DELETE FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
        conn.commit()

        session['temporary_user_id'] = str(uuid.uuid4())
        return jsonify({'success': True, 'new_temporary_user_id': session['temporary_user_id']})
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'success': False, 'error': 'Server error occurred.'}), 500
    finally:
        cur.close()
        conn.close()

@app.route("/menu/<category>")
def menu(category):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT id FROM menucategories WHERE name = %s", [category])
        category_data = cur.fetchone()
        
        cur.execute("SELECT name FROM menucategories")
        categories = cur.fetchall()

        if not category_data:
            return render_template("client/cards.html", categories=categories, menu_items=[], daily_offers_items=[], total=0)

        category_id = category_data['id']
        cur.execute("SELECT * FROM menuitems WHERE category_id = %s", [category_id])
        menu_items = cur.fetchall()

        # Temporary user cart
        temporary_user_id = session.get('temporary_user_id')
        cart_items = []
        total = 0
        if temporary_user_id:
            cur.execute("SELECT id, name, price, image_url, quantity FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
            cart_items = cur.fetchall()
            total = sum(float(cart_item["price"]) * cart_item["quantity"] for cart_item in cart_items)

        cur.execute("""
            SELECT mi.id, mi.name, mi.price, mi.image_url
            FROM menuitems mi
            JOIN menucategories mc ON mi.category_id = mc.id
            WHERE mi.is_active = TRUE
        """)
        daily_offers_items = cur.fetchall()

        # Best Sellers Logic (Simplified)
        cur.execute("UPDATE menuitems SET is_bestSeller = FALSE")
        # Find top 3
        cur.execute("SELECT id FROM menuitems ORDER BY sales_count DESC LIMIT 3")
        best_sellers = cur.fetchall()
        for bs in best_sellers:
            cur.execute("UPDATE menuitems SET is_bestSeller = TRUE WHERE id = %s", (bs['id'],))
        conn.commit()

        return render_template("client/cards.html", 
                               category=category, 
                               menu_items=menu_items, 
                               categories=categories, 
                               cart_items=cart_items, 
                               total=total, 
                               daily_offers_items=daily_offers_items)
    except Exception as e:
        print(f"Error: {e}")
        return render_template("error.html", error="Failed to load menu.")
    finally:
        cur.close()
        conn.close()

@app.route('/add_to_cart', methods=['POST'])
def add_to_cart():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        if 'temporary_user_id' not in session:
            session['temporary_user_id'] = str(uuid.uuid4())
        
        temporary_user_id = session['temporary_user_id']
        name = request.form.get('name')
        price = request.form.get('price')
        image_url = request.form.get('image_url')

        cur.execute("""
            SELECT id, quantity FROM cart_items 
            WHERE name = %s AND image_url = %s AND temporary_user_id = %s
        """, (name, image_url, temporary_user_id))
        existing_item = cur.fetchone()

        if existing_item:
            new_quantity = existing_item['quantity'] + 1
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, existing_item['id']))
        else:
            cur.execute("""
                INSERT INTO cart_items (name, price, image_url, quantity, created_at, temporary_user_id)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """, (name, price, image_url, 1, temporary_user_id))
        
        conn.commit()

        cur.execute("SELECT id, name, price, image_url, quantity FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
        cart_items = cur.fetchall()
        
        total = sum(float(item['price']) * item['quantity'] for item in cart_items)

        return jsonify({
            'cart_items': [{**item, 'price': float(item['price'])} for item in cart_items],
            'total': round(total, 2)
        })
    finally:
        cur.close()
        conn.close()

@app.route('/cart/update/<int:item_id>', methods=['POST'])
def update_cart_item(item_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        data = request.get_json()
        action = data.get('action')

        cur.execute("SELECT quantity FROM cart_items WHERE id = %s", (item_id,))
        result = cur.fetchone()

        if not result:
            return jsonify({'success': False, 'message': 'Item not found in cart.'}), 404

        current_quantity = result["quantity"]
        new_quantity = current_quantity + 1 if action == 'increment' else current_quantity - 1

        if new_quantity <= 0:
            cur.execute("DELETE FROM cart_items WHERE id = %s", (item_id,))
        else:
            cur.execute("UPDATE cart_items SET quantity = %s WHERE id = %s", (new_quantity, item_id))
        conn.commit()

        temporary_user_id = session.get('temporary_user_id')
        cur.execute("SELECT id, name, price, image_url, quantity FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
        cart_items = cur.fetchall()
        total = sum(float(item["price"]) * item["quantity"] for item in cart_items)

        return jsonify({
            'success': True, 
            'cartItems': [{**item, 'price': float(item['price'])} for item in cart_items],
            'total': total
        })
    finally:
        cur.close()
        conn.close()

@app.route('/cancel_order', methods=['POST'])
def cancel_order():
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        if 'temporary_user_id' in session:
            cur.execute("DELETE FROM cart_items WHERE temporary_user_id = %s", (session['temporary_user_id'],))
            conn.commit()
        return jsonify({'success': True})
    finally:
        cur.close()
        conn.close()

@app.route('/cart_items', methods=['GET'])
def get_cart_items():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        temporary_user_id = session.get('temporary_user_id')
        if temporary_user_id:
            cur.execute("SELECT id, name, price, image_url, quantity FROM cart_items WHERE temporary_user_id = %s", (temporary_user_id,))
            cart_items = cur.fetchall()
            # Convert decimals to float for JSON serialization
            return jsonify({'cart_items': [{**item, 'price': float(item['price'])} for item in cart_items]})
        return jsonify({'cart_items': []})
    finally:
        cur.close()
        conn.close()

@app.route("/karaoke")
def karaoke():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT name FROM menucategories")
        categories = cur.fetchall()

        cur.execute("""
            SELECT mi.id, mi.name, mi.price, mi.image_url
            FROM menuitems mi
            JOIN menucategories mc ON mi.category_id = mc.id
            WHERE mc.name = 'Daily Offers' AND mi.is_active = TRUE
        """)
        daily_offers_items = cur.fetchall()
        return render_template("client/karaoke.html", hide_footer=True, categories=categories, daily_offers_items=daily_offers_items)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)