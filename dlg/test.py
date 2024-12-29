from pymongo import MongoClient
from flask import Request
from agent.QuestionsGenerator import QuestionsGenerator
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

@toto_delegate(config_class=Config)
def test(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        
        collection = db['quizQuestions']
        
        result = collection.insert_one({"quizId": '990d8a9s8d09a'})
        
        print(result)
        
    except Exception as e: 
        print(f'ERROR: {e}')
        return {}
    
    finally: 
        if client: 
            client.close()
    
    # resp = QuestionsGenerator(exec_context).generate_questions(num_questions=5)
    resp = 'asd'
    
    return {"ok": True, "questions": resp}