from typing import List
import boto3
from botocore.exceptions import ClientError
import json
import time
import os
from google.cloud import storage
from totoapicontroller.model.ExecutionContext import ExecutionContext

client = boto3.client("bedrock-runtime", region_name="eu-west-1")

class GeneratedQuestions: 
    response_time: float 
    response_time_unit: str 
    questions: List[str]
    
    def __init__(self, response_time: float, response_time_unit: str, questions: List[str]):
        self.response_time = response_time
        self.response_time_unit = response_time_unit
        self.questions = questions
    
class QuestionsGenerator: 
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    knowledge_base_folder = 'kb'
    
    def __init__(self, exec_context: ExecutionContext):
        self.client = storage.Client()
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid
        
        if os.getenv('ENVIRONMENT') == 'dev':
            self.bucket = self.client.get_bucket('totoexperiments-tome-bucket')
        else: 
            self.bucket = self.client.get_bucket('totolive-tome-bucket')


    def generate_questions(self, num_questions: int = 10) -> GeneratedQuestions: 
        """Generates a list of questions

        Params
        ----
        - kb a string containing the knowledge base to generate questions on

        Returns
        ----
        - a list of questions
        """
        # 1. Load the context
        kb_file_path = f'{self.knowledge_base_folder}/kb_cortes_mexico.txt'
        
        blob = self.bucket.blob(kb_file_path)
        
        self.logger.log(self.cid, f'Reading Knowledge Base file: {blob.name} from GCS bucket {self.bucket.name}')

        with blob.open('r') as file:
            kb = file.read()

        # 2. Define the System Prompt
        system_prompt = f"""
        You are acting as a Quiz's question generating engine. Your role is, given a knowledge base (hereafter KB) to generate 10 questions based on the content of KB. 
        The questions CAN ONLY REFER to the content of KB. 
        The following is the KB that is given to you: 
        ----------------
        {kb}
        ----------------
        Generate {num_questions} questions based on the KB. 
        Questions should require a bit of elaboration, not just a few words as an answer. 
        Provide the questions as a JSON object with only one field called questions which will be an array of strings.
        Do not provide anything else. Only provide a JSON object. No other text.
        """

        conversation = [
            {
                "role": "user", 
                "content": [{"text": system_prompt}]
            },
        ]
        
        try:
            start_time = time.time()
            
            # Send the message to the model, using a basic inference configuration.
            # Using a higher temperature because I do want some variance in the questions, with t=0 I always get the same questions
            response = client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 2000, "temperature": 0.3, "topP": 0.9},
            )
            
            end_time = time.time()
            
            # Extract the response
            response_text = response["output"]["message"]["content"][0]["text"]
            
            questions = json.loads(response_text)['questions']
        
            # Extract and print the response text.
            return GeneratedQuestions(
                response_time = end_time - start_time, 
                response_time_unit = "seconds", 
                questions = questions
            )
            
        except (json.JSONDecodeError) as e: 
            print(f'Error decoding JSON. Expected json from LLM but got {response_text}')
            raise e
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)
            