from flask import Flask, Response
from F1Scaper import getWDC, getWCC, nextrace, getDriverPhotos, getTeamLogos
import json
import shutil

app = Flask(__name__)

@app.route('/api/drivers', methods=['GET'])
def drivers():
    try:
        data = getWDC()
        # print(data)
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
    

@app.route('/api/nextrace', methods=['GET'])
def next_race():
    try:
        gp_name = nextrace()
        return Response(json.dumps({"next_race": gp_name}), content_type="application/json")
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type="application/json", status=500)
    

@app.route('/api/driverphotos', methods=['GET'])
def driver_photos():
    try:
        photos= getDriverPhotos()
        return Response(json.dumps({"driver_photos": photos}), content_type="application/json")
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

    
