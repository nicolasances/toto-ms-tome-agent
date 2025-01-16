from random import random
import re
from pymongo import DESCENDING
from pymongo.collection import Collection
from model.topic import Topic
from model.topicreview import TopicReview

def find_next_topic(topics_collection: Collection, topic_reviews_coll: Collection) -> Topic:
    """Finds the next Topic to review. 
    
    Args:
        topics_collection (Collection): the collection where the topics are stored
        topic_reviews_coll (Collection): the collection of topic reviews
        
    Returns:
        Topic: the next topic to review
    
    """
    
    topics = topics_collection.find().to_list()
    trs = topic_reviews_coll.find().sort({"completedOn": DESCENDING})
    
    topic_codes = [Topic.from_bson(topic).code for topic in topics]
    
    # For each Topic Review, sorted in descending order of completion, the following loop will remove the corresponding 
    # topic in the topics list
    # The last topic standing is the oldest topic that has been reviewed, and should be the next in line.
    for tr in trs: 
        
        # If there's only one topic left, return that one: it's the one reviewed the farthest
        if len(topics) == 1: 
            break
        
        topic_review = TopicReview.from_bson(tr)
        
        topics = [topic for topic in topics if Topic.from_bson(topic).code != topic_review.topic_code]
        
    return Topic.from_bson(topics[0])
    
    
    
