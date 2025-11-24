from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import date, datetime
from flask_socketio import SocketIO, emit

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'PharmaCheck'
socketio = SocketIO(app, cors_allowed_origins="*")  #alloww frontend connections

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def checkForExpiry(dateString):
    expiry_date = datetime.strptime(dateString, "%Y-%m-%d").date()
    # Get today's date
    today = date.today()
    # Compare and return True if Expiredd, otherwise False
    if today > expiry_date:
        return True
    else:
        return False

@app.route("/admin")
def admin_dashboard():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for("auth"))
    return render_template("admin.html")


@app.route("/pharm")
def pharm_dashboard():
    if "user" not in session or session.get("role") != "Pharmacist":
        return redirect(url_for("auth"))
    return render_template("pharm.html")

@app.route("/report")
def pharm_report():
    if "user" not in session or session.get("role") != "Pharmacist":
        return redirect(url_for("auth"))
    return render_template("pharmReport.html")



# --------------------------
# AUTH PAGES (Frontend)
# --------------------------
@app.route("/auth")
def auth():
    if "user" in session:
        if session.get("role") == "Admin":
            return redirect(url_for("admin_dashboard"))
        elif session.get("role") == "Pharmacist":
            return redirect(url_for("pharm_dashboard"))
    return render_template("auth.html")


# --------------------------
# SIGNUP
# --------------------------
@app.route("/signup", methods=["POST"])
def signup():
    role = request.form.get("role", "Pharmacist")
    license_no = request.form.get("license") if role == "Pharmacist" else None
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        # 1. Create user in Supabase Auth
        user = supabase.auth.sign_up({
            "email": email,
            "password": password,
        })

        # 2. Store extended profile
        supabase.table("profiles").insert({
            "user_id": user.user.id,
            "email": email,
            "license": license_no,
            "role": role
        }).execute()

        flash("Registration successful! Please log in.", "success")
        return redirect(url_for("auth"))

    except Exception as e:
        flash(f"Signup error: {str(e)}", "danger")
        return redirect(url_for("auth"))

# --------------------------
# LOGIN
# --------------------------
@app.route("/login", methods=["POST"])
def login():
    email = request.form.get("email")
    password = request.form.get("password")

    try:
        # 1️⃣ Sign in with Supabase auth
        auth_res = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        user_email = auth_res.user.email

        # 2️⃣ Fetch role from profiles table
        profile = (
            supabase
            .table("profiles")
            .select("role")
            .eq("email", user_email)
            .single()
            .execute()
        )

        role = profile.data["role"]

        # 3️⃣ Store session
        session["user"] = user_email
        session["role"] = role


        # 4️⃣ Redirect based on role
        if role == "Admin":
            return redirect("/admin")
        else:
            return redirect("/pharm")

    except Exception as e:
        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth"))

# --------------------------
# LOGOUT
# --------------------------
@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("auth"))


# --------------------------
# PROTECTED HOME PAGE
# --------------------------
@app.route("/")
def index():
    if "user" not in session:
        return redirect(url_for("auth"))
    return render_template("index.html")

    

# Home route
# @app.route('/')
# def home():
#     return render_template('index.html')  # Make sure you create a templates/index.html file

#  Example API route. 
#  Dw abt this. Just used this to access the data directly so i don't have to login to Supabase everytime
@app.route('/api/verify/data', methods=['GET'])
def get_data():
    response1 = supabase.table("AMOXICILLIN_BATCH").select("*").execute() 
    response2 = supabase.table("AMOXICILLIN_SERIAL").select("*").execute()
    return jsonify({"AMOXICILLIN_BATCH":response1.data,"AMOXICILLIN_SERIAL":response2.data})

@app.route('/api/report/data', methods=['GET'])
def get_data_report():
    response1 = supabase.table("report_page").select("*").execute() 
    return jsonify({"Table Data":response1.data})

# Verify serial/batch numbers here
@app.route('/api/verify', methods=['POST'])
def verify_data():
    user_input = request.json.get('serial')
    response1 = supabase.table("AMOXICILLIN_BATCH").select("*").eq("batch_number", user_input).execute() 
    response2 = supabase.table("AMOXICILLIN_SERIAL").select("*").eq("serial_no", user_input).execute()
    user_email = session["user"]
    #Evaluate cases
    if response1.data:
        for record in response1.data:
            if checkForExpiry(record['expiry_date']):
                return jsonify({"status": "EXPIRED","user":user_email})
            else:
                return jsonify({"status": "AUTHENTIC", "expiryDate": record['expiry_date'], "batch": record['batch_number'], "manufacturer": record['manufacturer'],"user":user_email})
            # print(record['expiry_date'])
    
    elif response2.data:
        for record2 in response2.data:
            response3 = supabase.table("AMOXICILLIN_BATCH").select("*").eq("batch_number", record2['batch_number']).execute() 
            if response3.data:
                for record3 in response3.data:
                    # Convert expiry string to a date object
                    if checkForExpiry(record3['expiry_date']):
                        return jsonify({"status": "EXPIRED","expiryDate": record3['expiry_date'], "batch": record3['batch_number'], "manufacturer": record3['manufacturer'], "serial": record2['serial_no'],"user":user_email})
                    else:
                        return jsonify({"status": "AUTHENTIC", "expiryDate": record3['expiry_date'], "batch": record3['batch_number'], "manufacturer": record3['manufacturer'], "serial": record2['serial_no'],"user":user_email})
            else:
                return jsonify({"status": "COUNTERFEIT","user":user_email})
    else:
        return jsonify({"status": "COUNTERFEIT","user":user_email})


@app.route("/api/report", methods=["POST"])
def add_report():
    data = request.get_json()

    # Extract nested form_data
    form = data.get("form_data", {})

    # Required fields
    product_name = form.get("productName")
    batch_serial = form.get("batchSerial")
    location = form.get("location")
    description = form.get("description")

    # Optional fields
    reporter_name = form.get("reporterName")
    reporter_email = form.get("reporterEmail")

    # --- Validate required fields ---
    if not all([product_name, batch_serial, location, description]):
        return jsonify({"error": "Missing required fields"}), 400
    
    # --- Build record dictionary ---
    record = {
        "product_name": product_name,
        "batch_serial": batch_serial,
        "location": location,
        "description": description
    }

    # Add optional fields only if provided
    if reporter_name:
        record["name"] = reporter_name
    if reporter_email:
        record["email"] = reporter_email

    # --- Insert into Supabase ---
    response = supabase.table("report_page").insert(record).execute()

    # ✅ Check status code instead of .error
    if not response:
        return jsonify({
            "error": f"Supabase insert failed (status {response})"
        }), 400
    return jsonify({
        "message": "Report added successfully!",
        "data": response.data
    }), 201


@app.route("/api/log", methods=["POST"])
def log_transaction():
    data = request.get_json()

    try:
        # Extract fields from incoming JS object
        user_id = data.get("userId")
        serial = data.get("serial")
        status = data.get("status")
        timestamp = data.get("timestamp")

        # Insert into Supabase pharmLogs table
        supabase.table("pharmlogs").insert({
            "user_id": user_id,
            "serial": serial,
            "status": status,
            "timestamp": timestamp,
        }).execute()

        return jsonify({"success": True}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route('/admin/add-records', methods=['GET'])
def add_records():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for("auth"))
    return render_template('addRecords.html')

@app.route('/admin/add-batch', methods=['POST'])
def add_batch():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for("auth"))
    # Extract form data
    batch_number = request.form.get('batch_number')
    manufacturer = request.form.get('manufacturer')
    manufacture_date = request.form.get('manufacture_date')
    expiry_date = request.form.get('expiry_date')
    delivery_date = request.form.get('delivery_date')
    source_distributor = request.form.get('source_distributor')
    
    # Convert dates to ISO format if they exist
    if manufacture_date:
        manufacture_date = manufacture_date  # YYYY-MM-DD from <input type="date">
    if expiry_date:
        expiry_date = expiry_date
    if delivery_date:
        delivery_date = delivery_date  # YYYY-MM-DDTHH:MM from datetime-local input

    # Insert into Supabase table
    data = {
        "batch_number": batch_number,
        "manufacturer": manufacturer,
        "manufacture_date": manufacture_date,
        "expiry_date": expiry_date,
        "delivery_date": delivery_date,
        "source_distributor": source_distributor
    }

    response = supabase.table("AMOXICILLIN_BATCH").insert(data).execute()

    # Check for errors
    if isinstance(response.data, dict) and response.data.get("error"):
        flash(f"Error adding batch {batch_number}: {response.data['error']}", "danger")
    else:
        flash(f"Batch {batch_number} added successfully.", "success")

    return redirect(url_for('add_records'))
 

@app.route('/admin/add-serial', methods=['POST'])
def add_serial():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for("auth"))
    serial_no = request.form.get('serial_no')
    strength_form = request.form.get('strength_form')
    units_per_pack = request.form.get('units_per_pack')
    packs_per_box = request.form.get('packs_per_box')
    pack_type = request.form.get('pack_type')
    batch_number = request.form.get('batch_number')
    
    # Convert numeric inputs
    units_per_pack = int(units_per_pack) if units_per_pack else None
    packs_per_box = int(packs_per_box) if packs_per_box else None

    data = {
        "serial_no": serial_no,
        "strength_form": strength_form,
        "units_per_pack": units_per_pack,
        "packs_per_box": packs_per_box,
        "pack_type": pack_type,
        "batch_number": batch_number
    }

    response = supabase.table("AMOXICILLIN_SERIAL").insert(data).execute()

    if isinstance(response.data, dict) and response.data.get("error"):
        flash(f"Error adding serial {serial_no}: {response.data['error']}", "danger")
    else:
        flash(f"Serial {serial_no} added successfully.", "success")

    return redirect(url_for('add_records'))
    
# #Socket io connection signals
# @socketio.on("connect")
# def handle_connect():
#     print("Client connected")

# @socketio.on("disconnect")
# def handle_disconnect():
#     print("Client disconnected")

# Run the app
if __name__ == '__main__':
    socketio.run(app, debug=True, host="0.0.0.0", port=5000)