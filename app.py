from flask import Flask, request, jsonify
import requests
import random
import re
import json
import os

@app.route('/pan', methods=['GET'])
def get_pan():
    key = request.headers.get('x-api-key') or request.args.get('api_key')

    if key != API_KEY:
        return jsonify({"error": "Unauthorized"}), 401

    aadhaar = request.args.get('aadhaar')
    if not aadhaar:
        return jsonify({"error": "aadhaar parameter required"}), 400

    result = fetch_pan(aadhaar)
    return jsonify(result)

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

    res = requests.get(url, headers=headers, params=params, timeout=30)
    html = res.text

    half_pan = None
    full_pan = None

    half_match = re.search(r'Half PAN.*?([A-Z0-9\*]{10})', html, re.I | re.S)
    if half_match:
        half_pan = half_match.group(1)

    full_match = re.search(r'Full PAN Number.*?([A-Z]{5}[0-9]{4}[A-Z])', html, re.I | re.S)
    if full_match:
        full_pan = full_match.group(1)

    if full_pan:
        save_full_pan({
            "aadhaar_number": aadhaar,
            "full_pan": full_pan
        })

    return {
        "aadhaar_number": aadhaar,
        "half_pan": half_pan,
        "full_pan": full_pan
    }

@app.route("/pan", methods=["GET"])
def get_pan():
    aadhaar = request.args.get("aadhaar")

    if not aadhaar:
        return jsonify({"error": "aadhaar parameter required"}), 400

    result = fetch_pan(aadhaar) 
    return jsonify(result)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
