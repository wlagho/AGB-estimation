from datetime import datetime, timedelta
from utils.database import execute_query
import bcrypt
import secrets

class User:
    def __init__(self, id, email, password_hash, role, first_name, last_name,
                 organization, email_verified=False, two_factor_enabled=False,
                 phone_number=None, created_at=None, last_login=None):
        self.id = id
        self.email = email
        self.password_hash = password_hash
        self.role = role
        self.first_name = first_name
        self.last_name = last_name
        self.organization = organization
        self.email_verified = email_verified
        self.two_factor_enabled = two_factor_enabled
        self.phone_number = phone_number
        self.created_at = created_at
        self.last_login = last_login

    @staticmethod
    def hash_password(password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    @staticmethod
    def verify_password(password, password_hash):
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))

    @staticmethod
    def create(email, password, role, first_name, last_name, organization, phone_number=None):
        password_hash = User.hash_password(password)

        query = """
            INSERT INTO users (email, password_hash, role, first_name, last_name,
                             organization, phone_number)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            RETURNING id, email, password_hash, role, first_name, last_name,
                      organization, email_verified, two_factor_enabled, phone_number,
                      created_at, last_login
        """

        result = execute_query(
            query,
            (email, password_hash, role, first_name, last_name, organization, phone_number),
            fetch_one=True
        )

        if result:
            return User(**result)
        return None

    @staticmethod
    def get_by_email(email):
        query = """
            SELECT id, email, password_hash, role, first_name, last_name,
                   organization, email_verified, two_factor_enabled, phone_number,
                   created_at, last_login
            FROM users
            WHERE email = %s
        """

        result = execute_query(query, (email,), fetch_one=True)

        if result:
            return User(**result)
        return None

    @staticmethod
    def get_by_id(user_id):
        query = """
            SELECT id, email, password_hash, role, first_name, last_name,
                   organization, email_verified, two_factor_enabled, phone_number,
                   created_at, last_login
            FROM users
            WHERE id = %s
        """

        result = execute_query(query, (user_id,), fetch_one=True)

        if result:
            return User(**result)
        return None

    def update_last_login(self):
        query = "UPDATE users SET last_login = %s WHERE id = %s"
        execute_query(query, (datetime.now(), self.id))

    def enable_two_factor(self):
        query = "UPDATE users SET two_factor_enabled = true WHERE id = %s"
        execute_query(query, (self.id,))
        self.two_factor_enabled = True

    def disable_two_factor(self):
        query = "UPDATE users SET two_factor_enabled = false WHERE id = %s"
        execute_query(query, (self.id,))
        self.two_factor_enabled = False

    def verify_email(self):
        query = "UPDATE users SET email_verified = true WHERE id = %s"
        execute_query(query, (self.id,))
        self.email_verified = True

    def update_password(self, new_password):
        password_hash = User.hash_password(new_password)
        query = "UPDATE users SET password_hash = %s WHERE id = %s"
        execute_query(query, (password_hash, self.id))

    @staticmethod
    def get_all_users():
        query = """
            SELECT id, email, role, first_name, last_name, organization,
                   email_verified, two_factor_enabled, created_at, last_login
            FROM users
            ORDER BY created_at DESC
        """
        return execute_query(query, fetch_all=True)

class UserToken:
    @staticmethod
    def create_token(user_id, token_type, expiry_minutes=60):
        token = secrets.token_urlsafe(32)
        expires_at = datetime.now() + timedelta(minutes=expiry_minutes)

        query = """
            INSERT INTO user_tokens (user_id, token, token_type, expires_at)
            VALUES (%s, %s, %s, %s)
            RETURNING id, token
        """

        result = execute_query(
            query,
            (user_id, token, token_type, expires_at),
            fetch_one=True
        )

        return result['token'] if result else None

    @staticmethod
    def verify_token(token, token_type):
        query = """
            SELECT user_id, expires_at, used
            FROM user_tokens
            WHERE token = %s AND token_type = %s
        """

        result = execute_query(query, (token, token_type), fetch_one=True)

        if not result:
            return None

        if result['used']:
            return None

        if datetime.now() > result['expires_at']:
            return None

        return result['user_id']

    @staticmethod
    def mark_as_used(token):
        query = "UPDATE user_tokens SET used = true WHERE token = %s"
        execute_query(query, (token,))

    @staticmethod
    def delete_expired_tokens():
        query = "DELETE FROM user_tokens WHERE expires_at < %s"
        execute_query(query, (datetime.now(),))
