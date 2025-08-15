import base64
import binascii
from collections.abc import Buffer
from typing import Literal, cast

from Crypto.Cipher import AES
from Crypto.Util.Padding import pad


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
        iv: str | None = None,
        mode: Literal[1, 2] = AES.MODE_ECB,
        style: Literal["pkcs7", "x923", "iso7816"] = "pkcs7",
        fmt: Literal["base64", "hex"] = "base64"
) -> str:
    """
    default: AES ECB PKCS7Padding

    """
    data_bytes: bytes = data.encode()
    key_bytes: bytes = key.encode()
    if iv is not None:
        iv_bytes = iv.encode()
    else:
        iv_bytes = None

    if mode == AES.MODE_ECB:
        cipher = AES.new(key_bytes, mode)
    else:
        cipher = AES.new(key_bytes, mode, iv_bytes)

    padded_data_bytes: bytes = pad(data_bytes, AES.block_size, style)
    encrypted_data_bytes: bytes = cipher.encrypt(padded_data_bytes)
    encrypted_data_buffer: Buffer = cast(Buffer, encrypted_data_bytes)

    if fmt == "base64":
        encrypted_data: str = base64.b64encode(encrypted_data_buffer).decode()
    elif fmt == "hex":
        encrypted_data: str = binascii.hexlify(encrypted_data_buffer).decode()
    else:
        raise ValueError(
            f"Invalid type for 'fmt': "
            f"Expected ` Literal[\"base64\", \"hex\"] `, "
            f"but got {type(fmt).__name__!r} (value: {fmt!r})"
        )
    return encrypted_data


if __name__ == '__main__':
    print(aes_encrypt("123456", "1234567890123456"))
    print(aes_encrypt("123456", "1234567890123456", "1234567890123456", mode=AES.MODE_CBC))
    print(aes_encrypt("123456", "1234567890123456", "1234567890123456", mode=AES.MODE_ECB, style="x923"))
