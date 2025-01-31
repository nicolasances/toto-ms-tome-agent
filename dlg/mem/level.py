from pymongo import MongoClient
from flask import Request
from config.Config import Config
import traceback

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from util.memlevel import Topic, compute_mem_levels

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
        topics_coll = db['topics']
        
        # 1. Retrieve the topic reviews
        pipeline = [
            { "$sort": { "completedOn": -1 } },
            { "$group": {
            "_id": "$topicCode",
            "latestCompletedOn": { "$first": "$completedOn" },
            "rating": { "$first": "$rating" },
            "maxRating": { "$first": "$maxRating" }
            }}
        ]
        
        reviewed_topics = tr_coll.aggregate(pipeline).to_list()
        
        # 2. Read the topics
        topics = topics_coll.find().to_list()
        
        # 3. Find the topics that have not been reviewed
        reviewed_topic_codes = {topic['_id'] for topic in reviewed_topics}
        unreviewed_topics = [topic['code'] for topic in topics if topic['code'] not in reviewed_topic_codes]
        
        # 4. Crete the input for the mem level calculation
        topics_to_score = []
        for reviewed_topic in reviewed_topics: 
            
            if reviewed_topic['rating'] is not None: 
                rating = reviewed_topic['rating'] / reviewed_topic['maxRating']
            else: 
                rating = None
            
            topic = Topic(code = reviewed_topic["_id"], last_reviewed_on = reviewed_topic['latestCompletedOn'], last_rating = rating)
            
            topics_to_score.append(topic)
            
        for utopic_code in unreviewed_topics: 
            topics_to_score.append(Topic(code = utopic_code))
            
            
        # 5. Calculate the Memorization Levels
        topics_with_memlevel = compute_mem_levels(topics_to_score)
        
        return {
            "topics": [topic.to_json() for topic in topics_with_memlevel]
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
    
