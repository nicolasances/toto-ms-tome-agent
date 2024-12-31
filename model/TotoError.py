
class TotoError: 
    
    code: int
    msg: str
    reasonCode: str # An application-specific code to be used for front-end error-handling
    
    def __init__(self, code: int, msg: str, reasonCode: str = None): 
        self.code = code 
        self.msg = msg
        self.reasonCode = reasonCode