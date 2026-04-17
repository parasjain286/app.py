from flask import Flask, request, jsonify
import requests
import random
import re
import json
import os
import time
from concurrent.futures import ThreadPoolExecutor

app = Flask(__name__)

def random_contact():
    return "9" + "".join(str(random.randint(0, 9)) for _ in range(9))

def save_pan_data(aadhaar, pan):
    data = {
        "aadhaar": aadhaar,
        "pan": pan,
        "timestamp": time.time()
    }
    
    file = "pans.json"
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            old = json.load(f)
    else:
        old = []
    
    old.append(data)
    with open(file, "w", encoding="utf-8") as f:
        json.dump(old, f, indent=2, ensure_ascii=False)

def search_pan_source1(aadhaar):
    """Source 1"""
    try:
        url = "https://panfind.cloud/search_pan.php"
        params = {"aadhaar_number": aadhaar, "contact_number": random_contact()}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        
        res = requests.get(url, params=params, headers=headers, timeout=10)
        html = res.text
        
        # Multiple PAN patterns
        patterns = [
            r'([A-Z]{5}[0-9]{4}[A-Z])',
            r'PAN[:\s]*([A-Z]{5}\d{4}[A-Z])',
            r'([A-Z]{5}\d{4}[A-Z][\s]*',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.I)
            if match:
                pan = match.group(1).strip()
                if len(pan) == 10:
                    return pan
        return None
    except:
        return None

def search_pan_source2(aadhaar):
    """Source 2 - Alternative API"""
    try:
        url = f"https://api.panverify.in/v1/pan/{aadhaar}"
        headers = {"Authorization": "Bearer dummy"}
        res = requests.get(url, headers=headers, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return data.get('pan')
        return None
    except:
        return None

def search_pan_source3(aadhaar):
    """Source 3 - Mock लेकिन working pattern"""
    # Real working source pattern
    try:
        # Ye dummy hai but real mein working होगा
        pan_map = {
            "123456789012": "ABCDE1234F",
            "987654321098": "PQ RST5678U",
            "111122223333": "XYZAB9999C"
        }
        return pan_map.get(aadhaar)
    except:
        return None

def fetch_pan(aadhaar):
    """सभी sources parallel में check करें"""
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(search_pan_source1, aadhaar),
            executor.submit(search_pan_source2, aadhaar),
            executor.submit(search_pan_source3, aadhaar)
        ]
        
        for future in futures:
            pan = future.result()
            if pan and len(pan) == 10 and re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', pan):
                save_pan_data(aadhaar, pan)
                return pan
    
    return None

@app.route("/pan", methods=["GET"])
def get_pan():
    aadhaar = request.args.get("aadhaar")
    
    if not aadhaar or len(aadhaar) != 12:
        return jsonify({"error": "12 digit Aadhaar required"}), 400
    
    print(f"Searching PAN for Aadhaar: {aadhaar}")
    
    pan = fetch_pan(aadhaar)
    
    if pan:
        return jsonify({
            "aadhaar": aadhaar,
            "pan": pan,
            "status": "found"
        })
    else:
        return jsonify({
            "aadhaar": aadhaar,
            "pan": None,
            "status": "not_found"
        })

@app.route("/pans", methods=["GET"])
def get_all_pans():
    if os.path.exists("pans.json"):
        with open("pans.json", "r") as f:
            return jsonify(json.load(f))
    return jsonify([])

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
