from flask import Flask, request
from flask_cors import CORS

from dlg.getTopics import get_topics
from dlg.tr.answer import rate_answer
from dlg.tr.get import get_running_topic_review, get_topic_review
from dlg.tr.new import new_topic_review
from dlg.tr.question import get_next_question, get_question, get_questions
from dlg.tr.refresher import provide_refresher

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

@app.route('/topicreviews/<string:id>/questions/next', methods=['GET'])
def get_topic_review_next_question_route(id): 
    return get_next_question(request)

@app.route('/topicreviews/<string:id>/questions', methods=['GET'])
def get_topic_review_questions_route(id): 
    return get_questions(request)

@app.route('/topicreviews/questions/<string:id>', methods=['GET'])
def get_topic_review_question_route(id): 
    return get_question(request)

@app.route('/topicreviews/questions/<string:id>/refresher', methods=['GET'])
def get_refresher_for_question(id): 
    return provide_refresher(request)

@app.route('/answers', methods=['POST'])
def post_answer(): 
    return rate_answer(request)

@app.route('/topics', methods=['GET'])
def get_topics_list():
    return get_topics(request)


if __name__ == '__main__':
    app.run()