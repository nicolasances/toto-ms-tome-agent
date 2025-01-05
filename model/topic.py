from dataclasses import dataclass
from typing import List

@dataclass
class TopicSection: 
    
    title: str 
    code: str 
    
@dataclass
class Topic: 
    
    title: str 
    code: str 
    sections: List[TopicSection]
    
    @staticmethod
    def from_bson(bson): 
        return Topic(
            title=bson["title"], 
            code=bson["code"], 
            sections=[TopicSection(**section) for section in bson["sections"]]
        )