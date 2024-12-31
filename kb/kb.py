# This package stores all utility classes related to the knowledge base

from totoapicontroller.model.ExecutionContext import ExecutionContext
from config.Config import Config
from google.cloud import storage

class KnowledgeBase: 
    
    config: Config
    client: storage.Client
    knowledge_base_folder: str = 'kb'
    
    def __init__(self, exec_context: ExecutionContext): 
        self.config = exec_context.config 
        self.client = storage.Client()
        self.logger = exec_context.logger
        self.cid = exec_context.cid

    def get_knowledge(self, topic_code: str, section_code: str) -> str: 
        """Retrieves the content of the topic-section file.

        Args:
            topic_code (str): the code of the topic 
            section_code (str): the code of the section (corresponding to the name of the txt file containing the knowledge)

        Returns:
            str: _description_
        """
        
        # 1. Get the Bucket
        bucket = self.client.get_bucket(self.config.get_tome_bucket_name())
        
        # 2. Get the file in the bucket
        filepath = f'{self.knowledge_base_folder}/{topic_code}/{section_code}.txt'
        
        # 3. Get the blob
        blob = bucket.blob(filepath)
        
        # 4. Read the file
        self.logger.log(self.cid, f'Reading Knowledge Base file: {blob.name} from GCS bucket {bucket.name}')

        with blob.open('r') as file:
            kb = file.read()
            
        # 5. Return 
        return kb