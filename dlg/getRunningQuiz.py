from pymongo import MongoClient
from flask import Request
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

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
        quiz = quizes.find_one({
            "finishedOn": {"$exists": False}
        })
        
        # Make the id serializable
        quiz["_id"] = str(quiz["_id"])
        
        return quiz 
    
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
    