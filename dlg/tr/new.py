import traceback
from pymongo import MongoClient
from flask import Request
from agent.questions import QuestionsGenerator
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.topicreview import TopicReview
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
        tr_questions_coll = db['topicReviewQuestions']
        
        # 1. Find the next topic to review
        topic = find_next_topic(db['topics'])
        
        # 2. Create a TopicReview and save it to the database
        tr = TopicReview(topic.code, topic.title)
        tr_id = tr_collection.insert_one(tr.to_bson()).inserted_id
        tr.id = str(tr_id)
        
        # 3. Generate questions on that topic
        topic_review_questions = QuestionsGenerator(exec_context).generate_topic_review_questions(topic, str(tr_id))

        # 4. Save the questions to the database 
        for trq in topic_review_questions: 
            tr_questions_coll.insert_one(trq.to_bson())
            
        # 5. Return the TopicReview and the questions
        return {
            "topicReview": tr.to_json(), 
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
    
