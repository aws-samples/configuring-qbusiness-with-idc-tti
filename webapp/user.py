# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""Simulates user database"""

from typing import Dict, Optional, Iterable
from flask_login import UserMixin


# Simulate user database
USERS_DB = {}


class User(UserMixin):

    """Custom User class."""

    def __init__(self, id_: str, name: str, email: str,
                 credential: Optional[Dict[str, str]]):
        self.id = id_
        self.name = name
        self.email = email
        self.credential = credential

    def claims(self) -> Iterable[tuple[str, str]]:
        """Use this method to render all assigned claims on profile page."""
        return {'subject': self.id,
                'email': self.email}.items()

    @staticmethod
    def create(user_id: str, name: str, email: str,
               credential: Optional[Dict[str, str]]) -> 'User':
        """create and store user data"""
        USERS_DB[user_id] = User(user_id, name, email, credential)
        return USERS_DB[user_id]

    @staticmethod
    def get(user_id: str) -> 'User':
        """Retrieve user data"""
        return USERS_DB.get(user_id)

    @staticmethod
    def delete(user_id: str) -> None:
        """delete user data"""
        if user_id in USERS_DB:
            USERS_DB.pop(user_id)
