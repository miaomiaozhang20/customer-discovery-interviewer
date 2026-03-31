import anthropic 
from typing import List, Dict, Generator 

from .gateway import AICompanyGateway
from .objects import ContentBlock

class AnthropicGateway (AICompanyGateway): 
    name = 'anthropic' 

    def setup_client(self, api_key:str=None, api_secret:str=None, region:str=None) -> None: 
        """Sets up the client to the AI company SDK 

        Args:
            api_key (str): the api key 
            api_secret (str): the secret key
            region (str): the AWS region (only used for the AWS Bedrock gateway)
        """
        self.__client = anthropic.Anthropic(api_key=api_key) 


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
        system = [
            {
                'type': 'text', 
                'text': system_message
            }
        ]
        if cache_control: 
            system[0]['cache_control'] = {'type': 'ephemeral'}
        msg = self.__client.messages.create(
            model=model, 
            messages=self.convert_to_api_messages(messages, cache_control), 
            system=system, 
            **model_params,
            **kwargs
        ) 
        return msg.content[0].text 


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
        system = [
            {
                'type': 'text', 
                'text': system_message
            }
        ]
        if cache_control: 
            system[0]['cache_control'] = {'type': 'ephemeral'}
        with self.__client.messages.stream(
            model=model, 
            messages=self.convert_to_api_messages(messages, cache_control), 
            system=system, 
            **model_params, 
            **kwargs
        ) as stream: 
            for text_delta in stream.text_stream: 
                yield text_delta 


    def count_tokens(self, model:str, messages:List[ContentBlock], system_message:str=None, **kwargs) -> int: 
        """Counts the number of tokens in a message 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.

        Returns:
            int: the number of tokens 
        """
        response = self.__client.messages.count_tokens(
            model=model,
            messages=self.convert_to_api_messages(messages, True),
            system=system_message,
            **kwargs 
        )
        return response.input_tokens


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
                    'content': [
                        {
                            'type': 'text', 
                            'text': msg.text 
                        }
                    ]
                })
            elif msg.type == 'document': 
                content = [
                    {
                        'type': msg.type, 
                        'source': msg.source 
                    }, 
                    {
                        'type': 'text', 
                        'text': msg.accompanying_text.text
                    }
                ]
                if cache_control: 
                    content[0]['cache_control'] = {'type': 'ephemeral'}
                api_messages.append({
                    'role': msg.role, 
                    'content': content 
                })
        if cache_control: 
            api_messages[-1]['content'][0]['cache_control'] = {'type': 'ephemeral'}
        return api_messages 