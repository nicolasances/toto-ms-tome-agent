from flask import Flask, request
from flask_cors import CORS

from dlg.startQuiz import start_quiz
from dlg.test import test

app = Flask(__name__)
# CORS(app, origins=["*"])
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization", "toto-service", "x-correlation-id"]}})

@app.route('/', methods=['GET'])
def smoke():
    return {"api": "toto-ms-tome-agent", "running": True}

@app.route('/quizzes', methods=['POST'])
def post_quiz(): 
    return start_quiz(request)

@app.route('/test', methods=['GET'])
def testing(): 
    return test(request)

if __name__ == '__main__':
    app.run()