from typing import List
import boto3
from botocore.exceptions import ClientError
import json
from totoapicontroller.model.ExecutionContext import ExecutionContext

from kb.kb import KnowledgeBase

client = boto3.client("bedrock-runtime", region_name="eu-west-1")

class TopicRefresherAgent: 
    """This Agent helps the user by providing a refresher on a topic. 
    
    Given a question and an answer from the user, it will relook at the topic section and 
    give a refresher on it, so that the user understands the concepts better and is able to answer 
    the question the next time. 
    
    """

    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid

    def generate_refresher(self, question: str, answer: str, topic_code: str, section_code: str) -> str: 

        # 1. Load the context
        kb = KnowledgeBase(self.exec_context).get_knowledge(topic_code, section_code)
        
        # 2. Define the First Prompt
        system_prompt = f"""
        You are a specialist on the following topic (here identified by its code): {topic_code}. You base your information on the provided Knowledge Base.  
        You are helping a user of our app to refresh (review) the topic you are an expert on. 
        The user has been given a question to test his or her level of understanding and has given an answer. 
        Based on the question and the answer, and based on the content of the Knowledge Base, you are asked to provide a refresher to the user to help him (her) better remember the topic next time. 
        This is the KNOWLEDGE BASE:
        ----------------
        {kb}
        ----------------
        This is the QUESTION that was given to the user: 
        ----------------
        {question}
        ----------------
        This is the user's ANSWER: 
        ----------------
        {answer}
        ----------------
        Provide a refresher of the topic to the user, based on his (or her) answer to the question, that will help him (her) better remember the topic. 
        """

        conversation = [
            {
                "role": "user", 
                "content": [{"text": system_prompt}]
            },
        ]
        
        try:
            # Send the message to the model, using a basic inference configuration.
            response = client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 2000, "temperature": 0.3, "topP": 0.9},
            )
        
            # Extract and print the response text.
            return response["output"]["message"]["content"][0]["text"]
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            raise e
    