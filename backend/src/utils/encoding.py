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

def rle_encode(data: str) -> str:
    encoding = ''
    prev_char = ''
    count = 1

    for char in data:
        if char != prev_char:
            if prev_char:
                encoding += str(count) + prev_char
            count = 1
            prev_char = char
        else:
            count += 1
    else:
        encoding += str(count) + prev_char
    return encoding

def rle_decode(data: str) -> str:
    decoding = ''
    count = ''
    for char in data:
        if char.isdigit():
            count += char
        else:
            decoding += char * int(count)
            count = ''
    return decoding