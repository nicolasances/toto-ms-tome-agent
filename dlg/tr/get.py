import traceback
from bson import ObjectId
from pymongo import ASCENDING, MongoClient
from flask import Request
from agent.questions import QuestionsGenerator
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.topicreview import TopicReview, TopicReviewQuestion

@toto_delegate(config_class=Config)
def get_running_topic_review(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_collection = db['topicReviews']
        tr_questions_coll = db['topicReviewQuestions']
        
        # 1. Retrieve the running topic review, if any. It's the one that have a null completedOn or a missing completedOn
        tr_bson = tr_collection.find_one({ "$or": [ { "completedOn": { "$exists": False } }, { "completedOn": None } ] })
        
        if tr_bson is None: 
            return {}
        
        # 2. Revtrieve the questions of that topic review sorted by question order
        tr_questions = tr_questions_coll.find({ "topicReviewId": str(tr_bson["_id"]) }).sort({"questionNum": ASCENDING})
    
        # 2. Return the TopicReview and its questions
        return {
            "topicReview": TopicReview.from_bson(tr_bson).__dict__, 
            "questions": [TopicReviewQuestion.from_bson(q).__dict__ for q in tr_questions]
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
    


@toto_delegate(config_class=Config)
def get_topic_review(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Retrieves a specific Topic Review, given its id
    """
    # 1. Extract the params
    tr_id = request.view_args.get('id')
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_collection = db['topicReviews']
        tr_questions_coll = db['topicReviewQuestions']
        
        # 1. Retrieve the running topic review, if any. It's the one that have a null completedOn or a missing completedOn
        tr_bson = tr_collection.find_one({ "_id": ObjectId(tr_id) })
        
        if tr_bson is None: 
            return {}
        
        # 2. Revtrieve the questions of that topic review sorted by question order
        tr_questions = tr_questions_coll.find({ "topicReviewId": str(tr_bson["_id"]) }).sort({"questionNum": ASCENDING})
    
        # 2. Return the TopicReview and its questions
        return {
            "topicReview": TopicReview.from_bson(tr_bson).__dict__, 
            "questions": [TopicReviewQuestion.from_bson(q).__dict__ for q in tr_questions]
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
    
