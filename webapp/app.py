from flask import Flask, request, jsonify, render_template, redirect, session, url_for, flash, send_file, render_template_string, request
from flask_cors import CORS
from supabase import create_client, Client
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta, date
import io
from collections import defaultdict
import random
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'PharmaCheck'

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
    session.pop("user", None)
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

        flash("Registration successful! Please confirm your email then log in.", "success")
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
            flash("Pharmacist login successful!", "success")
            return redirect("/pharm")

    except Exception as e:
        flash("Invalid email or password.", "danger")
        return redirect(url_for("auth"))

# --------------------------
# LOGOUT
# --------------------------
@app.route("/logout")
def logout():
    if "user" in session:
        session.pop("user", None)
        flash(f"Logged out successfully! ", "success")
        return redirect(url_for("auth"))
    else:
        return redirect(url_for("auth"))


# --------------------------
# PROTECTED HOME PAGE
# --------------------------
@app.route("/")
def index():
    # if "user" not in session:
    #     return redirect(url_for("auth"))
    return redirect(url_for("auth"))

    
#  Dw abt this. Just used this to access the data directly so i don't have to login to Supabase everytime
# @app.route('/api/verify/data', methods=['GET'])
# def get_data():
#     response1 = supabase.table("AMOXICILLIN_BATCH").select("*").execute() 
#     response2 = supabase.table("AMOXICILLIN_SERIAL").select("*").execute()
#     return jsonify({"AMOXICILLIN_BATCH":response1.data,"AMOXICILLIN_SERIAL":response2.data})

# @app.route('/api/report/data', methods=['GET'])
# def get_data_report():
#     response1 = supabase.table("report_page").select("*").execute() 
#     return jsonify({"Table Data":response1.data})

# Verify serial/batch numbers here
@app.route('/api/verify', methods=['POST'])
def verify_data():
    if "user" not in session:
        return redirect(url_for(request.referrer))
    user_input = request.json.get('serial')
    response1 = supabase.table("AMOXICILLIN_BATCH").select("*").eq("batch_number", user_input).execute() 
    response2 = supabase.table("AMOXICILLIN_SERIAL").select("*").eq("serial_no", user_input).execute()
    user_email = session["user"]
    #Evaluate cases
    if response1.data:
        for record in response1.data:
            if checkForExpiry(record['expiry_date']):
                return jsonify({"status": "EXPIRED","expiryDate": record['expiry_date'], "batch": record['batch_number'], "manufacturer": record['manufacturer'],"user":user_email})
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
    if "user" not in session:
        return redirect(url_for(request.referrer))
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

    
    flash(f"Report added successfully! ", "success")
    return jsonify({
        "message": "Report added successfully!",
        "data": response.data
    }), 201


@app.route("/api/log", methods=["POST"])
def log_transaction():
    if "user" not in session:
        return redirect(url_for("auth"))
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
        return redirect(url_for(request.referrer))
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
    

""" ADMIN REPORTS """
# -------------------------------
# Pharmacy Vericication Queries report
# -------------------------------

def get_logs_from_db(start_date_str, end_date_str):
    """
    Fetches raw log data from the database within the specified time frame.

    NOTE: This is the critical function you must implement using your Supabase client.
    """
    # 1. Parse date strings into datetime objects
    try:
        # Flask is sending YYYY-MM-DD
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        # Include the entire end day
        end_date = end_date.replace(hour=23, minute=59, second=59)
    except ValueError:
        print("Error parsing date inputs.")
        return []

    # --- SUPABASE INTEGRATION POINT (IMPLEMENTATION REQUIRED) ---
    raw_logs = []
    if supabase:
        try:
            # Use the schema specified by the user: 'pharmlogs'
            response = supabase.table('pharmlogs') \
                .select('serial, status, timestamp') \
                .gte('timestamp', start_date.isoformat()) \
                .lte('timestamp', end_date.isoformat()) \
                .execute()

            # Supabase responses need to be parsed, usually response.data
            raw_logs = response.data
        except Exception as e:
            print(f"Supabase query failed: {e}")
            raw_logs = []
    else:
        print("Supabase client not initialized. Returning empty data.")

    # IMPORTANT: The database returns timestamps as strings.
    # We must convert them back to datetime objects for aggregation logic.
    # Assuming the timestamp format is 'YYYY-MM-DD HH:MM:SS.mmm' or 'YYYY-MM-DDTHH:MM:SS+00:00'
    for log in raw_logs:
        if isinstance(log['timestamp'], str):
            try:
                # Attempt to parse common ISO formats returned by Supabase
                log['timestamp'] = datetime.fromisoformat(log['timestamp'].replace('Z', '+00:00'))
            except ValueError:
                # Fallback for simpler format like 'YYYY-MM-DD HH:MM:SS.mmm'
                try:
                    log['timestamp'] = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S.%f')
                except:
                    # Fallback for format 'YYYY-MM-DD HH:MM:SS'
                    log['timestamp'] = datetime.strptime(log['timestamp'], '%Y-%m-%d %H:%M:%S')

    return raw_logs
    # --- END SUPABASE INTEGRATION POINT ---


def aggregate_log_data(raw_logs):
    """
    Aggregates raw log data by serial number to count frequencies and statuses.
    Also returns total counts for queries, authentic, counterfeit, and expired statuses.
    """
    # Key: serial number, Value: aggregation object
    report_data = defaultdict(lambda: {
        'serial': '',
        'total_queries': 0,
        'authentic_count': 0,
        'counterfeit_count': 0,
        'expired_count': 0,
        'other_count': 0,
        'last_query_timestamp': datetime.min
    })

    # Total aggregates
    total_queries = 0
    authentic_count = 0
    counterfeit_count = 0
    expired_count = 0

    for log in raw_logs:
        serial = log['serial']
        status = log['status']
        timestamp = log['timestamp']

        entry = report_data[serial]
        entry['serial'] = serial
        entry['total_queries'] += 1
        total_queries += 1

        # Count status frequencies
        if status.upper() == 'AUTHENTIC':
            entry['authentic_count'] += 1
            authentic_count += 1
        elif status.upper() == 'COUNTERFEIT':
            entry['counterfeit_count'] += 1
            counterfeit_count += 1
        elif status.upper() == 'EXPIRED':
            entry['expired_count'] += 1
            expired_count += 1
        else:
            entry['other_count'] += 1

        # Track the latest query time (Note: timestamp should be a datetime object here)
        if timestamp > entry['last_query_timestamp']:
            entry['last_query_timestamp'] = timestamp

    # Convert dictionary values to a list and format timestamps for JSON
    final_report = list(report_data.values())
    for item in final_report:
        # Convert datetime objects to string for JSON serialization
        if item['last_query_timestamp'] != datetime.min:
            item['last_query_timestamp'] = item['last_query_timestamp'].strftime('%Y-%m-%d %H:%M:%S')
        else:
            item['last_query_timestamp'] = None

    # Return aggregates along with the detailed report data
    return final_report, {
        "total_queries": total_queries,
        "authentic_count": authentic_count,
        "counterfeit_count": counterfeit_count,
        "expired_count": expired_count,
    }


@app.route('/api/report', methods=['GET'])
def get_report_data():
    """Endpoint to fetch and return aggregated log data as JSON."""
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for(request.referrer))
    else:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if not start_date or not end_date:
            return jsonify({"error": "Start and end dates are required."}), 400

        raw_logs = get_logs_from_db(start_date, end_date)
        aggregated_data, summary = aggregate_log_data(raw_logs)

        return jsonify({
            "reportData": aggregated_data,
            "summary": summary
        })


@app.route('/api/generate_pdf', methods=['POST'])
def generate_pdf_report():
    """
    Endpoint to generate a PDF report from the aggregated data.
    """
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for(request.referrer))
    else:
        # 1. Get the JSON data sent from the client
        data = request.get_json()
        if not data or 'reportData' not in data:
            return jsonify({"error": "No report data provided."}), 400

        report_data = data['reportData']
        start_date = data.get('startDate', 'N/A')
        end_date = data.get('endDate', 'N/A')

        # Calculate summary data
        total_queries = sum(row.get("total_queries", 0) for row in report_data)
        authentic_count = sum(row.get("authentic_count", 0) for row in report_data)
        counterfeit_count = sum(row.get("counterfeit_count", 0) for row in report_data)
        expired_count = sum(row.get("expired_count", 0) for row in report_data)

        # --- PDF GENERATION LOGIC (Example using ReportLab concept) ---
        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, title="Verification Log Report")
            styles = getSampleStyleSheet()
            elements = []

            # -----------------------------------------------------
            # 1. PHARMACHECK TEXT LOGO
            # -----------------------------------------------------
            logo_style = ParagraphStyle(
                name="LogoStyle",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",
                fontSize=22,
                textColor=colors.HexColor("#2A6A50"),  # Logo color
                alignment=1,
            )

            elements.append(Paragraph("Pharmacheck", logo_style))
            elements.append(Spacer(1, 18))

            # -----------------------------------------------------
            # 2. TITLE + DATE PERIOD
            # -----------------------------------------------------
            elements.append(Paragraph("Pharmacy Query Log Report", styles["Title"]))
            elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"]))

            # -----------------------------------------------------
            # 3. SUMMARY SECTION (New Section Added)
            # -----------------------------------------------------
            elements.append(Spacer(1, 18))  # Space before the summary section
            summary_text = f"""
                <b>Total Queries:</b> {total_queries}<br/>
                <b>Authentic Queries:</b> {authentic_count}<br/>
                <b>Counterfeit Queries:</b> {counterfeit_count}<br/>
                <b>Expired Queries:</b> {expired_count}
            """
            elements.append(Paragraph(summary_text, styles["Normal"]))

            # Add space before table
            elements.append(Spacer(1, 24))

            # -----------------------------------------------------
            # 4. TABLE DATA
            # -----------------------------------------------------
            table_headers = [
                "Serial No.",
                "Total Queries",
                "Authentic Count",
                "Counterfeit Count",
                "Expired Count",
                "Last Query"
            ]

            table_rows = [table_headers]

            for row in report_data:
                table_rows.append([
                    row.get("serial", ""),
                    str(row.get("total_queries", "")),
                    str(row.get("authentic_count", "")),
                    str(row.get("counterfeit_count", "")),
                    str(row.get("expired_count", "")),
                    row.get("last_query_timestamp") or ""
                ])

            # -----------------------------------------------------
            # 5. TABLE STYLE
            # -----------------------------------------------------
            if len(table_rows) > 1:

                table = Table(table_rows)

                header_bg = colors.HexColor("#12B981")  # Your green

                table.setStyle(TableStyle([
                    # HEADER
                    ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                    ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                    ("FONTSIZE", (0, 0), (-1, 0), 11),
                    ("TOPPADDING", (0, 0), (-1, 0), 6),
                    ("BOTTOMPADDING", (0, 0), (-1, 0), 6),

                    # BODY
                    ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                    ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                    ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                    ("FONTSIZE", (0, 1), (-1, -1), 10),
                    ("ALIGN", (0, 1), (-1, -1), "CENTER"),

                    # GRID
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

                    # Padding
                    ("LEFTPADDING", (0, 0), (-1, -1), 6),
                    ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                    ("TOPPADDING", (0, 1), (-1, -1), 4),
                    ("BOTTOMPADDING", (0, 1), (-1, -1), 4),
                ]))

                elements.append(table)

            else:
                elements.append(Paragraph(
                    "No data available for the selected time frame.",
                    styles["Normal"]
                ))

            # -----------------------------------------------------
            # 6. FINALIZE PDF
            # -----------------------------------------------------
            doc.build(elements)
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype='application/pdf',
                as_attachment=True,
                download_name=f'pharm_log_report_{start_date}_to_{end_date}.pdf'
            )

        except ImportError:
            # Fallback if ReportLab is not installed
            print("ReportLab library not found. PDF generation not supported.")
            return jsonify({"error": "PDF generation library (e.g., ReportLab) is not installed on the server."}), 500
        except Exception as e:
            print(f"An error occurred during PDF generation: {e}")
            return jsonify({"error": f"Failed to generate PDF: {str(e)}"}), 500

@app.route('/admin/reports/queries')
def admin_reports():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for('auth'))
    else:
        return render_template("admin_reports.html")

# -------------------------------
# Pharmacy Reported Drugs report
# -------------------------------
# Fetch rows directly from report_page
# -------------------------------

def get_reports_from_db(start_date_str, end_date_str):
    try:
        # Parse the input date strings into datetime objects
        start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    except ValueError:
        print("Date parsing failed")
        return []

    try:
        # Normalize the start_date to the beginning of the day (00:00:00)
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        # Normalize the end_date to the end of the day (23:59:59)
        end_date = end_date.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        # Query the database for records within the date range
        response = supabase.table("report_page") \
            .select("product_name, batch_serial, location, description, email, created_at") \
            .gte("created_at", start_date.isoformat()) \
            .lte("created_at", end_date.isoformat()) \
            .execute()

        # Return the data or an empty list if no data is found
        return response.data or []

    except Exception as e:
        print(f"Supabase query error: {e}")
        return []

# -------------------------------
# API returns JSON list
# -------------------------------
@app.route("/api/report2", methods=["GET"])
def get_report_data2():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for(request.referrer))
    else:
        start_date = request.args.get("start_date")
        end_date = request.args.get("end_date")

        if not start_date or not end_date:
            return jsonify({"error": "Start and end dates required"}), 400

        rows = get_reports_from_db(start_date, end_date)

        # Format timestamps
        for row in rows:
            if "created_at" in row and isinstance(row["created_at"], str):
                row["created_at"] = row["created_at"].replace("T", " ").split("+")[0]

        return jsonify(rows)

# -------------------------------
# PDF GENERATION
# -------------------------------
@app.route("/api/generate_pdf_2", methods=["POST"])
def generate_pdf_report_2():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for(request.referrer))
    else:
        data = request.get_json()
        if not data or "reportData" not in data:
            return jsonify({"error": "No report data provided"}), 400

        report_data = data["reportData"]
        start_date = data.get("startDate", "N/A")
        end_date = data.get("endDate", "N/A")

        try:
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=letter, title="Report Page Export")
            styles = getSampleStyleSheet()
            elements = []


            # -----------------------------------------------------
            # TEXT LOGO AT TOP
            # -----------------------------------------------------
            logo_style = ParagraphStyle(
                name="LogoStyle",
                parent=styles["Normal"],
                fontName="Helvetica-Oblique",       # Italic
                fontSize=22,
                textColor=colors.HexColor("#2A6A50"),
                alignment=1,
            )

            logo_paragraph = Paragraph("Pharmacheck", logo_style)
            elements.append(logo_paragraph)
            elements.append(Spacer(1, 18))   # Space under logo


            # Title
            elements.append(Paragraph("Report Page Export", styles["Title"]))
            elements.append(Paragraph(f"Period: {start_date} to {end_date}", styles["Normal"]))
            elements.append(Paragraph("<br/>", styles["Normal"]))

            # Extra spacing before table
            elements.append(Spacer(1, 24))

            # Table headers
            headers = ["Product Name", "Batch/Serial No", "Location", "Description", "Email", "Created At"]
            rows = [headers]

            # Table rows
            for r in report_data:
                rows.append([
                    r.get("product_name", ""),
                    r.get("batch_serial", ""),
                    r.get("location", ""),
                    r.get("description", ""),
                    r.get("email", ""),
                    r.get("created_at", "")
                ])

            table = Table(rows)
            
            # Header color you wanted
            header_bg = colors.HexColor("#12B981")

            # -----------------------------------------------------
            # TABLE STYLE
            # -----------------------------------------------------
            table.setStyle(TableStyle([
                # HEADER
                ("BACKGROUND", (0, 0), (-1, 0), header_bg),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("ALIGN", (0, 0), (-1, 0), "CENTER"),
                ("FONTSIZE", (0, 0), (-1, 0), 11),

                # BODY
                ("BACKGROUND", (0, 1), (-1, -1), colors.white),
                ("TEXTCOLOR", (0, 1), (-1, -1), colors.black),
                ("FONTNAME", (0, 1), (-1, -1), "Helvetica"),
                ("FONTSIZE", (0, 1), (-1, -1), 10),

                # GRID
                ("GRID", (0, 0), (-1, -1), 0.5, colors.black),

                # Padding for readability
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))

            elements.append(table)
            doc.build(elements)
            buffer.seek(0)

            return send_file(
                buffer,
                mimetype="application/pdf",
                as_attachment=True,
                download_name=f"report_page_{start_date}_to_{end_date}.pdf"
            )

        except Exception as e:
            print(e)
            return jsonify({"error": f"PDF error: {str(e)}"}), 500

@app.route('/admin/reports/pharmReports', methods=['GET'])
def admin_reports2():
    if "user" not in session or session.get("role") != "Admin":
        return redirect(url_for('auth'))
    else:
        return render_template("admin_reports2.html")



# Run the app
if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)