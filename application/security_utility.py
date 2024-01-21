import hashlib


class SecurityUtility:
    SECRET_SALT = b'ad'

    @staticmethod
    def hash_password(password):
        hashed_password = hashlib.sha256(SecurityUtility.SECRET_SALT + password.encode()).hexdigest()
        return hashed_password
