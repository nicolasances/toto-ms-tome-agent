
from dataclasses import dataclass
from datetime import datetime
from typing import List
from bson import ObjectId
from pymongo.collection import Collection

from agent import rating
    

@dataclass
class TopicReview: 
    
    topic_code: str
    created_on: str 
    id: str = None
    completed_on: str = None
    rating: float = None
    max_rating: int = 5
    
    def __init__(self, topic_code: str):
        self.topic_code = topic_code
        self.created_on = datetime.now().strftime('%Y%m%d')
        self.completed_on = None
    
    def to_bson(self): 
        
        return {
            "topicCode": self.topic_code, 
            "createdOn": self.created_on, 
            "completedOn": self.completed_on, 
            "rating": self.rating,
            "maxRating": self.max_rating
        }
        
    def to_json(self):
        return {
            "id": self.id, 
            "topicCode": self.topic_code, 
            "createdOn": self.created_on, 
            "completedOn": self.completed_on, 
            "rating": self.rating,
            "maxRating": self.max_rating
        }
                
    @staticmethod
    def from_bson(data):
        
        if data is None: 
            return TopicReview()
        
        tr = TopicReview(data['topicCode'])
        tr.id = str(data['_id'])
        tr.created_on = data['createdOn']
        tr.completed_on = data.get('completedOn')
        tr.rating = data.get('rating')
        tr.max_rating = data.get('maxRating')
        
        return tr
    
    def close(self, rating: float, collection: Collection): 
        """Marks the Topic Review as finished and updates the collection

        Args:
            collection (Collection): the collection to update
        """
        # 1. Mark as finished
        self.completed_on = datetime.now().strftime('%Y%m%d')
        self.rating = rating
        
        # 2. Update the collection
        collection.update_one({"_id": ObjectId(self.id)}, {"$set": {
            "completedOn": self.completed_on, 
            "rating": rating,
        }})


@dataclass
class AnswerRating: 
    
    rating: float = 0
    max_rating: int = 5
    explanations: str = None
    detailedExplanations: str = None
    
    def __init__(self, rating: float, explanations: str, detailedExplanations: str):
        self.rating = rating 
        self.explanations = explanations 
        self.detailedExplanations = detailedExplanations
        
    def to_json(self):
        return {
            "rating": self.rating, 
            "maxRating": self.max_rating, 
            "explanations": self.explanations, 
            "detailedExplanations": self.detailedExplanations
        }
        
    

@dataclass
class TopicReviewQuestion: 
    
    topic_review_id: str # The id of the Topic Review the question belongs to
    
    section_code: str   # The code of the section the question belongs to
    section_title: str  # The title of the section the question belongs to
    
    question: str 
    question_num: int   
    num_questions_in_tr: int
    
    id: str = None
    
    answer: str = None
    answered_on: str = None
    answered_at: str = None 
    
    rating: float = None
    max_rating: int  = 5
    explanations: str  = None
    detailed_explanation: str = None 
    
    def __init__(self, topic_review_id: str, section_code: str, section_title: str, question: str, question_num: int, num_questions_in_tr: int):
        self.topic_review_id = topic_review_id
        self.section_code = section_code
        self.section_title = section_title
        self.question = question
        self.question_num = question_num
        self.num_questions_in_tr = num_questions_in_tr
    
    @staticmethod
    def from_bson(data): 
        
        if data is None: 
            return TopicReviewQuestion()
        
        trq = TopicReviewQuestion(
            data['topicReviewId'], 
            data['sectionCode'], 
            data['sectionTitle'], 
            data['question'], 
            data['questionNum'], 
            data['numQuestions']
        )
        
        trq.id = str(data['_id'])
        trq.answer = data.get('answer')
        trq.answered_on = data.get('answeredOn')
        trq.answered_at = data.get('answeredAt')
        trq.rating = data.get('rating')
        trq.max_rating = data.get('maxRating')
        trq.explanations = data.get('explanations')
        trq.detailed_explanation = data.get('detailedExplanation')
        
        return trq
        
    
    def to_bson(self):
        """Translate this object to a BSON dictionary
        """
        return {
            "topicReviewId": self.topic_review_id, 
            "sectionCode": self.section_code, 
            "sectionTitle": self.section_title, 
            "question": self.question, 
            "questionNum": self.question_num, 
            "numQuestions": self.num_questions_in_tr,
            "answer": self.answer, 
            "answeredOn": self.answered_on, 
            "answeredAt": self.answered_at, 
            "rating": self.rating, 
            "maxRating": self.max_rating, 
            "explanations": self.explanations, 
            "detailedExplanation": self.detailed_explanation
        }
    
    def to_json(self):
        """Translate this object to a JSON dictionary
        """
        return {
            "id": self.id, 
            "topicReviewId": self.topic_review_id, 
            "sectionCode": self.section_code, 
            "sectionTitle": self.section_title, 
            "question": self.question, 
            "questionNum": self.question_num, 
            "numQuestions": self.num_questions_in_tr,
            "answer": self.answer, 
            "answeredOn": self.answered_on, 
            "answeredAt": self.answered_at, 
            "rating": self.rating, 
            "maxRating": self.max_rating, 
            "explanations": self.explanations, 
            "detailedExplanation": self.detailed_explanation
        }
    
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