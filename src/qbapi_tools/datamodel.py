# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# pylint: disable=invalid-name

"""Amazon Q Business Expert API data models"""

from pathlib import Path
from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, computed_field


class ServiceConfig(BaseModel):
    """AWS service settings for boto3 client session"""
    service_name: Optional[str] = "qbusiness"
    region_name: Optional[str] = None


class DataSourceEnum(str, Enum):
    """Amazon Q Business Expert supported data sources"""
    s3 = 'S3'
    sharepoint = 'SHAREPOINT'
    database = 'DATABASE'
    salesforce = 'SALESFORCE'
    onedrive = 'ONEDRIVE'
    servicenow = 'SERVICENOW'
    custom = 'CUSTOM'
    confluence = 'CONFLUENCE'
    googledrive = 'GOOGLEDRIVE'
    webcrawler = 'WEBCRAWLER'
    workdocs = 'WORKDOCS'
    fsx = 'FSX'
    slack = 'SLACK'
    box = 'BOX'
    quip = 'QUIP'
    jira = 'JIRA'
    github = 'GITHUB'
    alfresco = 'ALFRESCO'


class AIScope(str, Enum):
    """AI Knowledge scope"""
    enterprise = "ENTERPRISE_CONTENT_ONLY"
    extended = "EXTENDED_KNOWLEDGE_ENABLED"


class ChatMode(str, Enum):
    """QBusiness Chat modes"""
    retrieval = "RETRIEVAL_MODE"
    creator = "CREATOR_MODE"
    plugin = "PLUGIN_MODE"


class Application(BaseModel):
    """List applications response item"""
    applicationId: str
    displayName: str
    createdAt: datetime
    updatedAt: datetime
    status: str


class ListApplicationsResponse(BaseModel):
    """List applications response object"""
    nextToken: Optional[str] = None
    applications: list[Application] = Field(default_factory=list)


class DataSource(BaseModel):
    """List data sources response item"""
    dataSourceId: str
    displayName: str
    createdAt: datetime
    updatedAt: datetime
    status: str
    type: str


class ListDataSourcesResponse(BaseModel):
    """List applications response object"""
    nextToken: Optional[str] = None
    dataSources: List[DataSource] = Field(default_factory=list)


class Index(BaseModel):
    """List indices response item"""
    indexId: str
    displayName: str
    createdAt: datetime
    updatedAt: datetime
    status: str


class ListIndicesResponse(BaseModel):
    """List indices response object"""
    nextToken: Optional[str] = None
    indices: List[Index] = Field(default_factory=list)


class DocumentIndexError(BaseModel):
    """Document indexing error"""
    errorCode: Optional[str] = None
    errorMessage: Optional[str] = None


class DocumentDetail(BaseModel):
    """Indexed document details"""
    documentId: str
    error: DocumentIndexError
    createdAt: datetime
    updatedAt: datetime
    status: str


class DocumentDetailsResponse(BaseModel):
    """List indexed document details object"""
    nextToken: Optional[str] = None
    documentDetailList: List[DocumentDetail] = Field(default_factory=list)


class CreatorModeConfiguration(BaseModel):
    """Configuration details for CREATOR_MODE"""
    creatorModeControl: str


class ChatControlConfigResponse(BaseModel):
    """chat controls configured information"""
    nextToken: Optional[str] = None
    responseScope: Optional[AIScope] = None
    creatorModeConfiguration: Optional[CreatorModeConfiguration] = None


class Conversation(BaseModel):
    """conversation detail"""
    conversationId: str
    title: str
    startTime: datetime


class ListConversationsResponse(BaseModel):
    """List of conversation response object"""
    nextToken: Optional[str] = None
    conversations: List[Conversation] = Field(default_factory=list)


class TextMessageSegment(BaseModel):
    """Source attribution text message segment"""
    beginOffset: int
    endOffset: int


class SourceAttribution(BaseModel):
    """Chat Sync source attribution"""
    citationNumber: int
    snippet: str
    title: str
    url: str
    textMessageSegments: List[TextMessageSegment] = Field(default_factory=list)
    updatedAt: Optional[datetime] = None


class ChatSyncResponse(BaseModel):
    """Chat Sync response base"""
    conversationId: str
    systemMessage: str
    systemMessageId: str
    userMessageId: str
    sourceAttributions: List[SourceAttribution] = Field(default_factory=list)


class ChatAttachment(BaseModel):
    """Chat file attachment"""
    filename: str

    @computed_field
    def name(self) -> str:
        """Returns the name of the file from path"""
        file_path = Path(self.filename)
        if file_path.exists() and file_path.is_file():
            return file_path.name
        raise FileNotFoundError(file_path.absolute())

    @computed_field
    def data(self) -> bytes:
        """Retrieves file content as binary data"""
        file_path = Path(self.filename)
        if file_path.exists() and file_path.is_file():
            return file_path.read_bytes()
        raise FileNotFoundError(file_path.absolute())
