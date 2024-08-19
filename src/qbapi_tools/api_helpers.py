# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# pylint: disable=invalid-name,not-an-iterable,too-many-arguments.logging-fstring-interpolation

"""Amazon Q Business Expert API helpers to parse responses and paginate"""

import os
import random
import string
import logging
from typing import Any, List, Iterator, Optional
from datetime import datetime, timedelta
from dateutil import tz

import boto3
from rich.logging import RichHandler
from qbapi_tools.datamodel import (
    ServiceConfig, DataSourceEnum,
    Application, ListApplicationsResponse,
    Index, ListIndicesResponse,
    DataSource, ListDataSourcesResponse,
    DocumentDetail, DocumentDetailsResponse,
    ListConversationsResponse, Conversation,
    AIScope, ChatMode, ChatControlConfigResponse,
    ChatSyncResponse, ChatAttachment,
    CreateDataSourceResponse, StartDataSourceSyncJobResponse,
    GetUserResponse
)
from qbapi_tools.exception import (
    ChatAIResponseScopeNotFound,
    ChatSyncConversationMissingParameters
)

logger = logging.getLogger("qbapi_tools")
logger.addHandler(RichHandler(show_time=False, rich_tracebacks=False))
logger.setLevel(logging.getLevelName(os.environ.get('logging', 'DEBUG')))

MSG_MISSING_USER_ID = "'user_id' parameter is required, if not using identity propagation credentials."
MSG_MISSING_CONV_SYSMSG_ID = "Both conversation ID and previous system message ID are required."
MSG_MISSING_AI_CHAT_SCOPE = "AI chat response scope setting not found."


class QBusinessAPIHelpers:
    """Q Business API helper methods"""
    def __init__(self, service_config: ServiceConfig, credentials=None) -> None:
        self.service_config = service_config
        self.credentials = credentials
        self._client = self._get_client()

    def _get_client(self) -> Any:
        if self.credentials:
            assumed_session = boto3.Session(
                aws_access_key_id=self.credentials['AccessKeyId'],
                aws_secret_access_key=self.credentials['SecretAccessKey'],
                aws_session_token=self.credentials['SessionToken']
            )
            return assumed_session.client(**self.service_config.model_dump())
        return boto3.client(**self.service_config.model_dump())

    def _get_client_token(self) -> str:
        return "".join(random.choices(
            string.ascii_letters + string.digits,
            k=32
        ))  # nosec

    def list_applications(self) -> Iterator[Application]:
        """Iterate applications"""
        paginator = self._client.get_paginator('list_applications')
        page_iterator = paginator.paginate()
        for page in page_iterator:
            list_apps_resp: ListApplicationsResponse = ListApplicationsResponse(
                **page
            )
            for app in list_apps_resp.applications:
                yield app

    def list_indices(self, app_id: str) -> Iterator[Index]:
        """Iterate indices for a given application"""
        paginator = self._client.get_paginator('list_indices')
        page_iterator = paginator.paginate(applicationId=app_id)
        for page in page_iterator:
            list_indices_resp: ListIndicesResponse = ListIndicesResponse(
                **page
            )
            for idx in list_indices_resp.indices:
                yield idx

    def list_data_sources(
            self,
            app_id: str,
            index_id: str) -> Iterator[DataSource]:
        """Iterate data sources for a given application and index"""
        paginator = self._client.get_paginator('list_data_sources')
        page_iterator = paginator.paginate(
            applicationId=app_id,
            indexId=index_id
        )
        for page in page_iterator:
            list_ds_resp: ListDataSourcesResponse = ListDataSourcesResponse(
                **page
            )
            for ds in list_ds_resp.dataSources:
                yield ds

    def list_documents(
            self,
            app_id: str,
            index_id: str,
            ds_id_list: List[str]) -> Iterator[DocumentDetail]:
        """Iterate documents for a given application,
        index and list of data sources"""
        for ds_id in ds_id_list:
            paginator = self._client.get_paginator('list_documents')
            page_iterator = paginator.paginate(
                applicationId=app_id,
                indexId=index_id,
                dataSourceIds=[ds_id]  # API accepts list of size 1 only
            )
            for page in page_iterator:
                list_docs_resp: DocumentDetailsResponse = DocumentDetailsResponse(
                    **page
                )
                for docs in list_docs_resp.documentDetailList:
                    yield docs

    def list_documents_by_datasource_type(
            self,
            app_id: str,
            ds_type: Optional[DataSourceEnum] = None) -> Iterator[DocumentDetail]:
        """Iterate documents for a given application and optional
        datasource type (eg. CONFLUENCE)"""
        idx_iter = self.list_indices(app_id=app_id)
        for idx in idx_iter:
            ds_iter = self.list_data_sources(
                app_id=app_id,
                index_id=idx.indexId
            )
            ds_ids = []
            if not ds_type:
                ds_ids = list(map(lambda ds: ds.dataSourceId, ds_iter))
            else:
                ds_ids = list(
                    map(
                        lambda ds: ds.dataSourceId,
                        filter(lambda ds: ds.type==ds_type, ds_iter)  # noqa: E225
                    )
                )
            docs_iter = self.list_documents(
                app_id=app_id,
                index_id=idx.indexId,
                ds_id_list=ds_ids
            )
            for doc in docs_iter:
                yield doc

    def allow_ai_fallback(self, app_id: str, allow: bool = True) -> None:
        """Enable/disable fallback to AI to use its knowledge to answer questions"""
        scope = AIScope.extended if allow else AIScope.enterprise
        self._client.update_chat_controls_configuration(
            applicationId=app_id,
            responseScope=scope,
            clientToken=self._get_client_token()
        )

    def is_ai_fallback_allowed(self, app_id: str) -> bool:
        """Find if allowed to fallback to AI knowledge to answer questions"""
        paginator = self._client.get_paginator('get_chat_controls_configuration')
        page_iterator = paginator.paginate(applicationId=app_id)
        for page in page_iterator:
            chat_conf_resp: ChatControlConfigResponse = ChatControlConfigResponse(
                **page
            )
            if chat_conf_resp.responseScope:
                return chat_conf_resp.responseScope == AIScope.extended
        raise ChatAIResponseScopeNotFound(MSG_MISSING_AI_CHAT_SCOPE)

    def allow_creator_mode(self, app_id: str, allow: bool = True) -> None:
        """Enable/disable direct LLM access for creators"""
        scope = 'ENABLED' if allow else 'DISABLED'
        self._client.update_chat_controls_configuration(
            applicationId=app_id,
            creatorModeConfiguration={'creatorModeControl': scope},
            clientToken=self._get_client_token()
        )

    def is_creator_mode_allowed(self, app_id: str) -> bool:
        """Find if direct LLM access for creators is enabled"""
        paginator = self._client.get_paginator('get_chat_controls_configuration')
        page_iterator = paginator.paginate(applicationId=app_id)
        for page in page_iterator:
            chat_conf_resp: ChatControlConfigResponse = ChatControlConfigResponse(
                **page
            )
            if chat_conf_resp.creatorModeConfiguration:
                return chat_conf_resp.creatorModeConfiguration.creatorModeControl == "ENABLED"
        logger.warning("Creator mode configuration not found.")
        return False

    def create_custom_ds(self, app_id: str, index_id: str, name: str) -> CreateDataSourceResponse:
        """Creates custom data source"""
        ds_create_resp = self._client.create_data_source(
            applicationId=app_id,
            indexId=index_id,
            displayName=name,
            configuration={"type": DataSourceEnum.custom, "version": "1.0.0"}
        )
        return CreateDataSourceResponse(**ds_create_resp)

    def delete_ds(self, app_id: str, index_id: str, ds_id: str) -> None:
        """Deletes a data source"""
        self._client.delete_data_source(
            applicationId=app_id,
            indexId=index_id,
            dataSourceId=ds_id
        )

    def start_ds_sync_job(self, app_id: str, index_id: str, ds_id: str) -> StartDataSourceSyncJobResponse:
        """Start data source sync job"""
        ds_start_sync_resp = self._client.start_data_source_sync_job(
            applicationId=app_id,
            indexId=index_id,
            dataSourceId=ds_id
        )
        return StartDataSourceSyncJobResponse(**ds_start_sync_resp)

    def stop_ds_sync_job(self, app_id: str, index_id: str, ds_id: str) -> None:
        """Stop data source sync job"""
        self._client.stop_data_source_sync_job(
            applicationId=app_id,
            indexId=index_id,
            dataSourceId=ds_id
        )

    def put_documents(self, app_id: str, index_id: str, sync_id: str, documents: dict):
        """Puts documents to custom data source"""
        put_docs_resp = self._client.batch_put_document(
            applicationId=app_id,
            indexId=index_id,
            dataSourceSyncId=sync_id,
            documents=documents
        )
        return put_docs_resp

    def add_user_alias(
            self, email: str, alias: str, app_id: str,
            index_id: str, ds_id: str) -> dict:
        """Creates user and/or update user alias"""
        get_user_resp = None
        alias_list = []
        try:
            get_user_resp = GetUserResponse(**self._client.get_user(
                applicationId=app_id,
                userId=email
            ))
            logger.debug(get_user_resp)
        except self._client.exceptions.ResourceNotFoundException:
            logger.warning(f"User '{email}' not found. Will create.")

        if get_user_resp:
            # Check if alias exists and skip
            alias_list = list(filter(
                lambda x: (x.indexId == index_id
                           and x.dataSourceId == ds_id
                           and x.userId == alias),
                get_user_resp.userAliases
            ))
        else:
            # Create user/alias
            logger.info(f"Creating user '{email}' / alias '{alias}'")
            resp = self._client.create_user(
                applicationId=app_id,
                userId=email,
                userAliases=[
                    {
                        'indexId': index_id,
                        'dataSourceId': ds_id,
                        'userId': alias
                    },
                ],
                clientToken=self._get_client_token()
            )
            return resp

        if len(alias_list) <= 0:
            # Update user/alias
            logger.info(f"Updating user '{email}' / alias '{alias}'")
            resp = self._client.update_user(
                applicationId=app_id,
                userId=email,
                userAliasesToUpdate=[
                    {
                        'indexId': index_id,
                        'dataSourceId': ds_id,
                        'userId': alias
                    },
                ]
            )
            return resp

        # No action: user and alias exist
        return {}

    def list_conversations(self, app_id: str,
                           user_id: Optional[str] = None) -> Iterator[Conversation]:
        """Iterate conversations for a given application and user"""
        params = {
            "applicationId": app_id
        }
        if not user_id and not self.credentials:
            raise ChatSyncConversationMissingParameters(MSG_MISSING_USER_ID)
        if user_id and not self.credentials:
            params["userId"] = user_id
        paginator = self._client.get_paginator('list_conversations')
        page_iterator = paginator.paginate(**params)
        for page in page_iterator:
            list_conv_resp: ListConversationsResponse = ListConversationsResponse(
                **page
            )
            for conversation in list_conv_resp.conversations:
                yield conversation

    def delete_conversation(
            self, conversation_id: str, app_id: str, user_id: Optional[str] = None) -> bool:
        """Delete a conversation"""
        params = {
            "applicationId": app_id,
            "conversationId": conversation_id
        }
        if not user_id and not self.credentials:
            raise ChatSyncConversationMissingParameters(MSG_MISSING_USER_ID)
        if user_id and not self.credentials:
            params["userId"] = user_id
        try:
            self._client.delete_conversation(**params)
            return True
        except Exception as ex:  # pylint: disable=broad-exception-caught
            logger.exception(ex.args[0])
        return False

    def delete_conversations_by_age(
            self, app_id: str, user_id: Optional[str] = None,
            age: Optional[timedelta] = None) -> bool:
        """Delete conversations by age"""
        age = age if age else timedelta(seconds=0)
        # tzlocal used for consistency with conversation.startTime
        expiry_cutoff = datetime.now(tz.tzlocal()) - age
        for conversation in self.list_conversations(app_id, user_id):
            expired = conversation.startTime <= expiry_cutoff
            if expired:
                if not self.delete_conversation(
                    conversation_id=conversation.conversationId,
                    app_id=app_id,
                    user_id=user_id
                ):
                    return False
        return True

    def chat_sync_ttp(
            self, message: str, app_id: str,
            conversation_id: Optional[str] = None,
            prev_sys_message_id: Optional[str] = None,
            attach_files: Optional[List[str]] = None,
            chat_mode: str = ChatMode.retrieval) -> ChatSyncResponse:
        """Facilitate call sync chat API with identity propagation. No user ID."""
        return self.chat_sync(
            message=message,
            app_id=app_id,
            conversation_id=conversation_id,
            prev_sys_message_id=prev_sys_message_id,
            attach_files=attach_files,
            chat_mode=chat_mode
        )

    def chat_sync(
            self, message: str, app_id: str,
            user_id: Optional[str] = None,
            conversation_id: Optional[str] = None,
            prev_sys_message_id: Optional[str] = None,
            attach_files: Optional[List[str]] = None,
            chat_mode: str = ChatMode.retrieval) -> ChatSyncResponse:
        """Facilitate call sync chat API"""
        chat_params = {
            "applicationId": app_id,
            "clientToken": self._get_client_token(),
            "userMessage": message,
            "chatMode": chat_mode
        }
        if not user_id and not self.credentials:
            raise ChatSyncConversationMissingParameters(MSG_MISSING_USER_ID)
        if user_id and not self.credentials:
            chat_params["userId"] = user_id
        if conversation_id and prev_sys_message_id:
            chat_params["conversationId"] = conversation_id
            chat_params["parentMessageId"] = prev_sys_message_id
        elif conversation_id or prev_sys_message_id:
            raise ChatSyncConversationMissingParameters(MSG_MISSING_CONV_SYSMSG_ID)
        if attach_files:
            attachments = [
                ChatAttachment(filename=file).model_dump(exclude={'filename'})
                for file in attach_files
            ]
            # ic(list(map(lambda x: x['name'], attachments)))
            chat_params["attachments"] = attachments
        resp = self._client.chat_sync(**chat_params)
        return ChatSyncResponse(**resp)
