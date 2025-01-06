from dataclasses import dataclass
from typing import List

@dataclass
class TopicSection: 
    
    title: str 
    code: str 
    order: int = None
    
    def __init__(self, title: str, code: str, order: int = None): 
        self.title = title
        self.code = code
        self.order = order
    
    
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
            sections=[TopicSection(title=section["title"], code=section["code"], order=section.get("order")) for section in bson["sections"]]
        )