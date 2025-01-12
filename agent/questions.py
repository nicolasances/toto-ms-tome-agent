from dataclasses import dataclass
from typing import List
import boto3
from botocore.exceptions import ClientError
import json
import time
from totoapicontroller.model.ExecutionContext import ExecutionContext
import concurrent.futures
from kb.kb import KnowledgeBase
from model.topic import Topic, TopicSection
from model.topicreview import TopicReviewQuestion
import random

client = boto3.client("bedrock-runtime", region_name="eu-west-1")

@dataclass
class GeneratedQuestions: 
    topic_code: str 
    topic_title: str 
    section: TopicSection
    questions: List[str]
    response_time: float 
    response_time_unit: str 
    
    def __init__(self, topic: Topic, section: TopicSection, response_time: float, response_time_unit: str, questions: List[str]):
        self.topic_code = topic.code
        self.topic_title = topic.title
        self.section = section
        self.response_time = response_time
        self.response_time_unit = response_time_unit
        self.questions = questions


    
class QuestionsGenerator: 
    """Questions generator
    Generates all the questions for a given topic in order to create a Topic Review
    """
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid

    def generate_topic_review_questions(self, topic: Topic, topic_review_id: str) -> List[TopicReviewQuestion]:
        """This method generates a set of questions for a topic review. 
        It will generate questions for each section of a topic. 
        It parallelizes the generation of questions for each section, sending multiple parallel requests to the LLM.

        Args:
            topic (Topic): the topic to generate questions for

        Returns:
            List[GeneratedQuestions]: a list of GeneratedQuestions
        """
        # 1. Split the sections in chunks of 10
        chunk_size = 10
        chunks = [topic.sections[i:i + chunk_size] for i in range(0, len(topic.sections), chunk_size)]
        
        # 2. For each chunk, parallelize the question generation
        
        # List of questions for the Topic Review
        questions: List[TopicReviewQuestion] = []
        
        # Go through each chunk of sections and generate the questions
        for chunk in chunks: 
            # Parallelize the generation of questions
            with concurrent.futures.ThreadPoolExecutor() as executor_topic:
                futures = [executor_topic.submit(self.generate_questions, topic, section) for section in topic.sections]
                results:  List[GeneratedQuestions] = [future.result() for future in concurrent.futures.as_completed(futures)]
            
            # Sort the sections by their order
            results.sort(key=lambda x: x.section.order)
            
            # For each item in results, extract the list of questions and translate into a list of TopicReviewQuestion objects to be appended to the questions array
            for i, result in enumerate(results):
                for j, question in enumerate(result.questions):
                    # Define the sequence order of the question in the topic review. Order is 1-indexed
                    order = i * len(result.questions) + j + 1
                    
                    trq = TopicReviewQuestion(
                        topic_code = topic.code, 
                        topic_review_id = topic_review_id,
                        section_code = result.section.code,
                        section_title = result.section.title,
                        question = question,
                        question_num = order
                    )
                    
                    questions.append(trq)
                
        # Update the questions with the total number of generated questions
        num_questions_in_tr = len(questions)
        
        for q in questions: 
            q.num_questions_in_tr = num_questions_in_tr
        
        return questions
    
    def generate_questions(self, topic: Topic, section: TopicSection) -> GeneratedQuestions: 
        """Generates a list of questions. 
        Each question is generated from a given provider.

        Params
        ----
        - kb a string containing the knowledge base to generate questions on

        Returns
        ----
        - a list of questions
        """
        # 1. Load the context
        kb = KnowledgeBase(self.exec_context).get_knowledge(topic.code, section.code)
        
        # Pick up the Generators
        generators = [
            SequenceQG(self.exec_context, num_questions=1), 
            GenericQG(self.exec_context, num_questions=2),
            DatesAndNamesQG(self.exec_context, num_questions=1), 
        ]
        
        # 2. Generate the questions
        start_time = time.time()
        
        results = []
        for generator in generators: 
            questions = generator.generate_questions(kb)
            results.append(questions)
            
        end_time = time.time()
        
        # Flatten the results
        flattened_results = [question for sublist in results for question in sublist]
        
        self.exec_context.logger.log(self.exec_context.cid, f'Generated Questions for section {section.code}')
            
        # Create a GeneratedQuestions 
        return GeneratedQuestions(
            topic=topic, 
            section=section, 
            response_time=(end_time - start_time), 
            response_time_unit="seconds",
            questions=flattened_results
        )
        
            

# #######################################################
# Generic Questions Generator
# #######################################################
class GenericQG: 
    """This Question Generator generates a set of questions that are generic on the topic. 
    """
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext, num_questions: int = 1):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid
        self.num_questions = num_questions


    def generate_questions(self, kb: str) -> List[str]: 
        system_prompt = f"""
        You are acting as a Quiz's question generating engine. Your role is, given a knowledge base (hereafter KB) to generate questions based on the content of KB. 
        The questions CAN ONLY REFER to the content of KB. 
        The following is the KB that is given to you: 
        ----------------
        {kb}
        ----------------
        Generate {self.num_questions} questions based on the KB. 
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
            # Send the message to the model, using a basic inference configuration.
            # Using a higher temperature because I do want some variance in the questions, with t=0 I always get the same questions
            response = client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 2000, "temperature": 0.3, "topP": 0.9},
            )
            
            # Extract the response
            response_text = response["output"]["message"]["content"][0]["text"]
            
            questions = json.loads(response_text)['questions']
        
            # Return the list of questions
            return questions
            
        except (json.JSONDecodeError) as e: 
            print(f'Error decoding JSON. Expected json from LLM but got {response_text}')
            raise e
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)
            
            
# #######################################################
# Date and Names Question generator             
# #######################################################
class DatesAndNamesQG: 
    """This Question Generator generates a set of questions that only relate to dates and names. 
    It will ask the user questions like "In which date did .... happen?" or "What was the name of the person that ....?"
    """
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext, num_questions: int = 1):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid
        self.num_questions = num_questions


    def generate_questions(self, kb: str) -> List[str]: 
        """Generates a list of questions

        Params
        ----
        - kb a string containing the knowledge base to generate questions on

        Returns
        ----
        - a list of questions
        """
        # 1. Define the System Prompt
        system_prompt = f"""
        You are acting as a Quiz's question generating engine. 
        Your role is, given a knowledge base (hereafter KB) to generate questions based on the content of KB. 
        The questions CAN ONLY REFER to the content of KB. 
        The following is the KB that is given to you: 
        ----------------
        {kb}
        ----------------
        Generate {self.num_questions} questions that can either be:
        1. A question on a date (e.g. on what date did this event ... happen?)
        2. A question on a name (e.g. what was the name of the person that ...?)
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
            # Send the message to the model, using a basic inference configuration.
            # Using a higher temperature because I do want some variance in the questions, with t=0 I always get the same questions
            response = client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 2000, "temperature": 0.3, "topP": 0.9},
            )
            
            # Extract the response
            response_text = response["output"]["message"]["content"][0]["text"]
            
            questions = json.loads(response_text)['questions']
        
            # Return the list of questions
            return questions
            
        except (json.JSONDecodeError) as e: 
            print(f'Error decoding JSON. Expected json from LLM but got {response_text}')
            raise e
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)
            

# #######################################################
# Sequence Questions Generator
# #######################################################
class SequenceQG: 
    """This Question Generator generates questions focused on a sequence of event. 
    It will ask the user questions like "Describe the sequence of events of ... "
    """
    
    model_id = 'eu.anthropic.claude-3-5-sonnet-20240620-v1:0'
    
    def __init__(self, exec_context: ExecutionContext, num_questions: int = 1):
        self.exec_context = exec_context;
        self.logger = exec_context.logger
        self.cid = exec_context.cid
        self.num_questions = num_questions


    def generate_questions(self, kb: str) -> List[str]: 
        """Generates a list of questions

        Params
        ----
        - kb a string containing the knowledge base to generate questions on

        Returns
        ----
        - a list of questions
        """
        # 1. Define the System Prompt
        system_prompt = f"""
        You are acting as a Quiz's question generating engine. 
        Your role is, given a knowledge base (hereafter KB) to generate questions based on the content of KB. 
        The questions CAN ONLY REFER to the content of KB. 
        The following is the KB that is given to you: 
        ----------------
        {kb}
        ----------------
        Generate {self.num_questions} questions that require the user to describe the main sequence of events described in the Knowledge Base. 
        The question must start with a small introduction (a couple of sentences) of the topic, to contextualize the question. You can add your own knowledge (not necessarily in the knowledge base) to this. 
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
            # Send the message to the model, using a basic inference configuration.
            # Using a higher temperature because I do want some variance in the questions, with t=0 I always get the same questions
            response = client.converse(
                modelId=self.model_id,
                messages=conversation,
                inferenceConfig={"maxTokens": 2000, "temperature": 0.3, "topP": 0.9},
            )
            
            # Extract the response
            response_text = response["output"]["message"]["content"][0]["text"]
            
            questions = json.loads(response_text)['questions']
        
            # Return the list of questions
            return questions
            
        except (json.JSONDecodeError) as e: 
            print(f'Error decoding JSON. Expected json from LLM but got {response_text}')
            raise e
        
        except (ClientError, Exception) as e:
            print(f"ERROR: Can't invoke '{self.model_id}'. Reason: {e}")
            exit(1)
            