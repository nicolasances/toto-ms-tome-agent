import traceback
from pymongo import MongoClient
from flask import Request
from agent.questions import QuestionsGenerator
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.topic import Topic
from model.topicreview import TopicReview
from util.topicreview import find_next_topic

@toto_delegate(config_class=Config)
def generate_test_questions(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Creates a new Topic Review. 
    """
    data = request.get_json()
    
    # 1. Extract the params
    topic_code = data.get('topicCode', None)
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        topics_coll = db['topics']
        
        topic_bson = topics_coll.find_one({"code": topic_code})
        topic = Topic.from_bson(topic_bson)
        
        # 3. Generate questions on that topic
        topic_review_questions = QuestionsGenerator(exec_context).generate_topic_review_questions(topic, 'test-topic-review')

        # 5. Return the questions
        return {
            "questions": [q.to_json() for q in topic_review_questions]
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
    

