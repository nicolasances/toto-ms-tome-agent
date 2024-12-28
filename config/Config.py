from totoapicontroller.model.TotoConfig import TotoConfig
from totoapicontroller.model.singleton import singleton
from totoapicontroller.model.TotoConfig import CloudProvider

@singleton
class Config(TotoConfig): 
    
    def __init__(self):
        super().__init__(cloud_provider=CloudProvider.AWS)
        
        self.logger.log("INIT", "Configuration loaded!")
        
    def get_api_name(self) -> str:
        return "test-api"