# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

"""Q Business API helper custom exception"""


class ChatAIResponseScopeNotFound(Exception):
    """Raised when response scope not found in chat config"""


class ChatSyncConversationMissingParameters(Exception):
    """Raised when one of conversation or parent message id is missing"""


class AccessHelperException(Exception):
    """Access helper exception"""
