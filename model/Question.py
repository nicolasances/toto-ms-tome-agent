
from bson import ObjectId
from pymongo.collection import Collection
from datetime import datetime

from agent.rating import AnswerRating


class Question: 
    
    id: str
    question: str 
    quiz_id: str
    question_num: int
    num_questions_in_quiz: int
    answer: str = None
    answered_on: str = None
    answered_at: str = None 
    rating: float = None
    max_rating: int  = None
    explanations: str  = None
    detailed_explanation: str = None 

    @staticmethod
    def from_bson(data): 
        
        if data is None: 
            return Question();
        
        q = Question()    
        q.id = str(data['_id'])
        q.question = data['question']
        q.quiz_id = data['quizId']
        q.question_num = data['questionNum']
        q.num_questions_in_quiz = data['numQuestions']
        
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
    
    def to_json(self) -> dict: 
        """Returns the JSON version of this object as a dict. 
        This is to be used to generate a Transfer Object to send back through the API. 

        Returns:
            dict: the generated TO
        """
        
        return {
            "id": self.id, 
            "question": self.question, 
            "quizId": self.quiz_id, 
            "questionNum": self.question_num, 
            "numQuestionsInQuiz": self.num_questions_in_quiz,
            "answer": self.answer, 
            "answerOn": self.answered_on, 
            "rating": self.rating, 
            "maxRating": self.max_rating
        }