
from datetime import datetime
from typing import List
from bson import ObjectId
from pymongo.collection import Collection
from model.Question import Question


class Quiz: 
    
    id: str
    topic_code: str
    topic_name: str
    section_code: str 
    section_name: str 
    started_on: str 
    num_questions: int 
    num_questions_answered: int
    score: float
    max_score: int
    finished_on: str = None 
    finished_at: str = None 

    @staticmethod
    def from_bson(data, questions: List[Question] = None): 
        
        if data is None: 
            return Quiz();
        
        q = Quiz()    
        q.id = str(data['_id'])
        q.topic_code = data['topicCode']
        q.topic_name = data['topicName']
        q.section_code = data['sectionCode']
        q.section_name = data['sectionName']
        q.started_on = data['startedOn']
        q.num_questions = data.get('numQuestions', 5)
        q.finished_on = data.get('finishedOn')
        q.finished_at = data.get('finishedAt')
        
        # Computed fields
        q.num_questions_answered = 0 
        q.score = 0
        q.max_score = 5
        
        if questions is not None: 
            summed_score = 0
            
            for question in questions: 
                if question.answered_on is not None: 
                    q.num_questions_answered = q.num_questions_answered + 1
                    summed_score = summed_score + question.rating
            
            if q.num_questions_answered != 0: 
                q.score = summed_score / q.num_questions_answered
        
        return q
    
    def close_quiz(self, collection: Collection): 
        """Marks the Quiz as finished and updates the collection

        Args:
            collection (Collection): the collection to update
        """
        # 1. Mark as finished
        self.finished_on = datetime.now().strftime('%Y%m%d')
        self.finished_at = datetime.now().strftime('%H:%M') 
        
        # 2. Update the collection
        collection.update_one({"_id": ObjectId(self.id)}, {"$set": {
            "finishedOn": self.finished_on,
            "finishedAt": self.finished_at
        }})
        
    def to_json(self): 
        return {
            "id": self.id, 
            "topic": self.topic_name, 
            "section": self.section_name, 
            "startedOn": self.started_on, 
            "numQuestions": self.num_questions, 
            "numQuestionsAnswered": self.num_questions_answered, 
            "score": self.score, 
            "maxScore": self.max_score, 
            "finishedOn": self.finished_on, 
        }