import traceback
from bson import ObjectId
from pymongo import MongoClient
from flask import Request
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.Question import Question
from model.Quiz import Quiz

@toto_delegate(config_class=Config)
def get_quiz(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    # 1. Extract the params
    quiz_id = request.view_args.get('quizId')
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        quizes = db['quizes']
        
        # 1. Retrieve the running quiz
        quiz_bson = quizes.find_one({"_id": ObjectId(quiz_id)})
        
        if quiz_bson is None: 
            return {}
        
        quiz = Quiz.from_bson(quiz_bson)
        
        return quiz.to_json()
    
    except Exception as e: 
        traceback.print_exc()
        return {
            "code": 500, 
            "msg": "Server Error", 
            "error": str(e)
        }
    
    finally: 
        if client: 
            client.close()
    
