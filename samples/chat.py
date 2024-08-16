# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# pylint: disable=invalid-name,not-an-iterable,missing-function-docstring,logging-fstring-interpolation

"""Sample calls to Amazon Q Business Expert API helpers to get use chat functions"""

import os
import logging
import time
from datetime import timedelta
from typing import List, Optional

from rich.logging import RichHandler
from rich.pretty import pretty_repr
from qbapi_tools.api_helpers import QBusinessAPIHelpers
from qbapi_tools.datamodel import (
    ServiceConfig, SourceAttribution
)

logger = logging.getLogger("qbapi_samples")
logger.addHandler(RichHandler(
    show_time=False, show_path=False, show_level=False, rich_tracebacks=False
))
logger.setLevel(logging.getLevelName(os.environ.get('logging', 'DEBUG')))
WAIT_SECS_TO_SIMULATE_AGE = 10
WAIT_SECS_FOR_SETTING_UPDATE = 5
REGION_NAME = 'us-east-1'


def _citations(attributions: List[SourceAttribution]) -> List[str]:
    """Wrapper to stringify source attribution"""
    return list(map(
        lambda x: f"{x.citationNumber}/ {x.title} ({x.url})",
        attributions
    ))


def print_conversation_list(app_id: str, user_id: str):
    """Print active conversations for a given user"""
    logger.info("\n[bold][u]Use Case: print active conversations[/]", extra={"markup": True})
    logger.debug(f"Application ID: {app_id}")
    logger.debug(f"User ID: {user_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )
    for conversation in q_api_helper.list_conversations(app_id, user_id):
        logger.debug(pretty_repr(conversation))


def delete_all_conversation(app_id: str, user_id: str):
    """Delete all active conversations for a given user"""
    logger.info("\n[bold][u]Use Case: delete all conversations[/]", extra={"markup": True})
    logger.debug(f"Application ID: {app_id}")
    logger.debug(f"User ID: {user_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )
    result = q_api_helper.delete_conversations_by_age(app_id, user_id)
    logger.debug(f"All '{user_id}' conversations deleted: {result}")


def delete_conversation_by_age(app_id: str, user_id: str):
    """Delete all active conversations by age for a given user"""
    logger.info(
        "\n[bold][u]Use Case: simulate and delete conversations by age[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    logger.debug(f"User ID: {user_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )
    message = "who are you?"
    logger.debug(f"User Message:\n{message}")
    response = q_api_helper.chat_sync(message, app_id, user_id)
    logger.debug(f"System Message:\n{response.systemMessage}")
    logger.debug(f"Wait to simulate age: {WAIT_SECS_TO_SIMULATE_AGE} sec")
    time.sleep(WAIT_SECS_TO_SIMULATE_AGE)
    message = "What is the nearest star to solar system?"
    logger.debug(f"User Message:\n{message}")
    response = q_api_helper.chat_sync(message, app_id, user_id)
    logger.debug(f"System Message:\n{response.systemMessage}")
    age = timedelta(seconds=10)
    logger.debug(f"Delete messages older than: {age}")
    q_api_helper.delete_conversations_by_age(app_id, user_id, age)
    print_conversation_list(app_id, user_id)


def simple_qna(app_id: str, user_id: str, message: Optional[str] = None,
               verbose: bool = True):
    """Ask simple question and get answer"""
    if verbose:
        logger.info(
            "\n[bold][u]Use Case: simple question and answer[/]",
            extra={"markup": True}
        )
        logger.debug(f"Application ID: {app_id}")
        logger.debug(f"User ID: {user_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )
    message = message if message else "who are you?"
    logger.debug(f"User Message:\n{message}")
    response = q_api_helper.chat_sync(message, app_id, user_id)
    if verbose:
        logger.debug(pretty_repr(response))
    logger.debug(f"System Message:\n{response.systemMessage}")


def simple_conversation(app_id: str, user_id: str):
    """Have a conversation on a topic"""
    logger.info(
        "\n[bold][u]Use Case: have a conversation[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    logger.debug(f"User ID: {user_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )
    messages = [
        "who are you?",
        "How far is Earth from Mars?",
        "Summarize as an email to John Doe"
    ]
    conversation_id = None
    prev_sys_message_id = None
    for message in messages:
        logger.debug(f"User Message:\n{message}")
        response = q_api_helper.chat_sync(
            message, app_id, user_id,
            conversation_id, prev_sys_message_id
        )
        conversation_id = response.conversationId
        prev_sys_message_id = response.systemMessageId
        logger.debug(f"System Message:\n{response.systemMessage}")


def chat_with_file(app_id: str, user_id: str):
    """Have a private conversation on contents of a file with citations"""
    logger.info(
        "\n[bold][u]Use Case: chat with file with citations[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    logger.debug(f"User ID: {user_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )
    # Update path to use your own files
    files = [
        "resources/files/aws-repost_iam-users.md",
        "resources/files/aws-repost_securing-account.md"
    ]
    message = "Summarize the documents"
    logger.debug(f"User Message:\n{message}")
    response = q_api_helper.chat_sync(
        message, app_id, user_id,
        attach_files=files
    )
    logger.debug(f"System Message:\n{response.systemMessage}")
    messages = [
        # "How do I use IAM to allow user access to resources?",
        "What are some best practices for securing my AWS account and its resources?",
        "Summarize the best practices in an email to John Doe"
    ]
    for message in messages:
        conversation_id = response.conversationId
        prev_sys_message_id = response.systemMessageId
        logger.debug(f"User Message:\n{message}")
        response = q_api_helper.chat_sync(
            message, app_id, user_id,
            conversation_id, prev_sys_message_id
        )
        logger.debug(f"System Message:\n{response.systemMessage}")
        logger.debug(pretty_repr(_citations(response.sourceAttributions)))


def chat_with_ai_fallback_on_off(app_id: str, user_id: str):
    """Enable/disable ai knowledge fallback to see response"""
    logger.info(
        "\n[bold][u]Use Case: chat with ai knowledge fallback on/off[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    logger.debug(f"User ID: {user_id}")
    message = "How far is moon?"
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=REGION_NAME)
    )

    # Get current AI allowed state and creator mode
    ai_allowed = q_api_helper.is_ai_fallback_allowed(app_id)
    creator_allowed = q_api_helper.is_creator_mode_allowed(app_id)
    logger.debug(f"Current AI fallback mode state: {ai_allowed}")
    logger.debug(f"Current creator mode state: {creator_allowed}")

    logger.debug(f"Setting AI fallback mode and creator mode to {False}")
    q_api_helper.allow_ai_fallback(app_id, False)
    q_api_helper.allow_creator_mode(app_id, False)
    logger.debug(f"Wait for update: {WAIT_SECS_FOR_SETTING_UPDATE} sec")
    time.sleep(WAIT_SECS_FOR_SETTING_UPDATE)
    simple_qna(app_id=app_id, user_id=user_id, message=message, verbose=False)

    logger.debug(f"Setting AI fallback mode to {True}")
    q_api_helper.allow_ai_fallback(app_id, True)
    logger.debug(f"Wait for update: {WAIT_SECS_FOR_SETTING_UPDATE} sec")
    time.sleep(WAIT_SECS_FOR_SETTING_UPDATE)
    simple_qna(app_id=app_id, user_id=user_id, message=message, verbose=False)

    # Restore to original AI allowed state and creator mode
    logger.debug("Restoring AI fallback mode and creator mode to original")
    q_api_helper.allow_ai_fallback(app_id, ai_allowed)
    q_api_helper.allow_creator_mode(app_id, creator_allowed)
    logger.debug(f"Wait for update: {WAIT_SECS_FOR_SETTING_UPDATE} sec")
    time.sleep(WAIT_SECS_FOR_SETTING_UPDATE)
    ai_allowed = q_api_helper.is_ai_fallback_allowed(app_id)
    creator_allowed = q_api_helper.is_creator_mode_allowed(app_id)
    logger.debug(f"Restored AI fallback mode state: {ai_allowed}")
    logger.debug(f"Restored creator mode state: {creator_allowed}")


def main():
    """Demos Q Business API for chat. Uncomment use-cases as needed"""

    # ************************************************************
    # * Following use cases uses generic questions:              *
    # * TURN-ON admin setting to fallback to LLM world knowledge *
    # * - Uncomment USE CASES as needed                          *
    # * - Update Q Business application id and email for user id *
    # ************************************************************

    user_id = "tester1@anycompany.com"
    app_id = "0d9b62e4-a0d6-4782-9fa1-e27724e7f491"

    # print_conversation_list(app_id, user_id)

    # simple_qna(app_id, user_id)
    simple_qna(app_id, user_id, "Why use trusted identity propagation?")
    # simple_conversation(app_id, user_id)
    # chat_with_file(app_id, user_id)
    # chat_with_ai_fallback_on_off(app_id, user_id)

    # delete_conversation_by_age(app_id, user_id)
    delete_all_conversation(app_id, user_id)


if __name__ == "__main__":
    main()
