
from dataclasses import dataclass
from typing import List


@dataclass
class TimelineDate: 
    
    date: str
    events: List[str]
    
    def __init__(self, date: str, events: List[str]): 
        self.date = date
        self.events = events
        
    def to_json(self): 
        return {
            'date': self.date, 
            'events': self.events
        }
    
    @staticmethod
    def from_bson(data): 
        return TimelineDate(data['date'], data['events'])
    
@dataclass
class Timeline: 
    
    dates: List[TimelineDate] 
    
    def __init__(self, dates: List[TimelineDate] = None): 
        self.dates = dates
    
    def to_json(self): 
        if self.dates is None: 
            return []
        
        return [ date.to_json() for date in self.dates ]
    
    @staticmethod
    def from_bson(data): 
        if data is None or len(data) == 0: 
            return Timeline()
        
        return Timeline([TimelineDate.from_bson(item) for item in data])
    
    