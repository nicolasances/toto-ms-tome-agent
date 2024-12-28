
from flask import Request
from agent.QuestionsGenerator import QuestionsGenerator
from config.Config import Config

from totoapicontroller.TotoDelegateDecorator import toto_delegate
from totoapicontroller.model.UserContext import UserContext
from totoapicontroller.model.ExecutionContext import ExecutionContext

@toto_delegate(config_class=Config)
def test(request: Request, user_context: UserContext, exec_context: ExecutionContext): 
    
    exec_context.logger.log(exec_context.cid, f"It's working!")
    
    resp = QuestionsGenerator(exec_context).generate_questions(num_questions=5)
    
    return {"ok": True, "questions": resp}