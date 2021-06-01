import secrets
import hashlib

#Generates & returns a random string that will be used as the salt for authentication purposes.
def generateSalt():
    return secrets.token_hex(16)

#Generates & returns a token for authentication purposes
def generateHash(password, salt):
    return hashlib.md5(password.encode('utf-8') + salt.encode('utf-8')).hexdigest()