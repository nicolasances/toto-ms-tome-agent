
from dataclasses import dataclass
from datetime import datetime
from typing import List
import json

@dataclass
class Topic:
    topic_code: str
    last_reviewed_on: str
    last_rating: float
    mem_level: float = None
    
    def __init__(self, code: str, last_reviewed_on: str = None, last_rating: float = None): 
        self.topic_code = code
        self.last_reviewed_on = last_reviewed_on
        self.last_rating = last_rating
        
    def to_json(self): 
        return {
            'topicCode': self.topic_code,
            'lastReviewedOn': self.last_reviewed_on,
            'lastRating': self.last_rating,
            'memLevel': self.mem_level
        }

def compute_mem_levels(topics: List[Topic]) -> List[Topic]: 
    """Computes the memorization level for each topic

    Args:
        topics (Topic[]): the list of topics (reviewed and not reviewed)
    """
    # 1. Define the "forgetting rate"
    # Considering that in 180 days, we get a score of zero, that means a rate of 0.0278 points lost per day 
    # This should be taken from a trained model over time
    forgetting_rate = 0.0278
    
    # 2. Apply the fogetting rate
    for topic in topics: 
        
        if topic.last_reviewed_on:
            last_reviewed_date = datetime.strptime(topic.last_reviewed_on, '%Y%m%d')
            days_since_review = (datetime.now() - last_reviewed_date).days
            topic.mem_level = max(0, topic.last_rating - forgetting_rate * days_since_review)
        else:
            topic.mem_level = 0
        
    return topics