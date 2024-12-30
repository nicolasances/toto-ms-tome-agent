from pymongo import MongoClient
from flask import Request
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.Quiz import Quiz

@toto_delegate(config_class=Config)
def get_running_quiz(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        quizes = db['quizes']
        quiz_questions = db['quizQuestions']
        
        # 1. Retrieve the running quiz
        quiz_bson = quizes.find_one({
            "finishedOn": {"$exists": False}
        })
        
        # 2. Retrieve all questions from the quiz
        questions_bson = quiz_questions.find({"quizId": str(quiz_bson["_id"])})
        
        quiz = Quiz.from_bson(quiz_bson)
        
        return quiz.to_json()
    
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
    
