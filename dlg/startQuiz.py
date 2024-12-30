from pymongo import MongoClient
from flask import Request
from agent.QuestionsGenerator import QuestionsGenerator
from config.Config import Config
from datetime import datetime

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

@toto_delegate(config_class=Config)
def start_quiz(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    config: Config = exec_context.config
    
    client = None
    
    try: 
        client = MongoClient(config.get_mongo_connection_string())
        
        db = client['tome']
        quizes = db['quizes']
        quiz_questions = db['quizQuestions']
        
        # 1. Generate questions on that topic
        num_questions = 5
        
        generator_response = QuestionsGenerator(exec_context).generate_questions(num_questions=num_questions)
        
        # 2. Save the quiz with the questions generation time
        quiz = {
            "topicId": "890829081098as90d8a90s8d90a", 
            "topicName": "Cortes", 
            "sectionId": '98as890da8s09d8a90s8d', 
            "sectionName": "Cortes Invasion of Mexico", 
            "questionsGenerationTime": generator_response.response_time, 
            "questionsGenerationTimeUnit": generator_response.response_time_unit, 
            "startedOn": datetime.now().strftime('%Y%m%d'), 
            "startedAt": datetime.now().strftime('%H:%M')
        }
        
        quiz_id = quizes.insert_one(quiz).inserted_id
        
        # 3. Save the questions
        for i, question in enumerate(generator_response.questions): 
            
            quiz_questions.insert_one({
                "quizId": str(quiz_id), 
                "question": question, 
                "questionNum": i+1, 
                "numQuestions": num_questions
            })
            
        return {
            "quizId": str(quiz_id), 
            "questions": generator_response.questions, 
            "generatedIn": generator_response.response_time, 
            "generatedInUnit": generator_response.response_time_unit
        }
        
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
    