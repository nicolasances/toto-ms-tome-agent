
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

    @staticmethod
    def from_bson(data): 
        
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
        q.num_questions_answered = 0 
        q.score = 0
        q.max_score = 5
        
        return q
        
    def to_json(self): 
        return {
            "id": self.id, 
            "topic": self.topic_name, 
            "section": self.section_name, 
            "startedOn": self.started_on, 
            "numQuestions": self.num_questions, 
            "numQuestionsAnswered": self.num_questions_answered, 
            "score": self.score, 
            "maxScore": self.max_score
        }