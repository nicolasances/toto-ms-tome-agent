from dataclasses import dataclass
from typing import List
import boto3
from botocore.exceptions import ClientError
import json
import time
from totoapicontroller.model.ExecutionContext import ExecutionContext
import concurrent.futures
from kb.kb import KnowledgeBase
from model import topic
from model.topic import Topic, TopicSection

client = boto3.client("bedrock-runtime", region_name="eu-west-1")

@dataclass
class GeneratedQuestions: 
    topic: Topic
    section: TopicSection
    questions: List[str]
    response_time: float 
    response_time_unit: str 
    
    def __init__(self, topic: Topic, section: TopicSection, response_time: float, response_time_unit: str, questions: List[str]):
        self.topic = topic
        self.section = section
        self.response_time = response_time
        self.response_time_unit = response_time_unit
        self.questions = questions
    
class QuestionsGenerator: 
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid

    def generate_topic_review_questions(self, topic: Topic) -> List[GeneratedQuestions]:
        """This method generates a set of questions for a topic review. 
        It will generate questions for each section of a topic. 
        It parallelizes the generation of questions for each section, sending multiple parallel requests to the LLM.

        Args:
            topic (Topic): the topic to generate questions for

        Returns:
            List[GeneratedQuestions]: a list of GeneratedQuestions
        """
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.generate_questions, topic, section, num_questions=3) for section in topic.sections]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        # Convert the results into a list of GeneratedQuestions
        return results
            

    def generate_questions(self, topic: Topic, section: TopicSection, num_questions: int = 5) -> GeneratedQuestions: 
        """Generates a list of questions

        Params
        ----
        - kb a string containing the knowledge base to generate questions on

        Returns
        ----
        - a list of questions
        """
        # 1. Load the context
        kb = KnowledgeBase(self.exec_context).get_knowledge(topic.code, section.code)

        # 2. Define the System Prompt
        system_prompt = f"""
        You are acting as a Quiz's question generating engine. Your role is, given a knowledge base (hereafter KB) to generate {num_questions} questions based on the content of KB. 
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
                topic=topic,
                section=section,
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
            