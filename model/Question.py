
class Question: 
    
    id: str
    question: str 
    quiz_id: str
    question_num: int
    num_questions_in_quiz: int

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
        
        return q
    
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
            "numQuestionsInQuiz": self.num_questions_in_quiz
        }