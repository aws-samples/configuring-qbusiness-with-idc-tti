# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# pylint: disable=logging-fstring-interpolation,broad-exception-caught

"""Sample Flask based web application to demonstrate authorization flow
--------------------------------------------------------------------
| STEP | METHOD        | DESCRIPTION                               |
|------|---------------|-------------------------------------------|
| 1    | login         | Sign-in and get authorization code        |
| 2    | callback      | Get OIDC identity and access token        |
| 3    | callback      | Get IDC STS context token                 |
| 4    | callback      | Get STS temporary credentials             |
| 5    | conversations | Use credentials call Q Business User APIs |
--------------------------------------------------------------------
"""

import os
import random
import string
import logging
import json
from pathlib import Path

import requests
from dotenv import dotenv_values
from rich.logging import RichHandler
from flask import Flask, render_template, redirect, request, url_for
from flask_login import (
    LoginManager,
    current_user,
    login_required,
    login_user,
    logout_user,
)

from user import User
from qbapi_tools.api_helpers import QBusinessAPIHelpers
from qbapi_tools.access_helpers import (
    get_oidc_config,
    get_oidc_id_token,
    get_idc_sts_id_context,
    get_sts_credential,
)
from qbapi_tools.exception import (
    AccessHelperException,
)
from qbapi_tools.datamodel import (
    ServiceConfig, ChatMode
)

logger = logging.getLogger("qbapi_demo")
logger.addHandler(RichHandler(show_time=False, rich_tracebacks=True))
logger.setLevel(logging.getLevelName(os.environ.get('logging', 'DEBUG')))

config = {
    **dotenv_values(dotenv_path=Path('./webapp/config/.env').absolute()),
    # **os.environ  # override loaded values with system env variables
}
oidc_config = get_oidc_config(config["issuer_url"])
region_name = config.get(
    "region_name",
    os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
)

app = Flask(__name__)

# Random hash is only used to generate unique values,
# collisions are acceptable and "data" is not
# coming from user-generated input
app.config.update({'SECRET_KEY': ''.join(random.choices(
    string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32
))})  # nosec
login_manager = LoginManager()
login_manager.init_app(app)

APP_STATE = 'ApplicationState'
# Random hash is only used to generate unique values,
# collisions are acceptable and "data" is not
# coming from user-generated input
NONCE = ('Sample' + ''.join(random.choices(
    string.ascii_uppercase + string.ascii_lowercase + string.digits, k=32
)))  # nosec


@login_manager.user_loader
def load_user(user_id):
    """user information loader"""
    return User.get(user_id)


@app.route("/")
def home():
    """Home page"""
    return render_template("home.html")


@app.route("/login")
def login():
    """Sign-on user with OAuth provider"""
    # ------------------------------------------------
    # | STEP (1): Sign-in and get authorization code |
    # ------------------------------------------------
    query_params = {
        'client_id': config["client_id"],
        'redirect_uri': f'http://{config["app_domain"]}/authorization-code/callback',
        'scope': "openid email profile",
        'state': APP_STATE,
        'nonce': NONCE,
        'response_type': 'code',
        'response_mode': 'query'
    }

    # build request_uri
    base_url = oidc_config["authorization_endpoint"]
    query_params = requests.compat.urlencode(query_params)
    request_uri = f"{base_url}?{query_params}"
    logger.debug(request_uri)
    return redirect(request_uri)


@app.route("/authorization-code/callback")
def callback():
    """Okta SSO callback url"""
    code = request.args.get("code")
    if not code:
        return "The authorization code was not returned or is not accessible", 403
    try:
        # ------------------------------------------------
        # | STEP (2): Get OIDC identity token            |
        # ------------------------------------------------
        odic_data = get_oidc_id_token(
            base_url=request.base_url,
            code=code,
            token_uri=oidc_config["token_endpoint"],
            client_id=config["client_id"],
            client_secret=config["client_secret"]
        )
        # ------------------------------------------------
        # | STEP (3): Get IDC STS context token          |
        # ------------------------------------------------
        idc_sts_context = get_idc_sts_id_context(
            config["idc_provider_apl_arn"],
            odic_data.id_token,
            region_name
        )
        # ------------------------------------------------
        # | STEP (4): Get STS temporary credential       |
        # ------------------------------------------------
        credential = get_sts_credential(
            config["qb_sts_role"], idc_sts_context,
            region_name
        )
        # Authorization flow successful
        # Cache user info and credentials in user store
        user = User.get(odic_data.jwt_sub)
        if not user:
            user = User.create(
                user_id=odic_data.jwt_sub,
                name=odic_data.jwt_email,
                email=odic_data.jwt_email,
                credential=credential
            )
        login_user(user)
        return redirect(url_for("chat"))
    except AccessHelperException as ex:
        logger.exception(ex.args[0])
        return ex.args[0], 403
    except Exception as ex:
        logger.exception(ex.args[0])
        return "Internal error", 500


@app.route("/chat", methods=['GET'])
@login_required
def chat():
    """Generate chat page"""
    return render_template(
        "chat.html",
        user=current_user
    )


@app.route('/answer', methods=['POST'])
@login_required
def get_answer():
    """Invoke Q Business Chat API to get answer"""
    answer = "Sorry, an error occurred while getting the answer."
    try:
        data = json.loads(request.data)
        if "question" not in data:
            logger.error("Missing user query.")
            return json.dumps({'systemMessage': answer})
        # ----------------------------------------------------------
        # | STEP (5): Use temp credentials to call Q Business APIs |
        # ----------------------------------------------------------
        q_api_helper = QBusinessAPIHelpers(
            service_config=ServiceConfig(region_name=region_name),
            credentials=current_user.credential,
        )
        chat_params = {
            "message": data['question'],
            "app_id": config["qb_apl_id"],
            "chat_mode": ChatMode.retrieval
        }
        if "conversationId" in data and "prevSysMessageId" in data:
            chat_params["conversation_id"] = data["conversationId"]
            chat_params["prev_sys_message_id"] = data["prevSysMessageId"]
        resp = q_api_helper.chat_sync_ttp(**chat_params).model_dump()
        logger.debug(resp)
        return json.dumps(resp)
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'systemMessage': answer})


@app.route("/conversations", methods=['GET'])
@login_required
def conversations():
    """Generate conversations page"""
    # ----------------------------------------------------------
    # | STEP (5): Use temp credentials to call Q Business APIs |
    # ----------------------------------------------------------
    q_api_helper = QBusinessAPIHelpers(
        service_config=ServiceConfig(region_name=region_name),
        credentials=current_user.credential
    )
    user_conversations = list(q_api_helper.list_conversations(config["qb_apl_id"]))
    logger.debug(user_conversations)
    return render_template(
        "conversations.html",
        user=current_user,
        conversations=user_conversations
    )


@app.route("/delete_chat", methods=['POST'])
@login_required
def delete_conversation():
    """Delete conversation"""
    status = "fail"
    # ----------------------------------------------------------
    # | STEP (5): Use temp credentials to call Q Business APIs |
    # ----------------------------------------------------------
    try:
        data = json.loads(request.data)
        if "conversationId" not in data or not data.get("conversationId"):
            logger.error("Missing conversation ID.")
            return json.dumps({'status': status})
        q_api_helper = QBusinessAPIHelpers(
            service_config=ServiceConfig(region_name=region_name),
            credentials=current_user.credential
        )
        resp = q_api_helper.delete_conversation(
            conversation_id=data["conversationId"],
            app_id=config["qb_apl_id"]
        )
        logger.debug(resp)
        status = "success"
    except Exception as ex:
        logger.error(ex)
    return json.dumps({'status': status})


@app.route("/profile", methods=['GET'])
@login_required
def profile():
    """Generate profile page"""
    return render_template("profile.html", user=current_user)


@app.route("/logout", methods=["GET", "POST"])
@login_required
def logout():
    """Sign-out user"""
    User.delete(current_user)
    logout_user()
    return redirect(url_for("home"))


if __name__ == '__main__':
    app.run(host="localhost", port=8080, debug=False)
