import os
import secrets
import time
import bcrypt
import requests
from flask import Blueprint, request, jsonify

auth = Blueprint("auth", __name__)

# Temporary in-memory storage for pending OTPs
# Structure: { phone: { "otp_hash": bytes, "expiry": int, "attempts": int, "last_sent": int } }
pending_registrations = {}

def get_bird_key():
    return os.getenv("BIRD_API_KEY")

def get_bird_originator():
    return os.getenv("BIRD_ORIGINATOR", "UniSafe")

def normalize_phone(phone):
    phone = phone.strip()
    if len(phone) == 10 and not phone.startswith('+'):
        return f"+91{phone}"
    if not phone.startswith('+'):
        return f"+{phone}"
    return phone

def send_bird_sms(phone, otp):
    api_key = get_bird_key()
    if not api_key:
        raise Exception("BIRD_API_KEY not configured in backend/.env")
    
    originator = get_bird_originator()
    message = f"Your UniSafe verification code is {otp}. It expires in 10 minutes."
    
    # We try the modern Bird Workspace API first
    url = "https://api.bird.com/workspaces/default/channels/sms/messages"
    payload = {
        "body": message,
        "originator": originator,
        "receiver": {
            "contacts": [{"identifierValue": phone}]
        }
    }
    headers = {
        "Authorization": f"AccessKey {api_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, json=payload, headers=headers)
    
    # Fallback to classic MessageBird REST API if workspace API is not supported by this key
    if response.status_code in [401, 404, 403]:
        old_url = "https://rest.messagebird.com/messages"
        old_payload = {
            "recipients": [phone],
            "originator": originator,
            "body": message
        }
        old_headers = {
            "Authorization": f"AccessKey {api_key}",
            "Content-Type": "application/json"
        }
        response = requests.post(old_url, json=old_payload, headers=old_headers)
        
    response.raise_for_status()

@auth.route("/register/send-otp", methods=["POST"])
def send_otp():
    data = request.json
    if not data or not data.get("phone"):
        return jsonify({"error": "Phone number is required"}), 400
        
    phone = normalize_phone(data.get("phone"))
    
    # Check cooldown
    if phone in pending_registrations:
        last_sent = pending_registrations[phone].get("last_sent", 0)
        if time.time() - last_sent < 60:
            return jsonify({"error": f"Please wait {int(60 - (time.time() - last_sent))}s before resending"}), 429

    try:
        # Generate cryptographically secure 6 digit OTP
        otp = "".join([str(secrets.randbelow(10)) for _ in range(6)])
        
        # Hash OTP
        otp_hash = bcrypt.hashpw(otp.encode('utf-8'), bcrypt.gensalt())
        
        # Send SMS
        send_bird_sms(phone, otp)
        
        # Store in memory (10 min expiry)
        pending_registrations[phone] = {
            "otp_hash": otp_hash,
            "expiry": int(time.time()) + 600,
            "attempts": 0,
            "last_sent": int(time.time())
        }
        
        return jsonify({"success": True, "message": "OTP sent successfully"})
        
    except Exception as e:
        return jsonify({"error": f"Failed to send SMS: {str(e)}"}), 500

@auth.route("/register/verify-otp", methods=["POST"])
def verify_otp():
    data = request.json
    if not data or not data.get("phone") or not data.get("otp"):
        return jsonify({"error": "Phone and OTP are required"}), 400
        
    phone = normalize_phone(data.get("phone"))
    otp = data.get("otp")
    
    if phone not in pending_registrations:
        return jsonify({"error": "No pending registration found for this phone number."}), 404
        
    record = pending_registrations[phone]
    
    # Check expiry
    if time.time() > record["expiry"]:
        del pending_registrations[phone]
        return jsonify({"error": "The verification code has expired. Request a new code."}), 400
        
    # Check attempts
    if record["attempts"] >= 5:
        del pending_registrations[phone]
        return jsonify({"error": "Too many failed attempts. Request a new code."}), 429
        
    record["attempts"] += 1
    
    # Verify hash
    if not bcrypt.checkpw(otp.encode('utf-8'), record["otp_hash"]):
        return jsonify({"error": "Incorrect verification code. Please try again."}), 400
        
    # Success! Clear OTP
    del pending_registrations[phone]
    
    return jsonify({
        "success": True, 
        "message": "OTP verified successfully. You may now complete registration."
    })

@auth.route("/resend-otp", methods=["POST"])
def resend_otp():
    # It acts identically to send-otp in terms of cooldown and generating a new OTP
    return send_otp()
