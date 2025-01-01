from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from flask import Request
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.Question import Question
from model.Quiz import Quiz
from model.TotoError import TotoError

@toto_delegate(config_class=Config)
def get_quiz_questions(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Retrieves all the questions of a quiz

    Args:
        request (Request): must contain a path element called quizId
    """
    # 1. Extract the params
    quiz_id = request.view_args.get('quizId')
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        quiz_questions = db['quizQuestions']
        
        # 1. Retrieve the first unanswered question
        questions_bson = quiz_questions.find({ "quizId": quiz_id }).sort('questionNum', ASCENDING).to_list()
        
        # Error: no questions
        if len(questions_bson) == 0: 
            return TotoError(500, 'The Quiz does not have any question', 'no-questions').to_json()
        
        # 3. Return the questions
        questions = []
        for q in questions_bson: 
            questions.append(Question.from_bson(q).to_json())
        
        return {"questions": questions}
    
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
    
