def format_str_spacing_util(sentence:str, spaces_in_between: int = 50) -> str:
    sentence_length: int = len(sentence)
    space_dif: int = spaces_in_between - sentence_length
    formatted_sentence: str = sentence

    if space_dif < 5:
        formatted_sentence += " " * 25
    else:
        formatted_sentence += " " * space_dif

    return formatted_sentence