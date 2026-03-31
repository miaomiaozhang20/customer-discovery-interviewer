def read_md(fpath:str) -> str: 
    """Reads a markdown file 

    Args:
        fpath (str): the path to the markdown file 

    Returns:
        str: the text in the markdown file 
    """
    with open(fpath, 'r') as file: 
        text = file.read() 
    return text 