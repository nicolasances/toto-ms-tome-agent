from flask import Flask, request
from flask_cors import CORS

from dlg.getNextQuestion import get_next_question
from dlg.getQuiz import get_quiz
from dlg.getQuizQuestions import get_quiz_questions
from dlg.getTopics import get_topics
from dlg.rateQuestion import rate_answer
from dlg.tr.get import get_running_topic_review, get_topic_review
from dlg.tr.new import new_topic_review

app = Flask(__name__)
# CORS(app, origins=["*"])
CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"], "allow_headers": ["Content-Type", "Authorization", "toto-service", "x-correlation-id", "auth-provider"]}})

@app.route('/', methods=['GET'])
def smoke():
    return {"api": "toto-ms-tome-agent", "running": True}

@app.route('/topicreviews', methods=['POST'])
def post_topic_review_route(): 
    return new_topic_review(request)

@app.route('/topicreviews/running', methods=['GET'])
def get_running_topic_review_route(): 
    return get_running_topic_review(request)

@app.route('/topicreviews/<string:id>', methods=['GET'])
def get_topic_review_route(id):
    return get_topic_review(request)




@app.route('/quizzes/<string:quizId>', methods=['GET'])
def get_quiz_detail(quizId): 
    return get_quiz(request)


@app.route('/quizzes/<string:quizId>/questions', methods=['GET'])
def get_questions_of_quiz(quizId): 
    return get_quiz_questions(request)

@app.route('/quizzes/<string:quizId>/questions/next', methods=['GET'])
def get_quiz_next_question(quizId): 
    return get_next_question(request)

@app.route('/answers', methods=['POST'])
def post_answer(): 
    return rate_answer(request)

@app.route('/topics', methods=['GET'])
def get_topics_list():
    return get_topics(request)


if __name__ == '__main__':
    app.run()