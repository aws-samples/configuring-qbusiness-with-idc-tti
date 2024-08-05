# Amazon Q Business API Tools

This project aims to provide sample [Amazon Q Business](https://console.aws.amazon.com/amazonq/home) API code to help getting started with simple tasks such as list applications, indexes and conversations, and running simple chat commands. The sample also covers using Trusted Token Issuer (TTI) to implement identity-aware SigV4 signed Q Business APIs.

For more information see AWS blog [https://aws.amazon.com/blogs/machine-learning/configuring-amazon-q-business-with-aws-iam-identity-center-trusted-identity-propagation/](https://aws.amazon.com/blogs/machine-learning/configuring-amazon-q-business-with-aws-iam-identity-center-trusted-identity-propagation/)

![Trusted Token Issuer Architecture](/docs/images/q-api-tte-arch.png)

## Where to begin
This repository can be leveraged in multiple ways.

1. Checkout **end-to-end tutorials**, if you want to learn how to use identity-aware API with Identity Center and your OIDC identity provider (Okta, Microsoft Entra).
    * Microsoft Entra tutorial: [Configuring sample web application with Microsoft Entra](./docs/tutorials/entra/config-webapp-using-entra.md)
    * Okta tutorial: [Configuring sample web application with Okta](./docs/tutorials/okta/config-webapp-using-okta.md)

2. Explore included [CloudFormation templates](./cf/README.md), if you are looking to automate configuring TTI in your Identity Center Instance.

3. Try included Python [info.py](./samples/info.py) sample to learn how to use Q Business APIs for common admin tasks such as list applications, indexed files, etc.

4. Try included Python [chat.py](./samples/info.py) sample to learn how to use Q Business `legacy` Chat APIs for tasks such as listing conversations, delete conversations, chat, etc.

Remember to follow steps in `Repository Setup` section below to install required Python libraries.

## Project Files Overview
This code samples is organized into following sections.

### 1/ CloudFormation Templates for TTI and Cognito
Sample CloudFormation (CFN) templates are located in `<project_home>/cf` folder. You can use the CFN templates to automate deployment of Trusted Token Issuer (TTI) setup in AWS IAM Identity Center. Also a sample CFN template is provided to create Amazon Cognito user pool, if you do not have an OIDC OAuth 2.0 compliant 3rd party Identity Provider to test TTI deployment.

For more information refer to [CFN README](/cf/README.md).

> Note: You can use CloudFormation Templates without installing the project files.

### 2/ WebApp for testing TTI and Invoking Q Business Conversation API with identity context
The sample Flask based web application demonstrates how identity propagation with AWS IAM Identity Center can be implemented and is made available for learning and testing Trust Token Issuer deployment. The web application is located under `<project_home>/webapp`.

For more information refer to [WEBAPP README](/webapp/README.md).

### 3/ Samples for Application Info and for SAML based Conversation API
Samples files to demonstrate several use cases to retrieve Q Business application information and to use conversation API fos Q Business Applications using SAML 2.0 instead of AWS IAM Identity Center are located under `<project_home>/samples`.

For more information refer to [SAMPLES README](/samples/README.md).

### 4/ Q Business API Helpers
Various Amazon Q Business API helper methods are located under `<project_home>/src/qbapi_tools` folder. Pydantic based data models makes it easy to de-serialize API responses in JSON. The helper utilities, helps parsing multi-page results and use Python generators for iterating objects improving efficiency of system resource utilization. To get started, review the code samples under `<project_home>/webapp` and `<project_home>/samples` to learn how to use Amazon Q Business API helper utilities for common use cases.

### 5/ Tutorials and guides
Compilation of tutorials and guides to help with using Amazon Q Business identity-aware APIs are available under `<project_home>/docs`.

For more information refer to [DOCS README](/docs/README.md).

## Prerequisites
* An [AWS Account](https://signin.aws.amazon.com/signin?redirect_uri=https%3A%2F%2Fportal.aws.amazon.com%2Fbilling%2Fsignup%2Fresume&client_id=signup)
* Access to [Amazon Q Business](https://console.aws.amazon.com/amazonq/home).
* Access to [AWS IAM Identity Center](https://aws.amazon.com/iam/identity-center/) in the same AWS region as Amazon Q Business.
* An Amazon Q Business application created with data indexed for use with sample code.
* OpenID Connect (OIDC) compliant Identity Provider (IdP) for testing Trusted Token Issuer setup. See [WEBAPP README](/webapp/README.md) for instructions on setting up IdP. Examples: Okta, Amazon Cognito, Microsoft Entra ID, Ping Identity, etc.
* Requires Python 3.11 or above.
* [Poetry](https://python-poetry.org/) for Python library dependency management.

## Repository Setup
To execute the sample code, you will need to prepare your local development environment. The following steps will guide you through how to install required supporting libraries using Poetry.

> Note: The included sample CloudFormation templates are standalone component and can be deployed directly in your AWS Account without needing to install supporting libraries.

* Clone this project repository to your local development environment.
* Ensure the terminal is configured to access AWS APIs (https://docs.aws.amazon.com/cli/latest/userguide/cli-chap-configure.html)
* In the terminal change directory to root folder of the local cloned copy of the project
* Optionally, Poetry can be configured to create Python virtual environment (venv) locally in the project folder: `poetry config virtualenvs.in-project true`
* Install required python modules: `poetry install`
* Review [WEBAPP README](/webapp/README.md) and [SAMPLES README](/samples/README.md) for any additional configurations required. 
* Use Poetry to run sample codes:
    * For Q Business application info: `poetry run python samples/info.py`
    * For Chat SAML based application: `poetry run python samples/chat.py`
    * For IDC TTI WebApp based application: `poetry run python webapp/main.py`

## Logging
This project uses Rich Python library for logging messages with *rich text*. For more information visit: https://rich.readthedocs.io/en/stable/logging.html

## Poetry quick reference
This project uses Poetry for managing Python library dependency. Listed below are some useful poetry commands to get started. For more information visit: https://python-poetry.org/docs/basic-usage/

```shell
# To create python virtual environment (.venv) within the project folder
poetry config virtualenvs.in-project true

# List python virtual environments
poetry env info --path

# Install library dependencies (first time or when pyproject.toml is manually updated)
poetry install

# Add Python library dependency (will install library and add to project dependency)
poetry add boto3
poetry add --dev pylint

# Remove Python library dependency (will uninstall library and remove from project dependency)
poetry remove flask

# Run python program within poetry virtual environment
poetry run python samples/info.py
poetry run python webapp/main.py
poetry run python samples/chat.py

# Alternatively, run python program from poetry shell (activate virtual environment)
poetry shell
python samples/info.py
python webapp/main.py
```
