import traceback
from bson import ObjectId
from pymongo import MongoClient, ASCENDING
from flask import Request
from agent.questions import QuestionsGenerator
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.Question import Question
from model.Quiz import Quiz
from model.TotoError import TotoError
from util.topicreview import find_next_topic

@toto_delegate(config_class=Config)
def new_topic_review(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Creates a new Topic Review. 
    """
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_collection = db['topicReviews']
        
        # 1. Find the next topic to review
        topic = find_next_topic(db['topics'])
        
        # 1. Generate questions on that topic
        generator_response = QuestionsGenerator(exec_context).generate_topic_review_questions(topic)
        
        print(generator_response)
        
        return generator_response

        
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
    
