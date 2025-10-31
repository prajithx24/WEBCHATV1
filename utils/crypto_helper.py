from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import base64

BLOCK_SIZE = 16

def pad(s):
    pad_len = BLOCK_SIZE - len(s) % BLOCK_SIZE
    return s + (chr(pad_len) * pad_len)

def unpad(s):
    return s[:-ord(s[-1])]

def generate_key():
    key = get_random_bytes(32)
    return base64.b64encode(key)  # returns bytes

def create_cipher(key_str: str):
    decoded_key = base64.b64decode(key_str)
    return decoded_key

def encrypt_message(key: bytes, message: str) -> bytes:
    raw = pad(message).encode()
    iv = get_random_bytes(16)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    enc = cipher.encrypt(raw)
    return base64.b64encode(iv + enc)

def decrypt_message(key: bytes, encrypted: bytes) -> str:
    enc = base64.b64decode(encrypted)
    iv = enc[:16]
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(enc[16:])
    return unpad(decrypted.decode())
