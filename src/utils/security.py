import hashlib

def hash_sensitive_data(data):
    return hashlib.sha256(data.encode()).hexdigest()

def verify_hash(data, hashed_data):
    return hash_sensitive_data(data) == hashed_data