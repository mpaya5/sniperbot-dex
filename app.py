import json
import pandas as pd

from multiprocessing import Process

from run import run_loop

from flask import Flask, Response, request

app = Flask(__name__)

# processes = []
# # Crear y comenzar un nuevo proceso que ejecute el bucle principal
# p = Process(target=run_loop)
# p.start()

# processes.append(p)

# @app.route('/changePressureVol', methods=['POST'])
# def changePressureVol():
#     data = json.loads(s)

@app.route('/')
def index():
    return "MMDex API"

@app.route('/changePercentageSell', methods=["POST"])
def changeBuyPresure():
    data = json.loads(request.data)
    passhprase = data['passhprase']
    if passhprase == "EN9pV!A2VRqm8LQmBgWy&m":
        df = pd.DataFrame([{"pressure":data['value']}])
        df.to_csv('data/buy_pressure_sell.csv')

        return {"status": 200, "result": True}

    return {"status":400, "result": "Wrong passhprase"} 

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)