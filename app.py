from flask import Flask, Response
from F1Scaper import getWDC, getWCC
import json
import shutil

app = Flask(__name__)

def save_data():
    # This function saves the scraped data to data.json file
    wdc = getWDC()
    wcc = getWCC()
    all_data = {
        "drivers_championship": wdc,
        "constructors_championship": wcc,
    }
    with open('data.json', 'w') as f:
        json.dump(all_data, f)

@app.route('/api/drivers', methods=['GET'])
def drivers():
    try:
        data = getWDC()
        json_data = json.dumps(data)
        return Response(json_data, content_type="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type='application/json', status=500)

@app.route('/api/teams', methods=['GET'])
def teams():
    try:
        data = getWCC()
        json_data = json.dumps(data)
        return Response(json_data, content_type="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type='application/json', status=500)

@app.route('/debug', methods=['GET'])
def debug():
    chromium_path = shutil.which('chromium-browser') or shutil.which('chromium')
    chromedriver_path = shutil.which('chromedriver')
    return {
        "chromedriver_path": chromedriver_path or "",
        "chromium_path": chromium_path or ""
    }

if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port=5000)
