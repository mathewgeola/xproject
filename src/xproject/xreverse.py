import base64
import binascii
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from typing import Literal, Optional


def string_to_hex(string: str) -> str:
    """
    >>> string_to_hex("hi")
    '\\\\x68\\\\x69'

    """
    return ''.join(f'\\x{ord(s):02x}' for s in string)


def hex_to_string(hex_string: str) -> str:
    """
    >>> hex_to_string("\\\\x68\\\\x69")
    'hi'

    """
    hex_pairs = [hex_string[i:i + 4] for i in range(0, len(hex_string), 4)]
    return "".join(chr(int(pair[2:], 16)) for pair in hex_pairs if pair.startswith("\\x"))


def aes_encrypt(
        data: str,
        key: str,
        iv: Optional[str] = None,
        mode=AES.MODE_CBC,
        style: str = "pkcs7",
        fmt: Literal["hex", "base64"] = "base64"
) -> str:
    """
    默认: AES CBC　PKCS7Padding

    """
    data = data.encode()
    key = key.encode()
    if iv is not None:
        iv = iv.encode()

    cipher = AES.new(key, mode, iv)
    padded_data = pad(data, AES.block_size, style)
    encrypted_data = cipher.encrypt(padded_data)
    if fmt == "hex":
        encrypted_data = binascii.hexlify(encrypted_data).decode()
    elif fmt == "base64":
        encrypted_data = base64.b64encode(encrypted_data).decode()
    else:
        raise ValueError(
            f"Invalid type for 'fmt': "
            f"Expected ` Literal[\"hex\", \"base64\"] `, "
            f"but got {type(fmt).__name__!r} (value: {fmt!r})"
        )
    return encrypted_data
