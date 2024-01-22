# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# pylint: disable=invalid-name,not-an-iterable,missing-function-docstring,logging-fstring-interpolation

"""Sample calls to Amazon Q Business Expert API helpers to retrieve application related info"""

import os
import logging

from rich.logging import RichHandler
from rich.pretty import pretty_repr
from qbapi_tools.api_helpers import QBusinessAPIHelpers
from qbapi_tools.datamodel import (
    ServiceConfig, DataSourceEnum,
)

logger = logging.getLogger("qbapi_samples")
logger.addHandler(RichHandler(
    show_time=False, show_path=False, show_level=False, rich_tracebacks=False
))
logger.setLevel(logging.getLevelName(os.environ.get('logging', 'DEBUG')))


def print_apps_info(region_name: str):
    """Print app info by iterating thru application objects"""
    logger.info(
        "\n[bold][u]Use Case: print active application details[/]",
        extra={"markup": True}
    )
    logger.debug(f"AWS Region: {region_name}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=region_name)
    )
    for app in q_api_helper.list_applications():
        logger.debug(pretty_repr(app))


def print_apps_info_as_list(region_name: str):
    """Prints list of application objects"""
    logger.info(
        "\n[bold][u]Use Case: print active applications info as list[/]",
        extra={"markup": True}
    )
    logger.debug(f"AWS Region: {region_name}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=region_name)
    )
    app_list = list(q_api_helper.list_applications())
    logger.debug(pretty_repr(app_list))


def print_index_ids_as_list_4_app(app_id: str):
    """Prints a list of index ids for a given app"""
    logger.info(
        "\n[bold][u]Use Case: print index IDs for an app as a list[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig()
    )
    idx_iter = q_api_helper.list_indices(
        app_id=app_id
    )
    idx_ids = list(map(lambda idx: idx.indexId, idx_iter))
    logger.debug(pretty_repr(idx_ids))


def print_all_ds_info_4_app(app_id: str):
    """Prints all data sources for an app"""
    logger.info(
        "\n[bold][u]Use Case: print all data sources for an app[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig()
    )
    idx_iter = q_api_helper.list_indices(
        app_id=app_id
    )
    for idx in idx_iter:
        logger.debug(f"Index ID: {idx.indexId}")
        ds_iter = q_api_helper.list_data_sources(
            app_id=app_id,
            index_id=idx.indexId
        )
        for ds_info in ds_iter:
            logger.debug(pretty_repr(ds_info))


def print_ds_id_list_by_ds_type_4_app(app_id: str, ds_type: DataSourceEnum):
    """Prints data source id list filtered by data source type for an app"""
    logger.info(
        "\n[bold][u]Use Case: print data source IDs as list filtered by data source type[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig()
    )
    idx_iter = q_api_helper.list_indices(
        app_id=app_id
    )
    for idx in idx_iter:
        logger.debug(f"Index ID: {idx.indexId}")
        ds_iter = q_api_helper.list_data_sources(
            app_id=app_id,
            index_id=idx.indexId
        )
        # Filer by DS Type, then map only datasource id and convert to list
        ds_ids = list(
            map(
                lambda ds: ds.dataSourceId,
                filter(lambda ds: ds.type==ds_type, ds_iter)  # noqa: E225
            )
        )
        logger.debug(pretty_repr(ds_ids))


def print_all_indexed_docs_4_app(app_id: str):
    """Prints all indexed documents for an app"""
    logger.info(
        "\n[bold][u]Use Case: print all indexed document info[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig()
    )
    docs_iter = q_api_helper.list_documents_by_datasource_type(
        app_id=app_id
    )
    for doc in docs_iter:
        logger.debug(pretty_repr(doc))


def print_indexed_docs_4_app_ds_type(app_id: str, ds_type: DataSourceEnum):
    """Prints all indexed documents filtered by data source type for an app"""
    logger.info(
        "\n[bold][u]Use Case: print all indexed document info by data source type[/]",
        extra={"markup": True}
    )
    logger.debug(f"Application ID: {app_id}")
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig()
    )
    docs_iter = q_api_helper.list_documents_by_datasource_type(
        app_id=app_id,
        ds_type=ds_type
    )
    for doc in docs_iter:
        logger.debug(pretty_repr(doc))


def main():
    """Demos Q Business API helper usage."""

    # *******************************************************
    # * Uncomment USE CASES as needed                       *
    # * Update Q Business region name and application id    *
    # *******************************************************
    region_name = "us-east-1"
    # app_id = "<qbusiness-application-id>"

    print_apps_info(region_name)
    # print_apps_info_as_list(region_name)

    # print_index_ids_as_list_4_app(app_id)
    # print_all_ds_info_4_app(app_id)

    # print_ds_id_list_by_ds_type_4_app(app_id, DataSourceEnum.s3)
    # print_ds_id_list_by_ds_type_4_app(app_id, DataSourceEnum.confluence)
    # print_ds_id_list_by_ds_type_4_app(app_id, DataSourceEnum.sharepoint)

    # print_all_indexed_docs_4_app(app_id)
    # print_indexed_docs_4_app_ds_type(app_id, DataSourceEnum.s3)
    # print_indexed_docs_4_app_ds_type(app_id, DataSourceEnum.confluence)
    # print_indexed_docs_4_app_ds_type(app_id, DataSourceEnum.sharepoint)


if __name__ == "__main__":
    main()
