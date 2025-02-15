from bson import ObjectId
from pymongo import MongoClient
from flask import Request
from agent.rating import AnswerRating, RatingAgent
from agent.refresher import TopicRefresherAgent
from config.Config import Config
import traceback

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.TotoError import TotoValidationError
from model.topic import Topic
from model.topicreview import TopicReview, TopicReviewQuestion

@toto_delegate(config_class=Config)
def provide_refresher(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Provides a refresher on the given topic section, based on the given question and answer from the user. 

    Args:
        request (Request): must contain the answer and the question id
    """
    # 1. Extract the params
    question_id = request.view_args.get('id')
    
    if question_id is None: return TotoValidationError('No Question Id was provided').to_json()
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_coll = db['topicReviews']
        tr_questions_coll = db['topicReviewQuestions']
        topics_coll = db['topics']
        refreshers_coll = db['refreshers']
        
        # 1. Retrieve the question
        question_bson = tr_questions_coll.find_one({"_id": ObjectId(question_id)})
        
        question = TopicReviewQuestion.from_bson(question_bson)
        
        # 2. Retrieve the Topic Review
        topic_review_bson = tr_coll.find_one({"_id": ObjectId(question.topic_review_id)})
        
        topic_review = TopicReview.from_bson(topic_review_bson)
        
        # 3. Retrieve the Topic, for better context in the answer
        topic = topics_coll.find_one({"code": topic_review.topic_code})
        
        # 4. Find the pre-generated refresher
        refresher_bson = refreshers_coll.find_one({"topicCode": question.topic_code, 'sectionCode': question.section_code})
        
        if refresher_bson is not None: 
            refersher_text = refresher_bson['refersher']
        else: 
            # Use the Topic Refresher Agent to generate a refresher
            refersher_text = TopicRefresherAgent(exec_context).generate_refresher(question.question, question.answer, topic_review.topic_code, question.section_code)
            
        return {
            "topic": Topic.from_bson(topic).__dict__,
            "refresher": refersher_text
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
    
