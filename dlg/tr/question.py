from pymongo import MongoClient, ASCENDING
from flask import Request
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

from model.TotoError import TotoError
from model.topicreview import TopicReviewQuestion

@toto_delegate(config_class=Config)
def get_next_question(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Retrieves the next unanswered question for the specified topic review. 

    Args:
        request (Request): must contain a path element called id

    Returns:
        _type_: _description_
    """
    # 1. Extract the params
    tr_id = request.view_args.get('id')
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_questions_coll = db['topicReviewQuestions']
        
        # 2. Retrieve the first unanswered question
        questions_bson = tr_questions_coll.find({
            "topicReviewId": tr_id, 
            "$or": [
                { "answer": { "$exists": False } }, 
                { "answer": None }
            ]
        }).sort('questionNum', ASCENDING).to_list()
        
        # Error: no questions
        if len(questions_bson) == 0: 
            return TotoError(500, 'The Topic Review does not have any question', 'no-questions').to_json()
        
        first_unanswered_question = TopicReviewQuestion.from_bson(questions_bson[0])
        
        # 3. Return the question
        return first_unanswered_question.to_json()
    
    except Exception as e: 
        print(f'ERROR: {e}')
        return {
            "code": 500, 
            "msg": "Server Error", 
            "error": str(e)
        }
    
    finally: 
        if client: 
            client.close()
    


@toto_delegate(config_class=Config)
def get_questions(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    """Retrieves all the questions of a topic review

    Args:
        request (Request): must contain a path element called id
    """
    # 1. Extract the params
    tr_id = request.view_args.get('id')
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        tr_questions_coll = db['topicReviewQuestions']
        
        # 1. Retrieve the first unanswered question
        questions_bson = tr_questions_coll.find({ "topicReviewId": tr_id }).sort({'questionNum': ASCENDING}).to_list()
        
        # Error: no questions
        if len(questions_bson) == 0: 
            return TotoError(500, 'The Topic Review does not have any question', 'no-questions').to_json()
        
        # 3. Return the questions
        questions = []
        for q in questions_bson: 
            questions.append(TopicReviewQuestion.from_bson(q).__dict__)
        
        return {"questions": questions}
    
    except Exception as e: 
        print(f'ERROR: {e}')
        return {
            "code": 500, 
            "msg": "Server Error", 
            "error": str(e)
        }
    
    finally: 
        if client: 
            client.close()
    
