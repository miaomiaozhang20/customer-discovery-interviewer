"""
Define some standardized objects to hold AI message blocks for a variety of types
"""

from dataclasses import dataclass

@dataclass 
class ContentBlock: 
    role:str # role: user or assistant
    type:str # type of content (ex. text, document, etc...)

@dataclass 
class TextBlock (ContentBlock): 
    text:str # the text 

@dataclass
class DocumentBlock (ContentBlock):
    name:str # name for the document 
    format:str # the format of the document 
    source:dict # the source of the document 
    accompanying_text:TextBlock # any accompanying text for the document