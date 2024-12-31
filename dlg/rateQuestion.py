from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from flask import Request
from agent.rating import AnswerRating, RatingAgent
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.Question import Question
from model.Quiz import Quiz
from model.TotoError import TotoError, TotoValidationError

@toto_delegate(config_class=Config)
def rate_answer(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Rates the answer to a quiz question

    Args:
        request (Request): must contain the answer and the question id
    """
    data = request.get_json()
    
    # 1. Extract the params
    question_id = data.get('questionId', None)
    answer = data.get('answer', None)
    
    if question_id is None: return TotoValidationError('No Question Id was provided').to_json()
    if answer is None: return TotoValidationError('No Answer was provided').to_json()
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        quizes = db['quizes']
        quiz_questions = db['quizQuestions']
        
        # 1. Retrieve the question
        question_bson = quiz_questions.find_one({"_id": ObjectId(question_id)})
        
        question = Question.from_bson(question_bson)
        
        # 2. Retrieve the Quiz
        quiz_bson = quizes.find_one({"_id": ObjectId(question.quiz_id)})
        
        quiz = Quiz.from_bson(quiz_bson)
        
        # 2. Rate the answer
        rating: AnswerRating = RatingAgent(exec_context, quiz.topic_code, quiz.section_code).rate_answer(question.question, answer).to_json()
        
        return rating
    
    except Exception as e: 
        print(f'ERROR: {e}')
        return {
            "code": 500, 
            "msg": "Server Error", 
            "error": str(e)
        }
    
    finally: 
        if client: 
            client.close()
    
