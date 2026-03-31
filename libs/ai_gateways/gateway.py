import inspect 
import importlib 
import types 
from typing import Generator, List, Dict 

from .objects import ContentBlock

class AICompanyGateway: 
    """Class for standardized gateways to AI company APIs"""

    # the name of the AI company
    name = None 

    def __init__(self, api_key:str=None, api_secret:str=None, region:str=None) -> None: 
        """Sets up the object 

        Args:
            api_key (str): api key to the AI company's API 
            api_secret (str): api secret key to the AI company's API 
            region (str): the AWS region (only used for the AWS Bedrock gateway)
        """
        self.setup_client(api_key, api_secret, region)


    @classmethod
    def factory(cls, company:str=None, **opts) -> 'AICompanyGateway': 
        """Factory method to create a subclass of AICompanyGateway

        Args:
            company (str, optional): the name of the company to create. Defaults to None.

        Raises:
            Exception: raises an exception if an unknown company is passed

        Returns:
            AICompanyGateway: Returns an instance of the <company>_Gateway class 
        """
        def _find_class(module:types.ModuleType, company:str) -> type: 
            """Finds a class within a module 

            Args:
                module (types.ModuleType): the module to search in 
                company (str): the name of the company to look for 

            Raises:
                Exception: raises an exception if an unknown company is passed

            Returns:
                type: The class object for the company gateway 
            """
            class_name = company.lower() + 'gateway' 
            for m in inspect.getmembers(module, inspect.isclass): 
                if m[0].lower() == class_name: 
                    return m[1] 
            raise Exception(f"Cannot find class for AI company {company} in {module.__name__}")

        # search for the module in this folder with the company name 
        module = importlib.import_module("ai_interviewer_libs.ai_gateways." + company + "_gateway") 
        # find the gateway class for the company 
        AICompanyGatewayClass = _find_class(module, company) 
        return AICompanyGatewayClass(**opts) 


    def setup_client(self, api_key:str=None, api_secret:str=None, region:str=None) -> None: 
        """Sets up the client to the AI company SDK 

        Args:
            api_key (str): the api key 
            api_secret (str): the secret key
            region (str): the AWS region (only used for the AWS Bedrock gateway)
        """
        self.__client = None 


    def create_message(self, model:str, messages:List[ContentBlock], system_message:str=None, cache_control:bool=True, model_params:dict={}, **kwargs) -> str: 
        """Returns a message from the API. Overriden by subclass 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.
            cache_control (bool): True to use cache control, False otherwise. Defaults to True.
            model_params (dict): Model params to pass to the API. Defaults to {}.

        Returns:
            str: the messsage sent by the API 
        """
        pass 


    def stream_message(self, model:str, messages:List[ContentBlock], system_message:str=None, cache_control:bool=True, model_params:dict={}, **kwargs) -> Generator[str, None, None]: 
        """Streams a message from the API. Overriden by subclass 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.
            cache_control (bool): True to use cache control, False otherwise. Defaults to True.
            model_params (dict): Model params to pass to the API. Defaults to {}.

        Yields:
            Generator[str, None, None]: yields the messages sent by the AI 
        """
        pass  


    def count_tokens(self, model:str, messages:List[ContentBlock], system_message:str=None, **kwargs) -> int: 
        """Counts the number of tokens in a message. Overriden by subclass

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.

        Returns:
            int: the number of tokens 
        """
        pass 


    def convert_to_api_messages(self, messages:List[ContentBlock], cache_control:bool) -> List[Dict]: 
        """Converts the standardized list of messages to the API specific format. Overriden by subclass

        Args:
            messages (List[ContentBlock]): the messages of the conversation so far in standardized ContentBlock form
            cache_control (bool): True to use cache control, False otherwise

        Returns:
            List[Dict]: a list of messages in the format that the API likes
        """
        pass