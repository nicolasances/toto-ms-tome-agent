
from dataclasses import dataclass
from datetime import datetime
from typing import List
from bson import ObjectId
from pymongo.collection import Collection

@dataclass
class AnswerRating: 
    
    rating: float 
    max_rating: int = 5
    explanations: str 
    detailedExplanations: str
    
    def __init__(self, rating: float, explanations: str, detailedExplanations: str):
        self.rating = rating 
        self.explanations = explanations 
        self.detailedExplanations = detailedExplanations
        
    

@dataclass
class TopicQuestion: 
    
    id: str
    topic_review_id: str 
    
    question: str 
    question_num: int
    num_questions_in_tr: int
    
    answer: str = None
    answered_on: str = None
    answered_at: str = None 
    
    rating: float = None
    max_rating: int  = 5
    explanations: str  = None
    detailed_explanation: str = None 

    @staticmethod
    def from_bson(data): 
        
        if data is None: 
            return TopicQuestion();
        
        q = TopicQuestion()    
        q.id = str(data['_id'])
        q.topic_review_id = data['topicReviewId']
        
        q.question = data['question']
        q.question_num = data['questionNum']
        q.num_questions_in_tr = data['numQuestions']
        
        if data.get('answeredAt') is not None: 
            q.answer = data['answer']
            q.answered_on = data['answeredOn']
            q.answered_at = data['answeredAt']
            q.rating = data['rating']
            q.max_rating = data['maxRating']
            q.explanations = data['explanations']
            q.detailed_explanation = data['detailedExplanation']
        
        return q
    
    def rate_and_update(self, answer: str, rating: AnswerRating, collection: Collection): 
        """Updates the Question with the Answer and its Rating

        Args:
            answer (str): the answer
            rating (AnswerRating): the generated rating
            collection (Collection): the collection to update
        """
        
        # 1. Update the object
        self.answer = answer
        self.answered_on = datetime.now().strftime('%Y%m%d')
        self.answered_at = datetime.now().strftime('%H:%M')
        self.rating = rating.rating
        self.max_rating = rating.max_rating
        self.explanations = rating.explanations
        self.detailed_explanation = rating.detailedExplanations
        
        # 2. Update the collection
        collection.update_one(
            {"_id": ObjectId(self.id)}, 
            {"$set": {
                "answer": self.answer, 
                "answeredOn": self.answered_on, 
                "answeredAt": self.answered_at,
                "rating": self.rating, 
                "maxRating": self.max_rating, 
                "explanations": self.explanations, 
                "detailedExplanation": self.detailed_explanation
            }}
        )
    

@dataclass
class TopicReview: 
    
    id: str 
    topic_code: str
    
    created_on: str 
    completed_on: str 
    
    questions: List[TopicQuestion]
    