import hashlib

def getMd5(filename: str) -> str:
    """Get a file md5 string"""
    return hashlib.md5(open(filename,'rb').read()).hexdigest()
