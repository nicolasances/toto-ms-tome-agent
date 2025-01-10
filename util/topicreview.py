from random import random
import re
from pymongo.collection import Collection
from model.topic import Topic

def find_next_topic(topics_collection: Collection) -> Topic:
    """Finds the next Topic to review. 
    
    Args:
        topics_collection (Collection): the collection where the topics are stored
        
    Returns:
        Topic: the next topic to review
    
    """
    # Find the first topic found in the topics collection
    topics = topics_collection.find().to_list()
    
    topics_len = len(topics)
    
    random_index = int(random() * topics_len)
    topic_bson = topics[random_index]
    
    # Return a Topic object
    return Topic.from_bson(topic_bson)
    
    