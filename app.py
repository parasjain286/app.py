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
        json.dump(old, f, indent=4, ensure_ascii=False)

def fetch_pan(aadhaar):
    contact = random_contact()

    url = "https://panfind.cloud/search_pan.php"

    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Referer": "https://panfind.cloud/search_pan.php"
    }

    params = {
        "aadhaar_number": aadhaar,
        "contact_number": contact
    }

    try:
        res = requests.get(url, headers=headers, params=params, timeout=30)
        res.raise_for_status()
        html = res.text

        # Improved Full PAN regex - multiple patterns try करेंगे
        full_pan_patterns = [
            r'Full PAN Number.*?([A-Z]{5}[0-9]{4}[A-Z])',
            r'PAN.*?([A-Z]{5}\d{4}[A-Z])',
            r'([A-Z]{5}[0-9]{4}[A-Z])',
            r'Full.*?PAN.*?([A-Z]{5}\d{4}[A-Z])',
            r'PAN\s*:\s*([A-Z]{5}[0-9]{4}[A-Z])'
        ]
        
        full_pan = None
        for pattern in full_pan_patterns:
            match = re.search(pattern, html, re.I | re.S | re.M)
            if match:
                full_pan = match.group(1).strip()
                break

        # Half PAN हटा दिया गया

        if full_pan:
            save_full_pan({
                "aadhaar_number": aadhaar,
                "contact_number": contact,
                "full_pan": full_pan,
                "timestamp": str(random.randint(1000000000, 2000000000))
            })

        return {
            "aadhaar_number": aadhaar,
            "full_pan": full_pan,
            "status": "success" if full_pan else "no_data"
        }

    except requests.RequestException as e:
        return {
            "aadhaar_number": aadhaar,
            "full_pan": None,
            "error": str(e),
            "status": "error"
        }

@app.route("/pan", methods=["GET"])
def get_pan():
    aadhaar = request.args.get("aadhaar")

    if not aadhaar:
        return jsonify({"error": "aadhaar parameter required"}), 400

    if len(aadhaar) != 12 or not aadhaar.isdigit():
        return jsonify({"error": "Valid 12-digit aadhaar required"}), 400

    result = fetch_pan(aadhaar)
    return jsonify(result)

@app.route("/all_pans", methods=["GET"])
def get_all_pans():
    """सभी saved PANs देखने के लिए"""
    if os.path.exists("pan.json"):
        with open("pan.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return jsonify({"total": len(data), "pans": data})
    return jsonify({"total": 0, "pans": []})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
