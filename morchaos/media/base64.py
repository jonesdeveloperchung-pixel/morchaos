"""Base64 encoding and decoding utilities."""

import base64
from pathlib import Path
from typing import Union

def encode_bytes(data: bytes) -> str:
    """Encode bytes to base64 string."""
    return base64.b64encode(data).decode('ascii')

def decode_bytes(data: str) -> bytes:
    """Decode base64 string to bytes."""
    return base64.b64decode(data.encode('ascii'))

def encode_string(text: str, encoding: str = 'utf-8') -> str:
    """Encode string to base64."""
    return encode_bytes(text.encode(encoding))

def decode_string(data: str, encoding: str = 'utf-8') -> str:
    """Decode base64 to string."""
    return decode_bytes(data).decode(encoding)

def encode_file(file_path: Union[str, Path]) -> str:
    """Encode file contents to base64."""
    with open(file_path, 'rb') as f:
        return encode_bytes(f.read())

def decode_to_file(data: str, file_path: Union[str, Path]) -> None:
    """Decode base64 and save to file."""
    file_path = Path(file_path)
    file_path.parent.mkdir(parents=True, exist_ok=True)
    
    with file_path.open('wb') as f:
        f.write(decode_bytes(data))