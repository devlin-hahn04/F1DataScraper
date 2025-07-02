from flask import Flask, Response
from F1Scaper import getWDC, getWCC
import json

app= Flask(__name__)

@app.route('/api/drivers', methods=['GET'])

def drivers():
    try:
        data= getWDC()
        json_data= json.dumps(data)

        return Response(json_data, content_type= "application/json")
    
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type='application/json', status=500)
    

@app.route('/api/teams', methods=['GET'])

def teams():
    try:
        data= getWCC()
        json_data= json.dumps(data)

        return Response(json_data, content_type= "application/json")
    
    except Exception as e:
        return Response(json.dumps({"error": str(e)}), content_type='application/json', status=500)
    

@app.route('/debug')

def debug():
    import subprocess
    chromedriver = subprocess.run(['which', 'chromedriver'], capture_output=True, text=True).stdout.strip()
    chromium = subprocess.run(['which', 'chromium-browser'], capture_output=True, text=True).stdout.strip()
    return {
        'chromedriver_path': chromedriver,
        'chromium_path': chromium
    }

    

if __name__ == '__main__':
    app.run(debug= True, host= "0.0.0.0", port= 5000)
