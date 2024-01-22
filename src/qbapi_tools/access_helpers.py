# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# pylint: disable=logging-fstring-interpolation

"""Token exchange helper"""

import os
import random
import string
import logging
from typing import Optional

import boto3
import jwt
import requests
from rich.logging import RichHandler
from rich.pretty import pretty_repr
from pydantic import BaseModel

from qbapi_tools.exception import (
    AccessHelperException,
)

logger = logging.getLogger("qbapi_tools")
logger.addHandler(RichHandler(show_time=False, rich_tracebacks=False))
logger.setLevel(logging.getLevelName(os.environ.get('logging', 'DEBUG')))


class OidcData(BaseModel):
    """OIDC OAuth data"""
    id_token: Optional[str] = None
    access_token: Optional[str] = None
    jwt_email: Optional[str] = None
    jwt_sub: Optional[str] = None


def get_oidc_config(issuer_url: str, timeout: int = 10) -> dict:
    """Retrieve OIDC configuration using issuer url"""
    headers = {'Accept': 'application/json'}
    resp = requests.get(
        f"{issuer_url}/.well-known/openid-configuration",
        headers=headers,
        timeout=timeout
    )
    if resp.status_code != 200:
        raise AccessHelperException("Unable to retrieve OIDC Configuration")

    oidc_config = resp.json()
    endpoints = (
        "issuer",
        "authorization_endpoint",
        "token_endpoint",
        "userinfo_endpoint"
    )
    if not all(k in oidc_config for k in endpoints):
        raise AccessHelperException(" OIDC Configuration missing OAuth endpoints")
    return oidc_config


def get_oidc_id_token(base_url: str, code: str, token_uri: str, client_id: str,
                      client_secret: str, timeout: int = 120) -> OidcData:
    """Obtain OIDC access and identity token"""
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    query_params = {
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': base_url
    }
    exchange = requests.post(
        token_uri,
        headers=headers,
        data=requests.compat.urlencode(query_params),
        auth=(client_id, client_secret),
        timeout=timeout
    ).json()
    logger.debug(f"Get token response:\n{pretty_repr(exchange)}")

    id_token = exchange.get("id_token")
    if not id_token:
        raise AccessHelperException("Missing OIDC identity token.")
    oidc_id_jwt = jwt.decode(
        id_token,
        algorithms=["RS256"],
        options={"verify_signature": False}
    )
    logger.info(f"OIDC identity token:\n{pretty_repr(oidc_id_jwt)}")

    token_type = exchange.get("token_type", "")
    if not token_type:
        raise AccessHelperException("Missing OIDC token type.")
    if token_type.lower() != "bearer":
        raise AccessHelperException(
            f"OIDC token type must be 'Bearer'. Found '{token_type}'."
        )

    access_token = exchange.get("access_token")
    if not access_token:
        raise AccessHelperException("Missing OIDC access token.")

    return OidcData(
        id_token=id_token,
        access_token=access_token,
        jwt_sub=oidc_id_jwt.get("sub"),
        jwt_email=oidc_id_jwt.get("email"),
    )


def get_oidc_user_info(userinfo_uri: str, access_token: str,
                       timeout: int = 120) -> tuple[str, str, str]:
    """Retrieve user info from identity provider (IdP)"""
    headers = {'Authorization': f'Bearer {access_token}'}
    userinfo_response = requests.get(
        userinfo_uri,
        headers=headers,
        timeout=timeout
    ).json()
    logger.info(f"OIDC user info:\n{pretty_repr(userinfo_response)}")

    unique_id = userinfo_response.get("sub")
    user_email = userinfo_response.get("email", "")
    user_name = userinfo_response.get("given_name", "")
    if not unique_id:
        raise AccessHelperException("Missing OIDC user info.")
    return (unique_id, user_email, user_name)


def get_idc_sts_id_context(idc_app_auth_provider_arn: str, id_token: str,
                           region_name: str) -> str:
    """Exchanges OIDC ID token with IDC provide app to get STS id context"""
    sso_oidc_client = boto3.client('sso-oidc', region_name=region_name)
    try:
        idc_sso_resp = sso_oidc_client.create_token_with_iam(
            clientId=idc_app_auth_provider_arn,
            grantType="urn:ietf:params:oauth:grant-type:jwt-bearer",
            # scope=["sts:identity_context"],
            # scope=["openid", "sts:identity_context", 'aws'],
            assertion=id_token,
        )
        logger.info(f"IDC create token response:\n{pretty_repr(idc_sso_resp)}")
        idc_id_jwt = jwt.decode(
            idc_sso_resp["idToken"],
            algorithms=["RS256"],
            options={"verify_signature": False}
        )
        logger.info(f"IDC IAM token:\n{pretty_repr(idc_id_jwt)}")
        return idc_id_jwt["sts:identity_context"]
    except sso_oidc_client.exceptions.InvalidGrantException as ex:
        err_msg = (
            "CreateTokenWithIAM failed with invalid grant exception. "
            "Check if 1/ identity token is reused, 2/ IDC is missing TTI configuration, "
            "or 3/ user's primary email in IAM identity center matches the email address of user "
            "signing-in via external identity provider."
        )
        raise AccessHelperException(err_msg) from ex


def get_sts_credential(idc_assume_role_arn: str, sts_context: str,
                       region_name: str) -> dict:
    """Assumes IDC ID based role and generates aws credentials"""
    sts_client = boto3.client('sts', region_name=region_name)
    # Random hash used of unique session name. collisions are fine.
    session_name = "qbusiness-idc-" + "".join(
        random.choices(string.ascii_letters + string.digits, k=32)  # nosec
    )
    assumed_role_object = sts_client.assume_role(
        RoleArn=idc_assume_role_arn,
        RoleSessionName=session_name,
        ProvidedContexts=[{
            "ProviderArn": "arn:aws:iam::aws:contextProvider/IdentityCenter",
            "ContextAssertion": sts_context
        }]
    )
    credential = assumed_role_object.get('Credentials')
    if not credential:
        raise AccessHelperException("Unable to obtain STS temporary credential.")
    return credential
