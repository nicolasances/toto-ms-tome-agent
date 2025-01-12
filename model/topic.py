from dataclasses import dataclass
from typing import List

@dataclass
class TopicSection: 
    
    title: str 
    code: str 
    length: int
    order: int = None
    
    def __init__(self, title: str, code: str, length: int, order: int = None): 
        self.title = title
        self.code = code
        self.length = length
        self.order = order
    
    
@dataclass
class Topic: 
    
    title: str 
    code: str 
    sections: List[TopicSection]
    blog_url: str = None
    
    @staticmethod
    def from_bson(bson): 
        return Topic(
            title=bson["title"], 
            code=bson["code"], 
            # The 1000 is there purely for backward compatibility. Could be removed
            sections=[TopicSection(title=section["title"], code=section["code"], length=section.get("length", 1000), order=section.get("order")) for section in bson["sections"]], 
            blog_url=bson.get('blog_url')
        )
        