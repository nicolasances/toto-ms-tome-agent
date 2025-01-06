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
def rate_answer(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Rates the answer to a topic review question

    Args:
        request (Request): must contain the answer and the question id
    """
    data = request.get_json()
    
    # 1. Extract the params
    question_id = data.get('questionId', None)
    answer = data.get('answer', None)
    
    if question_id is None: return TotoValidationError('No Question Id was provided').to_json()
    if answer is None: return TotoValidationError('No Answer was provided').to_json()
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_coll = db['topicReviews']
        tr_questions_coll = db['topicReviewQuestions']
        
        # 1. Retrieve the question
        question_bson = tr_questions_coll.find_one({"_id": ObjectId(question_id)})
        
        question = TopicReviewQuestion.from_bson(question_bson)
        
        # 2. Retrieve the Topic Review
        topic_review_bson = tr_coll.find_one({"_id": ObjectId(question.topic_review_id)})
        
        topic_review = TopicReview.from_bson(topic_review_bson)
        
        # 2. Rate the answer
        rating: AnswerRating = RatingAgent(exec_context, topic_review.topic_code, question.section_code).rate_answer(question.question, answer)
        
        # 3. Save the rating
        exec_context.logger.log(exec_context.cid, f'Saving the Question with the Answer and Rating ({rating.rating}/{rating.max_rating})')
        
        question.rate_and_update(answer, rating, tr_questions_coll)
        
        # 4. Check if the quiz is over
        unanswered_questions = tr_questions_coll.find({ 
            "topicReviewId": question.topic_review_id, 
            "$or": [
                { "answer": { "$exists": False } }, 
                { "answer": None }
            ]
        }).to_list()
        
        topic_review_finished = False
        
        # If there are no more unanswered questions, the Review is finished
        if len(unanswered_questions) == 0: 
            
            exec_context.logger.log(exec_context.cid, f'The Topic Review is Finished!')
            
            topic_review_finished = True
            
            # Retrieve all the questions of the Topic Review
            all_questions = tr_questions_coll.find({ "topicReviewId": question.topic_review_id })
            
            # Calculate the rating of the Topic Review as an average of the ratings of the questions
            question_ratings = [TopicReviewQuestion.from_bson(q).rating for q in all_questions]
            
            avg_rating = sum(question_ratings) / len(question_ratings)
            
            # 4.1. Update the Topic Review
            topic_review.close(avg_rating, tr_coll)
            
        return rating.to_json(topic_review_finished=topic_review_finished)
    
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
    
