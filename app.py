import json
import pandas as pd

from multiprocessing import Process

from run import run_loop
from blockchain.utils.analyzer import CryptoAnalyzer

from flask import Flask, Response, request

app = Flask(__name__)

processes = []

# Crear y comenzar un nuevo proceso que ejecute el bucle principal
p = Process(target=run_loop)
p.start()

processes.append(p)


@app.route('/')
def index():
    return "MMDex API"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80)