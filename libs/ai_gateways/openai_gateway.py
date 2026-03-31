import openai 
from typing import List, Dict, Generator 

from .gateway import AICompanyGateway
from .objects import ContentBlock

class OpenAIGateway (AICompanyGateway): 
    name = 'openai' 

    def setup_client(self, api_key:str=None, api_secret:str=None, region:str=None) -> None: 
        """Sets up the client to the AI company SDK 

        Args:
            api_key (str): the api key 
            api_secret (str): the secret key
            region (str): the AWS region (only used for the AWS Bedrock gateway)
        """
        self.__client = openai.OpenAI(api_key=api_key) 


    def create_message(self, model:str, messages:List[ContentBlock], system_message:str=None, cache_control:bool=True, model_params:dict={}, **kwargs) -> str: 
        """Returns a message from the API. 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.
            cache_control (bool): True to use cache control, False otherwise. Defaults to True.
            model_params (dict): Model params to pass to the API. Defaults to {}.

        Returns:
            str: the messsage sent by the API 
        """
        messages = self.convert_to_api_messages(messages, cache_control) 
        if system_message and not self.__check_for_system_message(messages): 
            # add system message without overriding existing system message 
            messages.insert(0, {"role": "system", "content": system_message})
        msg = self.__client.chat.completions.create(
            model=model, 
            messages=messages, 
            **model_params, 
            **kwargs 
        ) 
        return msg.choices[0].message.content 


    def stream_message(self, model:str, messages:List[ContentBlock], system_message:str=None, cache_control:bool=True, model_params:dict={}, **kwargs) -> Generator[str, None, None]: 
        """Streams a message from the API. 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.
            cache_control (bool): True to use cache control, False otherwise. Defaults to True.
            model_params (dict): Model params to pass to the API. Defaults to {}.

        Yields:
            Generator[str, None, None]: yields the messages sent by the AI 
        """
        messages = self.convert_to_api_messages(messages, cache_control) 
        if system_message and not self.__check_for_system_message(messages): 
            # add system message without overriding existing system message 
            messages.insert(0, {"role": "system", "content": system_message})
        with self.__client.chat.completions.create(
            model=model, 
            messages=messages, 
            stream=True, 
            **model_params,
            **kwargs 
        ) as stream: 
            for chunk in stream: 
                yield chunk.choices[0].delta.content 


    def count_tokens(self, model:str, messages:List[ContentBlock], system_message:str=None, **kwargs) -> int: 
        """Counts the number of tokens in a message 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.

        Returns:
            int: the number of tokens 
        """
        raise NotImplementedError("Token counting for OpenAI has not been implemented yet")


    def convert_to_api_messages(self, messages:List[ContentBlock], cache_control:bool) -> List[Dict]: 
        """Converts the standardized list of messages to the API specific format. Overriden by subclass

        Args:
            messages (List[ContentBlock]): the messages of the conversation so far in standardized ContentBlock form
            cache_control (bool): True to use cache control, False otherwise

        Returns:
            List[Dict]: a list of messages in the format that the API likes
        """
        api_messages = [] 
        for msg in messages: 
            if msg.type == 'text': 
                api_messages.append({
                    'role': msg.role, 
                    'content': msg.text
                })
        return api_messages 
    

    def __check_for_system_message(self, messages:List[ContentBlock]) -> bool: 
        """Checks to see if there is a system message already in the conversation 

        Args:
            messages (List[ContentBlock]): messages in the conversation so far 

        Returns:
            bool: True if a system message exists already. False otherwise 
        """
        for msg in messages: 
            if msg['role'] == 'system': 
                return True 
        return False 