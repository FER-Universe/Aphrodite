import tiktoken


def calculate_num_tokens(sentence: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(sentence))
    return num_tokens
