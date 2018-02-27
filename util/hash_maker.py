import hashlib

def get_md5(md5_str):
    h = hashlib.md5()
    h.update(md5_str.encode('utf-8'))
    return h.hexdigest()