from flask import Flask, Response
from F1Scaper import getWDC, getWCC
import json
import shutil
import os
from dotenv import load_dotenv
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize Supabase client using environment variables
url = os.getenv("SUPABASE_URL")
key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not url or not key:
    raise Exception("Missing Supabase environment variables.")

supabase = create_client(url, key)

def save_to_supabase(all_data):
    # Insert the JSON data into your table (must exist in Supabase)
    response = supabase.table('f1_data').insert({"data": all_data}).execute()
    if response.error:
        print("Error inserting data:", response.error)
    else:
        print("Data inserted successfully")

def save_data():
    wdc = getWDC()
    wcc = getWCC()
    all_data = {
        "drivers_championship": wdc,
        "constructors_championship": wcc,
    }
    save_to_supabase(all_data)

@app.route('/api/drivers', methods=['GET'])
def drivers():
    try:
        data = getWDC()
        return Response(json.dumps(data), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type="application/json", status=500)

@app.route('/api/teams', methods=['GET'])
def teams():
    try:
        data = getWCC()
        return Response(json.dumps(data), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type="application/json", status=500)

@app.route('/save', methods=['POST'])
def save():
    try:
        save_data()
        return Response(json.dumps({"status": "success"}), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type="application/json", status=500)

@app.route('/debug', methods=['GET'])
def debug():
    chromium_path = shutil.which('chromium-browser') or shutil.which('chromium')
    chromedriver_path = shutil.which('chromedriver')
    return {
        "chromedriver_path": chromedriver_path or "Not found",
        "chromium_path": chromium_path or "Not found"
    }

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
