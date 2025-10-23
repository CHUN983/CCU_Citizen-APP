"""
Authentication service
"""

from typing import Optional
from models.user import User, UserCreate, UserLogin, UserInDB, Token
from utils.database import get_db_cursor
from utils.security import hash_password, verify_password, create_access_token


class AuthService:
    """Authentication service for user management"""

    @staticmethod
    def create_user(user_data: UserCreate) -> Optional[User]:
        """
        Create a new user

        Args:
            user_data: User creation data

        Returns:
            Created user or None if username/email exists
        """
        password_hash = hash_password(user_data.password)

        query = """
            INSERT INTO users (username, email, password_hash, full_name, role)
            VALUES (%s, %s, %s, %s, %s)
        """

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    query,
                    (user_data.username, user_data.email, password_hash,
                     user_data.full_name, user_data.role.value)
                )

                user_id = cursor.lastrowid

                # Fetch the created user
                cursor.execute(
                    "SELECT id, username, email, full_name, role, is_active, created_at, updated_at "
                    "FROM users WHERE id = %s",
                    (user_id,)
                )
                user_row = cursor.fetchone()

                if user_row:
                    return User(**user_row)

        except Exception as e:
            print(f"Error creating user: {e}")
            return None

    @staticmethod
    def authenticate_user(login_data: UserLogin) -> Optional[UserInDB]:
        """
        Authenticate user with username and password

        Args:
            login_data: User login credentials

        Returns:
            User with password hash or None if authentication fails
        """
        query = """
            SELECT id, username, email, password_hash, full_name, role, is_active, created_at, updated_at
            FROM users
            WHERE username = %s AND is_active = TRUE
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (login_data.username,))
            user_row = cursor.fetchone()

            if not user_row:
                return None

            # Verify password
            if not verify_password(login_data.password, user_row['password_hash']):
                return None

            return UserInDB(**user_row)

    @staticmethod
    def login(login_data: UserLogin) -> Optional[Token]:
        """
        Login user and generate JWT token

        Args:
            login_data: User login credentials

        Returns:
            JWT token or None if authentication fails
        """
        user = AuthService.authenticate_user(login_data)

        if not user:
            return None

        # Create access token
        token_data = {
            "user_id": user.id,
            "username": user.username,
            "role": user.role.value
        }

        access_token = create_access_token(token_data)

        return Token(access_token=access_token, token_type="bearer")

    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """
        Get user by ID

        Args:
            user_id: User ID

        Returns:
            User or None if not found
        """
        query = """
            SELECT id, username, email, full_name, role, is_active, created_at, updated_at
            FROM users
            WHERE id = %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            user_row = cursor.fetchone()

            if user_row:
                return User(**user_row)

        return None

    @staticmethod
    def get_user_by_username(username: str) -> Optional[User]:
        """
        Get user by username

        Args:
            username: Username

        Returns:
            User or None if not found
        """
        query = """
            SELECT id, username, email, full_name, role, is_active, created_at, updated_at
            FROM users
            WHERE username = %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (username,))
            user_row = cursor.fetchone()

            if user_row:
                return User(**user_row)

        return None
