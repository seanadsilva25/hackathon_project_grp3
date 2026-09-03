import os
from flask import Blueprint, jsonify, request
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

main = Blueprint("main", __name__)

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

supabase: Client = None
if SUPABASE_URL and SUPABASE_KEY:
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

@main.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend is running"
    })

@main.route("/complaints", methods=["GET"])
def get_complaints():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        response = supabase.table("complaints").select("*").execute()
        return jsonify(response.data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@main.route("/complaints", methods=["POST"])
def create_complaint():
    if not supabase:
        return jsonify({"error": "Supabase not configured"}), 500
    try:
        data = request.json
        # Format the data according to the database schema
        complaint = {
            "latitude": data.get("latitude"),
            "longitude": data.get("longitude"),
            "category": data.get("category"),
            "description": data.get("description"),
            "image_url": data.get("image_url"),
            "status": "pending"
        }
        response = supabase.table("complaints").insert(complaint).execute()
        return jsonify(response.data[0] if response.data else {})
    except Exception as e:
        return jsonify({"error": str(e)}), 500