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