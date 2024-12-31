from typing import List
import boto3
from botocore.exceptions import ClientError
import json
from totoapicontroller.model.ExecutionContext import ExecutionContext

from kb.kb import KnowledgeBase

client = boto3.client("bedrock-runtime", region_name="eu-west-1")

class AnswerRating: 
    rating: float 
    max_rating: int = 5
    explanations: str 
    detailedExplanations: str
    
    def __init__(self, rating: float, explanations: str, detailedExplanations: str):
        self.rating = rating 
        self.explanations = explanations 
        self.detailedExplanations = detailedExplanations
        
    def to_json(self): 
        return {
            "rating": self.rating,
            "maxRating": self.max_rating, 
            "explanations": self.explanations, 
            "detailedExplanations": self.detailedExplanations
        }
    
    
class RatingReasoningAgent: 
    """This Agent rates and answer of a given question, given a provided knowledge base. 
    It is a REASONING agent, it is meant to use Chain of Thought to provide an accurate rating with a good reasoning behind. 
    To do that it CANNOT provide a JSON structured answer and only provides text with the reasoning and the rating. 
    
    For an actual final rating, use the RatingAgent, which orchestrates multiple agents to do this.
    """

    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid

    def rate_answer(self, question: str, answer: str, topic_code: str, section_code: str) -> str: 

        # 1. Load the context
        kb = KnowledgeBase(self.exec_context).get_knowledge(topic_code, section_code)
        
        # 2. Define the First Prompt
        system_prompt = f"""
        You are a Quiz engine and you have previously generated some questions based on a knowledge base. 
        You are going to be provided a question (that you generated) and the user's answer to that question. 
        You are asked to rate the answer on a scale from 1 to 5, 1 being the lowest score, 5 the highest. 
        This is the KNOWLEDGE BASE:
        ----------------
        {kb}
        ----------------
        This is the QUESTION: 
        ----------------
        {question}
        ----------------
        This is the user's ANSWER: 
        ----------------
        {answer}
        ----------------
        Rate the answer as a float with maximum one decimal number.
        You MUST only use the knowledge base to rate the answer. 
        If some information is provided in the answer and cannot be found in the knowledge base, ignore it and do not mention it in your explanations. 

        To rate the answer you MUST perform the following steps: 
        1. List the most important aspects as a short list
        2. Check how many of those aspects are covered by the answer
        3. Rate the answer
            - if the answer misses half or more main aspects, it should NOT get a rating higher than 2
            - if the answer gets all the important aspects it should get a rating of 5. 
            - Minor omissions must be ignored. 
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
                inferenceConfig={"maxTokens": 2000, "temperature": 0.2, "topP": 0.9},
            )
        
            # Extract and print the response text.
            return response["output"]["message"]["content"][0]["text"]
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)
    
class FormattingAgent: 
    """This Agent merely generates a formatted (JSON) rating based on what the Reasoning Agent provides. 
    It is just a formatter. 
    It does not do any reasoning, it only extracts structured information out of the provided text. 
    
    This is meant to be used by the orchestrater (RatingAgent).
    """
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    class FormattedRating: 
        rating: float 
        explanation: str
        
        def __init__(self, rating: float, explanation: str): 
            self.rating = rating 
            self.explanation = explanation
    
    def __init__(self, exec_context: ExecutionContext):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid
    
    def format_rating(self, rating: str) -> FormattedRating: 
    
        # Define the First Prompt
        system_prompt = f"""
        You are a JSON formatter with a brain. 
        You are being given some text that rates a user answer to a question in the context of a Quiz. In that text there two VERY IMPORTANT things that I need: 
        1. A rating, expressed as either an integer or a float with a single decimal (from 1 to 5)
        2. An explanation of the rating.
        You are asked to extract these two pieces of information and provide them in a JSON format. 
        This is the text from which you must extract that information:
        ----------------
        {rating}
        ----------------

        Provide the rating in a JSON format. You must provide at least the following fields:
        - rating which will contain the rating value as a float
        - explanation which will contain the explanations for the rating, with corrections of what the user got wrong. Be synthetic. 

        ONLY provide the answer in a JSON format. Do not provide additional text. 
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
                inferenceConfig={"maxTokens": 2000, "temperature": 0, "topP": 0.9},
            )
            
            # Extract and print the response text.
            response_text = response["output"]["message"]["content"][0]["text"]
            
            rating = json.loads(response_text)
            
            self.logger.log(self.cid, f'Formatted response into JSON: {response_text}')
            
            return self.FormattedRating(rating.get('rating', 0), rating.get('explanation', ''))
            
        except (json.JSONDecodeError) as e: 
            print(f'Error decoding JSON. Expected json from LLM but got {response_text}')
            raise e
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)
            

class RatingAgent: 
    """This is the Agent that will perform the rating of the user's answer. 
    It orchestrates other agents to perform its task. 
    
    This is the class that should be used to rate answers in Tome.
    """
    exec_context: ExecutionContext
    topic_code: str 
    section_code: str
    
    def __init__(self, exec_context: ExecutionContext, topic_code: str, section_code: str):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid
        self.topic_code = topic_code
        self.section_code = section_code
    
    def rate_answer(self, question: str, answer: str) -> AnswerRating: 
        
        try:
            # 1. Use the Reasoning Agent to accurately rate the answer using COT
            reasoning = RatingReasoningAgent(self.exec_context).rate_answer(question, answer, self.topic_code, self.section_code)
            
            # 2. Use the Formatting Agent to extract the rating in a JSON 
            formatted_rating = FormattingAgent(self.exec_context).format_rating(reasoning)
            
            # 3. Return the answer
            return AnswerRating(formatted_rating.rating, formatted_rating.explanation, reasoning)
            
        except (ClientError, Exception) as e:
            print(f"ERROR: {e}")
            exit(1)