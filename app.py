from flask import Flask, request
from flask_cors import CORS

from dlg.test import test

app = Flask(__name__)
CORS(app, origins=["*"])

@app.route('/', methods=['GET'])
def smoke():
    return {"api": "toto-ms-tome-agent", "running": True}

@app.route('/test', methods=['GET'])
def testing(): 
    return test(request)

if __name__ == '__main__':
    app.run()