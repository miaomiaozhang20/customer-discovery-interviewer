import boto3 
from typing import List, Dict, Generator 

from .gateway import AICompanyGateway
from .objects import ContentBlock

class BedrockGateway (AICompanyGateway): 
    """Gateway for AWS Bedrock Converse API"""
    name = 'bedrock' 

    def setup_client(self, api_key:str=None, api_secret:str=None, region:str=None) -> None: 
        """Sets up the client to the AI company SDK 

        Args:
            api_key (str): the api key 
            api_secret (str): the secret key
            region (str): the AWS region (only used for the AWS Bedrock gateway)
        """
        self.__client = boto3.client(
            service_name='bedrock-runtime',
            region_name=region, 
            aws_access_key_id=api_key, 
            aws_secret_access_key=api_secret 
        )


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
                    'text': system_message, 
                }
            ]
        if cache_control: 
            system.append({'cachePoint': {'type': 'default'}})
        msg = self.__client.converse(
            modelId=model, 
            messages=self.convert_to_api_messages(messages, cache_control), 
            system=system, 
            inferenceConfig=model_params,
            **kwargs
        ) 
        return msg['output']['message']['content'][0]['text']


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
                    'text': system_message, 
                }
            ]
        if cache_control: 
            system.append({'cachePoint': {'type': 'default'}})
        msg = self.__client.converse_stream(
            modelId=model, 
            messages=self.convert_to_api_messages(messages, cache_control), 
            system=system, 
            inferenceConfig=model_params,
            **kwargs
        ) 
        for event in msg['stream']:
            if 'contentBlockDelta' in event: 
                yield event['contentBlockDelta']['delta']['text']


    def count_tokens(self, model:str, messages:List[ContentBlock], system_message:str=None, **kwargs) -> int: 
        """Counts the number of tokens in a message 

        Args:
            model (str): the name of the model 
            messages (List[ContentBlock]): a list of messages of the conversation so far 
            system_message (str): a system message, if any. The system message can also be included in the messages param. Defaults to None.

        Returns:
            int: the number of tokens 
        """
        msg = self.__client.converse(
            modelId=model, 
            messages=self.convert_to_api_messages(messages, True), 
            system=[{'text': system_message}], 
            inferenceConfig={'maxTokens': 1},
            **kwargs
        ) 
        return msg['usage']['totalTokens']


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
                            'text': msg.text 
                        }
                    ]
                })
            elif msg.type == 'document': 
                content = [
                    {
                        'document': {
                            'name': msg.name, 
                            'format': msg.format, 
                            'source': msg.source
                        }
                    }, 
                    {
                        'text': msg.accompanying_text.text
                    }
                ]
                if cache_control: 
                    content.append({"cachePoint": { "type":"default"}})
                api_messages.append({
                    'role': msg.role, 
                    'content': content 
                })
        if cache_control and messages[-1].type == 'text':  
            api_messages[-1]['content'].append({"cachePoint": { "type":"default"}})
        return api_messages 