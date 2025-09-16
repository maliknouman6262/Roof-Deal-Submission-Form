import os
import mysql.connector
from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from werkzeug.utils import secure_filename
from datetime import datetime
import json

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Aapke diye hue credentials ke mutabiq
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '123@Malik',
    'database': 'roof_deals_db'
}

# Email Configuration - Update these with your SMTP details
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Change this to your SMTP server
    'smtp_port': 587,
    'email': 'your-email@gmail.com',  # Change this to your email
    'password': 'your-app-password',  # Change this to your app password
    'recipient_emails': [
        'recipient1@example.com',
        'recipient2@example.com'
    ]
}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    """MySQL database se connection banata hai."""
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        print("Database connection successful!")
        return conn
    except mysql.connector.Error as err:
        print(f"Error connecting to MySQL: {err}")
        return None

def init_db():
    """Database aur table ko banata hai, agar maujood na ho."""
    conn = get_db_connection()
    if conn is None:
        return
    
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS roof_deals (
            id INT AUTO_INCREMENT PRIMARY KEY,
            
            -- Customer Information
            customer_name VARCHAR(255) NOT NULL,
            address TEXT NOT NULL,
            phone VARCHAR(255) NOT NULL,
            email VARCHAR(255) NOT NULL,
            
            -- Financing
            financing_type VARCHAR(50) NOT NULL,
            deposit_amount DECIMAL(10, 2),
            payment_method VARCHAR(50),
            check_number VARCHAR(255),
            auth_number VARCHAR(255),
            confirm_number VARCHAR(255),
            credit_amount DECIMAL(10, 2),
            bank_details TEXT,
            lender_name VARCHAR(255),
            loan_number VARCHAR(255),
            
            -- Roof Details
            roof_type VARCHAR(50) NOT NULL,
            roof_material_type VARCHAR(50),
            tamko_line VARCHAR(255),
            tamko_color VARCHAR(255),
            roof_pitch VARCHAR(50) NOT NULL,
            custom_rise INT,
            sold_squares INT NOT NULL,
            layers_to_remove TEXT,
            damage_type VARCHAR(50),
            insurance_claim VARCHAR(50) NOT NULL,
            insurance_name VARCHAR(255),
            insurance_phone VARCHAR(255),
            policy_number VARCHAR(255),
            claim_number VARCHAR(255),
            adjuster_info TEXT,
            
            -- Contract
            contract_source VARCHAR(50) NOT NULL,
            opensign_id VARCHAR(255),
            opensign_status VARCHAR(50),
            opensign_link TEXT,
            
            -- Survey & Notes
            survey_date DATE, -- Updated: NOT NULL hata diya
            survey_slot VARCHAR(50),
            needs_scheduling BOOLEAN,
            notes TEXT,
            media_consent BOOLEAN,
            
            -- File paths
            check_front_photo TEXT,
            check_rear_photo TEXT,
            coverage_doc TEXT,
            binder_doc TEXT,
            contract_pdf TEXT,
            front_photo TEXT,
            rear_photo TEXT,
            left_photo TEXT,
            right_photo TEXT,
            sign_photo TEXT,
            
            -- Metadata
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Server start hone par database initialize karen
init_db()

@app.route('/')
def index():
    """Serve the HTML form"""
    with open('index.html', 'r', encoding='utf-8') as f:
        html_content = f.read()
    return render_template_string(html_content)

@app.route('/submit-roof-deal', methods=['POST'])
def submit_roof_deal():
    try:
        data = request.form.to_dict()
        files = request.files
        file_paths = {}

        # Save uploaded files
        upload_dir = "uploads"
        os.makedirs(upload_dir, exist_ok=True)

        for field in ['checkFrontPhoto', 'checkRearPhoto', 'coverageDoc', 'binderDoc',
                      'contractPDF', 'frontPhoto', 'rearPhoto', 'leftPhoto', 'rightPhoto', 'signPhoto']:
            if field in files and files[field]:
                filename = datetime.now().strftime("%Y%m%d%H%M%S_") + files[field].filename
                filepath = os.path.join(upload_dir, filename)
                files[field].save(filepath)
                file_paths[field] = filepath
            else:
                file_paths[field] = ''
                
        conn = get_db_connection()
        if conn is None:
            return jsonify({"status": "error", "message": "Database connection failed"}), 500
        
        cursor = conn.cursor()

        sql = '''
            INSERT INTO roof_deals (
                customer_name, address, phone, email,
                financing_type, deposit_amount, payment_method, check_number,
                auth_number, confirm_number, credit_amount, bank_details,
                lender_name, loan_number,
                roof_type, roof_material_type, tamko_line, tamko_color,
                roof_pitch, custom_rise, sold_squares, layers_to_remove,
                damage_type, insurance_claim, insurance_name, insurance_phone,
                policy_number, claim_number, adjuster_info,
                contract_source, opensign_id, opensign_status, opensign_link,
                survey_date, survey_slot, needs_scheduling, notes, media_consent,
                check_front_photo, check_rear_photo, coverage_doc, binder_doc,
                contract_pdf, front_photo, rear_photo, left_photo, right_photo, sign_photo
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''
        
        survey_date_value = data.get('surveyDate', '')
        # Agar survey date khaali hai, to usse None set karen
        if not survey_date_value:
            survey_date_value = None
            
        values = (
            data.get('customerName', ''),
            data.get('address', ''),
            data.get('phone', ''),
            data.get('email', ''),
            data.get('financingType', ''),
            float(data.get('depositAmount', 0)) if data.get('depositAmount') else None,
            data.get('paymentMethod', ''),
            data.get('checkNumber', ''),
            data.get('authNumber', ''),
            data.get('confirmNumber', ''),
            float(data.get('creditAmount', 0)) if data.get('creditAmount') else None,
            data.get('bankDetails', ''),
            data.get('lenderName', ''),
            data.get('loanNumber', ''),
            data.get('roofType', ''),
            data.get('roofMaterialType', ''),
            data.get('tamkoLineSelect', ''),
            data.get('tamkoColor', ''),
            data.get('roofPitch', ''),
            int(data.get('customRise', 0)) if data.get('customRise') else None,
            int(data.get('soldSquares', 0)) if data.get('soldSquares') else 0,
            data.get('layers', ''),
            data.get('damageType', ''),
            data.get('insuranceClaim', ''),
            data.get('insuranceName', ''),
            data.get('insurancePhone', ''),
            data.get('policyNumber', ''),
            data.get('claimNumber', ''),
            data.get('adjusterInfo', ''),
            data.get('contractSource', ''),
            data.get('openSignID', ''),
            data.get('openSignStatus', ''),
            data.get('openSignLink', ''),
            survey_date_value, # Updated: Yahan value pass ki
            data.get('surveySlot', ''),
            1 if data.get('needsScheduling') == 'on' else 0,
            data.get('notes', ''),
            1 if data.get('mediaConsent') == 'on' else 0,
            file_paths.get('checkFrontPhoto', ''),
            file_paths.get('checkRearPhoto', ''),
            file_paths.get('coverageDoc', ''),
            file_paths.get('binderDoc', ''),
            file_paths.get('contractPDF', ''),
            file_paths.get('frontPhoto', ''),
            file_paths.get('rearPhoto', ''),
            file_paths.get('leftPhoto', ''),
            file_paths.get('rightPhoto', ''),
            file_paths.get('signPhoto', '')
        )
        
        cursor.execute(sql, values)
        deal_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Email notification
        # send_email_notification(data, file_paths, deal_id)

        return jsonify({"status": "success", "message": f"Roof deal submitted successfully! Deal ID: {deal_id}"})

    except Exception as e:
        print("Error in submit_roof_deal:", str(e))
        return jsonify({"status": "error", "message": str(e)})


def send_email_notification(data, file_paths, deal_id):
    """Send email notification with form data"""
    
    # Create email content
    subject = f"New Roof Deal Submission - Deal ID: {deal_id}"
    
    body = f"""
    New Roof Deal Submission - Deal ID: {deal_id}
    Submitted on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    CUSTOMER INFORMATION:
    Name: {data.get('customerName', 'N/A')}
    Address: {data.get('address', 'N/A')}
    Phone: {data.get('phone', 'N/A')}
    Email: {data.get('email', 'N/A')}
    
    FINANCING:
    Type: {data.get('financingType', 'N/A')}
    Deposit Amount: ${data.get('depositAmount', '0')}
    Payment Method: {data.get('paymentMethod', 'N/A')}
    
    ROOF DETAILS:
    Type: {data.get('roofType', 'N/A')}
    Material: {data.get('roofMaterialType', 'N/A')}
    Tamko Line: {data.get('tamkoLineSelect', 'N/A')}
    Color: {data.get('tamkoColor', 'N/A')}
    Pitch: {data.get('roofPitch', 'N/A')}
    Squares: {data.get('soldSquares', 'N/A')}
    Insurance Claim: {data.get('insuranceClaim', 'N/A')}
    
    SURVEY:
    Date: {data.get('surveyDate', 'N/A')}
    Time Slot: {data.get('surveySlot', 'N/A')}
    
    NOTES:
    {data.get('notes', 'No notes provided')}
    
    Files uploaded: {len(file_paths)} files
    """
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = EMAIL_CONFIG['email']
    msg['To'] = ', '.join(EMAIL_CONFIG['recipient_emails'])
    msg['Subject'] = subject
    
    # Add body to email
    msg.attach(MIMEText(body, 'plain'))
    
    # Attach files
    for file_field, file_path in file_paths.items():
        if os.path.exists(file_path):
            with open(file_path, "rb") as attachment:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(attachment.read())
            
            encoders.encode_base64(part)
            part.add_header(
                'Content-Disposition',
                f'attachment; filename= {os.path.basename(file_path)}',
            )
            msg.attach(part)
    
    # Send email
    server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
    server.starttls()
    server.login(EMAIL_CONFIG['email'], EMAIL_CONFIG['password'])
    text = msg.as_string()
    server.sendmail(EMAIL_CONFIG['email'], EMAIL_CONFIG['recipient_emails'], text)
    server.quit()

@app.route('/view-deals')
def view_deals():
    """View all deals in browser"""
    try:
        conn = get_db_connection()
        if conn is None:
            return "<h1>Error: Database connection failed</h1>"
        cursor = conn.cursor(dictionary=True)
        
        cursor.execute('SELECT * FROM roof_deals ORDER BY created_at DESC')
        deals = cursor.fetchall()
        conn.close()
        
        # Simple HTML to display data
        html = """
        <html>
        <head>
            <title>Roof Deals Database</title>
            <style>
                body { font-family: Arial; margin: 20px; }
                table { border-collapse: collapse; width: 100%; }
                th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
                th { background-color: #f2f2f2; }
                .record { margin-bottom: 20px; padding: 15px; border: 1px solid #ccc; }
            </style>
        </head>
        <body>
            <h1>Roof Deals Database (Total: """ + str(len(deals)) + """)</h1>
            <a href="/">← Back to Form</a><br><br>
        """
        
        if deals:
            for deal in deals:
                html += f"""
                <div class="record">
                    <h3>🏠 Deal #{deal['id']} - {deal['customer_name']}</h3>
                    <strong>Contact:</strong> {deal['phone']} | {deal['email']}<br>
                    <strong>Address:</strong> {deal['address']}<br>
                    <strong>Roof:</strong> {deal['roof_type']} | {deal['sold_squares']} squares<br>
                    <strong>Financing:</strong> {deal['financing_type']}<br>
                    <strong>Survey:</strong> {deal['survey_date']} - {deal['survey_slot']}<br>
                    <strong>Submitted:</strong> {deal['created_at']}<br>
                    <strong>Notes:</strong> {deal['notes'] or 'None'}
                </div>
                """
        else:
            html += "<p>No deals submitted yet!</p>"
            
        html += """
            </body>
        </html>
        """
        
        return html
        
    except Exception as e:
        return f"<h1>Error: {str(e)}</h1>"

@app.route('/get-deals', methods=['GET'])
def get_deals():
    """Get all deals from database"""
    try:
        conn = get_db_connection()
        if conn is None:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor = conn.cursor(dictionary=True)
        cursor.execute('SELECT * FROM roof_deals ORDER BY created_at DESC')
        deals = cursor.fetchall()
        
        conn.close()
        
        return jsonify({
            'success': True,
            'deals': deals
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error: {str(e)}'
        }), 500

if __name__ == '__main__':
    init_db()
    print("Database initialized!")
    print("Starting Flask server...")
    print("Make sure to update EMAIL_CONFIG with your SMTP details!")
    app.run(debug=True, host='0.0.0.0', port=5000)