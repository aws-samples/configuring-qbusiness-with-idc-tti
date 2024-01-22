# Tutorial: Configuring sample web application with Okta

This tutorial will provide step-by-step instructions to deploy the sample
web application with Okta as external identity provider.

## 1/ Initial setup
1. Enable AWS IAM Identity Center instance (IDC).
    * Add sample users to IDC.
    * From the IDC settings note the `IDC Instance ARN`.
2. Create/Register a web application provider in Okta.
    * Register for Okta trial account if you do not already have an Okta account.
    * Follow the steps listed at [Create an OIDC Web App in the Okta Admin Console](https://support.okta.com/help/s/article/create-an-oidc-web-app-in-dashboard?language=en_US) to register your application.
    * Add same sample users to Okta as added to IDC is Step-1.
    * Ensure the user email address in Okta matches IDC, including case.
    * **Callback URL:** `http://localhost:8080/authorization-code/callback`
    * **Logout URL:** `http://localhost:8080/logout`
    * **Default Okta Issuer URL:** `https://${okta_domain}/oauth2/default`
    * Note `Client ID`, `Client Secret`, `Audience ID`, and `Issuer URL`
3. Create Amazon Q Business integrating with IDC instance above and use `File Upload` or `S3` connector to index few sample files for query.
    * Try the built-in Amazon Q Business web experience and try asking information from indexed documents.
    * From the application details page note the `Application ID`
4. Clone this repo and setup the application environment using poetry.
    * Use your local development desktop. Okta must be able to call the sample web applications `Callback URL` running on `localhost:8080` from public network.
    * You will need AWS CLI, Python and Poetry is installed.
    * [Configure the AWS CLI](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html) for your environment and ensure you are able to run AWS CLI commands from command line/terminal.
    * Note the AWS `IAM User/Role ARN` that is used to execute AWS CLI commands above. The sample web application will use the same IAM User/Role.

## 2/ Deploying Trusted token issuer (TTI)
Use `<project_home>/cf/qb-api-idc-config.yaml` to configure TTI. For the template parameters:
* **IDCInstanceArn:** Use the `IDC instance ARN` from step-1 in initial setup above.
* **ClientAppExecutionArn:** Use the AWS `IAM User/Role ARN` from step-4 in initial setup above.
* **TokenIssuerUrl:** Use the Okta `Issuer URL` from step-2 in initial setup above.
* **AuthorizedAudiences:** Use the Okta `Audience ID` from step-2 in initial setup above.

Note the `IDC Application ARN` output of the stack creation step.

## 3/ Deploying IAM Roles required by sample web application
Use `<project_home>/cf/qb-api-idc-config.yaml` to configure IAM Roles and Policies required by web application. For the template parameters:
* **QBApplicationID:** Use the Amazon Q Business `Application ID` from step-3 in initial setup above.
* **IDCApiAppArn:** Use the `IDC Application ARN` output by Deploying Trusted token issuer (TTI) CFN.
* **ClientAppExecutionArn:** Use the AWS `IAM User/Role ARN` from step-4 in initial setup above.
* **KMSKeyId:** This is Optional. Leave the default value if the default AWS managed encryption key is used.

Note the `STS Assume Role` and `App Policy Add-On` output of the stack creation step.

> **_IMPORTANT:_** If your are using a non-admin `IAM User/Role` for executing web application, attach the `App Policy Add-On` to the `IAM User/Role` to enable access to `CreateTokenWithIAM` and `AssumeRole` API for your `IAM User/Role`.

## 4/ Configuring Web Application Environment
Make a copy of `<project_home>/webapp/config/.env.okta.dist` file and rename it to `<project_home>/webapp/config/.env`. Update the environment variables as described below.

#### OAuth client configuration
* **issuer_url:** Use the Okta `Issuer URL` from step-2 in initial setup above.
* **client_id:** Use the Okta `Client ID` from step-2 in initial setup above.
* **client_secret:** Use the Okta `Client Secret` from step-2 in initial setup above.

#### Application configuration
* **idc_provider_apl_arn:** Use the `IDC Application ARN` output by CFN for Deploying Trusted token issuer (TTI).
* **qb_sts_role:** Use the `IDC Application ARN` output by CFN for  Deploying IAM Roles required by sample web application CFN.
* **qb_apl_id:** Use the Amazon Q Business `Application ID` from step-3 in initial setup above.
* **app_domain:**  Use `localhost:8080`.
* **region_name:** Use the AWS Region where your Q Business application and IDC is deployed. Example, `us-east-1` or `us-west-2`.

## 5/ Launching sample web application
* From your command line interface change folder to `<project_home>`
* Ensure your AWS CLI access is configured with `IAM User/Role` from step-4 in initial setup above.
* Ensure AWS CLI is working properly by executing any CLI command. Example, `aws qbusiness list-applications`.
* Launch web application using command: `poetry run python webapp/main.py`
* Open web browser in `InCognito` or `InPrivate` mode and navigate to http://localhost:8080/
* Click on `Login` button to start the sign-in process with Okta.

If successful, you should be able to see a list of active conversations for the signed-in user.

> Review the debug messages in the command line for OIDC/IDC JWT tokens and any error messages to trouble shoot issues.

## 6/ Cleanup
* Delete the CFN stack for Deploying IAM Roles required by sample web application
* Delete the CFN stack for Deploying Trusted token issuer (TTI)
* Delete Amazon Q Business Application
* Delete IDC instance
* Delete web application from Okta
* Delete samples users created in Okta.
