import base64
import os
import tempfile

def base64_to_temp_file(image: str) -> tempfile.NamedTemporaryFile:
    """
    Intended to be used with "with" statement.
    """
    with tempfile.NamedTemporaryFile(mode='wb+', delete=False) as temp_file:
        temp_file.write(base64.b64decode(image))
        temp_file.seek(0)
        yield temp_file
        os.unlink(temp_file.name)

def rle_encode(data: str, delimiter: str = '|') -> str:
    encoding = []
    prev_char = ''
    count = 0

    for char in data:
        if char != prev_char:
            if prev_char:
                encoding.append(f"{count}{delimiter}{prev_char}")
            count = 1
            prev_char = char
        else:
            count += 1
    # Append the last run
    if prev_char:
        encoding.append(f"{count}{delimiter}{prev_char}")
    
    return ''.join(encoding)

def rle_decode(data: str, delimiter: str = '|') -> str:
    decoding = []
    i = 0
    n = len(data)

    while i < n:
        # Find the delimiter
        delimiter_index = data.find(delimiter, i)
        if delimiter_index == -1:
            raise ValueError(f"Delimiter '{delimiter}' not found in the encoded data at position {i}.")
        
        # Extract the count
        count_str = data[i:delimiter_index]
        if not count_str.isdigit():
            raise ValueError(f"Invalid count '{count_str}' at position {i}-{delimiter_index}.")
        
        count = int(count_str)
        i = delimiter_index + len(delimiter)
        
        if i >= n:
            raise ValueError(f"Missing character after delimiter at position {i}.")
        
        # Extract the character
        char = data[i]
        decoding.append(char * count)
        i += 1
    
    return ''.join(decoding)