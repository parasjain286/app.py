from flask import Flask, request, jsonify
import requests
import random
import re
import json
import os

app = Flask(__name__)

def random_contact():
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))

def save_full_pan(data):
    file = "pan.json"

    if os.path.exists(file):
        try:
            with open(file, "r", encoding="utf-8") as f:
                old = json.load(f)
        except:
            old = []
    else:
        old = []

    old.append(data)

    with open(file, "w", encoding="utf-8") as f:
        json.dump(old, f, indent=4)

def fetch_pan(aadhaar):
    contact = random_contact()

    url = "https://panfind.cloud/search_pan.php"

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10)",
        "Accept": "*/*",
        "Referer": "https://panfind.cloud/search_pan.php"
    }

    params = {
        "aadhaar_number": aadhaar,
        "contact_number": contact
    }

    # Sensitive personal-data lookup intentionally disabled
    # Original flow preserved for safe testing/demo
    half_pan = None
    full_pan = None

    demo_response = {
        "demo_mode": True,
        "requested_url": url,
        "params_sent": params,
        "message": "Sensitive lookup disabled. Replace with only lawful, authorized logic for your own records."
    }

    if full_pan:
        save_full_pan({
            "aadhaar_number": aadhaar,
            "full_pan": full_pan
        })

    return {
        "aadhaar_number": aadhaar,
        "half_pan": half_pan,
        "full_pan": full_pan,
        "contact_number_used": contact,
        "debug": demo_response
    }

@app.route("/", methods=["GET"])
def home():
    return jsonify({
        "status": "ok",
        "message": "Server is running"
    })

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy"
    })

@app.route("/pan", methods=["GET"])
def get_pan():
    aadhaar = request.args.get("aadhaar")

    if not aadhaar:
        return jsonify({"error": "aadhaar parameter required"}), 400

    try:
        result = fetch_pan(aadhaar)
        return jsonify(result)
    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500
