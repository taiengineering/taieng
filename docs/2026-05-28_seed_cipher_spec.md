#### 2. `utils/seed_cipher.py` (신규)

**`cryptography` 라이브러리가 SEED-128-CBC를 네이티브 지원.**
별도 마이너 패키지 불필요. `pip install cryptography` (이미 설치되어 있을 가능성 높음).

```python
"""
utils/seed_cipher.py — SEED-128-CBC 복호화 (cryptography 라이브러리 사용)
"""
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend


def seed_cbc_decrypt(key: bytes, iv: bytes, encrypted: bytes) -> bytes:
    """
    SEED-128-CBC 복호화 + PKCS5 언패딩.
    key: 16바이트, iv: 16바이트, encrypted: 암호문
    """
    cipher = Cipher(algorithms.SEED(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    decrypted = decryptor.update(encrypted) + decryptor.finalize()
    return _pkcs5_unpad(decrypted)


def seed_cbc_encrypt(key: bytes, iv: bytes, plaintext: bytes) -> bytes:
    """SEED-128-CBC 암호화 + PKCS5 패딩. (필요 시 사용)"""
    padded = _pkcs5_pad(plaintext)
    cipher = Cipher(algorithms.SEED(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return encryptor.update(padded) + encryptor.finalize()


def _pkcs5_unpad(data: bytes) -> bytes:
    if not data:
        return data
    pad_len = data[-1]
    if pad_len < 1 or pad_len > 16:
        return data
    if data[-pad_len:] != bytes([pad_len] * pad_len):
        return data
    return data[:-pad_len]


def _pkcs5_pad(data: bytes, block_size: int = 16) -> bytes:
    pad_len = block_size - (len(data) % block_size)
    return data + bytes([pad_len] * pad_len)
```

requirements.txt에 추가 (이미 없는 경우만):
```
cryptography>=42.0.0
```

**pyseedcipher, kisa-seed 등 마이너 패키지 불필요. cryptography만으로 충분.**
