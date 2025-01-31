from bson import ObjectId
from pymongo import MongoClient
from flask import Request
from agent.rating import AnswerRating, RatingAgent
from config.Config import Config
import traceback

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.TotoError import TotoValidationError
from model.topicreview import TopicReview, TopicReviewQuestion

@toto_delegate(config_class=Config)
def get_mem_levels(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Gets the memorization levels for all the topics in the knowledge base

    Args:
        request (Request)
    """        
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_coll = db['topicReviews']
        
        # 1. Retrieve the topic reviews
        pipeline = [
            { "$group": {
                "_id": "$topicCode",
                "latestCompletedOn": {
                    "$max": {
                        "$cond": {
                        "if": { "$eq": ["$completedOn", None] },
                        "then": None,
                        "else": "$completedOn"
                        }
                    }
                } 
            }
        }]
        
        trs_in_db = tr_coll.aggregate(pipeline).to_list()
    
        topic_reviews = []
        for tr in trs_in_db: 
            print(tr)
            #topic_reviews.append(TopicReview.from_bson(tr))
        
        return {
            "topicReviews": topic_reviews
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
    
