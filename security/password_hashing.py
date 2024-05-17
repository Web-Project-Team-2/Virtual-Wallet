from passlib.context import CryptContext

# hashing algo
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    new_hashed_pass = get_password_hash(plain_password)
    return new_hashed_pass == hashed_password


def get_password_hash(password):
    password = _hash_password(password)
    return password


def _hash_password(password: str):
    from hashlib import sha256
    return sha256(password.encode('utf-8')).hexdigest()
