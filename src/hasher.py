from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str):
    return pwd_context.hash(password)

# Replace 'your_password' with the actual password
passwords = ['aaa', 'aab', 'aac', 'aad', 'aae', 'aaf', 'aag', 'aah', 'aai', 'aaj',
             'aba', 'abb', 'abc', 'aca', 'acb', 'acc', 'acd', 'ace', 'ada', 'adb']

for password in passwords:
    hashed_password = hash_password(password)
    print(password + ":", hashed_password)