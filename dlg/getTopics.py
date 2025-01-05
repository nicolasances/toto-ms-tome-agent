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
from model.topic import Topic

@toto_delegate(config_class=Config)
def get_topics(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        topics = db['topics']
    
        # 1. Retrieve the topics
        topics_bson = topics.find({})
    
        topics = [] 
        for t in topics_bson: 
            topics.append(Topic.from_bson(t))   
            
        return {
            "topics": [topic.__dict__ for topic in topics]
        }
    
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
    
