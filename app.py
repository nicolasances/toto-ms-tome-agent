from flask import Flask, request
from flask_cors import CORS

from dlg.getNextQuestion import get_next_question
from dlg.getRunningQuiz import get_running_quiz
from dlg.rateQuestion import rate_answer
from dlg.startQuiz import start_quiz

app = Flask(__name__)
# CORS(app, origins=["*"])
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization", "toto-service", "x-correlation-id", "auth-provider"]}})

@app.route('/', methods=['GET'])
def smoke():
    return {"api": "toto-ms-tome-agent", "running": True}

@app.route('/quizzes', methods=['POST'])
def post_quiz(): 
    return start_quiz(request)

@app.route('/quizzes/running', methods=['GET'])
def get_quiz_running(): 
    return get_running_quiz(request)

@app.route('/quizzes/<string:quizId>/questions/next', methods=['GET'])
def get_quiz_next_question(quizId): 
    return get_next_question(request)

@app.route('/answers', methods=['POST'])
def post_answer(): 
    return rate_answer(request)



if __name__ == '__main__':
    app.run()