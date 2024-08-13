# Tutorial: Configuring sample web application with Amazon Cognito

This tutorial will provide step-by-step instructions to deploy the sample
web application with Amazon Cognito (Cognito) as external identity provider.

## 1/ Initial setup
1. Create Cognito user pool and register you web application with Cognito.
    * Go to the [Amazon Cognito console](https://console.aws.amazon.com/cognito/home)
    * Follow the steps listed at [Register web application with Amazon Cognito](./register-webapp-with-cognito.md) to create an user pool, if required and register your sample web application with Cognito user pool.
    * Add same sample users to Cognito user pool as needed.
    * Ensure the user email address attribute is configured for the user.
    * **Callback URL:** `http://localhost:8080/authorization-code/callback`
    * **Logout URL:** `http://localhost:8080/logout`
    * Note `Client ID`, `Client Secret`, and `cognito_user_pool_id`
        * For Cognito, by default, `Audience ID` is same as `Client ID`
    * **Default Cognito Issuer URL Syntax:**  `https://cognito-idp.<aws_region>.amazonaws.com/<cognito_user_pool_id>`
        * Reference: [OAuth 2.0, OpenID Connect, and SAML 2.0 federation endpoints reference](https://docs.aws.amazon.com/cognito/latest/developerguide/federation-endpoints.html)
2. Enable AWS IAM Identity Center instance (Identity Center).
    * Add same sample users (email address) to Identity Center as added to Cognito is _Step 1_.
        * Ensure the user email address in Cognito matches Identity Center, including case.
    * **_Auto Sync Users:_** Cognito currently _does not support SCIM protocol_ to auto sync user attributes with Identity Center.
    * From the Identity Center settings, note the `IDC Instance ARN`.
3. Create Amazon Q Business application.
    * See [Creating a sample Amazon Q Business application](https://docs.aws.amazon.com/amazonq/latest/qbusiness-ug/quick-create-app.html) to create new Q Business application.
    * Ensure the Q Business application is configured to use the Identity Center instance created in _step 2_ above.
    * From the application details page note the Q Business `Application ID`
    * Use `File Upload` or `S3` connector to index few sample files for query.
    * Sign-in to the Amazon Q Business web experience as one of the sample user created in Identity Center and asking information from the sample indexed documents.
4. Clone this repo and setup the application environment using poetry.
    * Use your local development desktop. Cognito must be able to call the sample web applications `Callback URL` running on `localhost:8080` from public network.
    * You will need AWS CLI, Python and Poetry is installed.
    * [Configure the AWS CLI](https://docs.aws.amazon.com/cli/v1/userguide/cli-chap-configure.html) for your environment and ensure you are able to run AWS CLI commands from command line/terminal.
    * Note the AWS `IAM User/Role ARN` that is used to execute AWS CLI commands above. The sample web application will use the same IAM User/Role.

## 2/ Deploying Trusted token issuer (TTI)
Use `<project_home>/cf/qb-api-idc-config.yaml` to configure TTI. For the template parameters:
* **IDCInstanceArn:** Use the `IDC instance ARN` from _step 2_ in initial setup above.
* **ClientAppExecutionArn:** Use the AWS `IAM User/Role ARN` from _step 4_ in initial setup above.
* **TokenIssuerUrl:** Use the Cognito `Issuer URL` from _step 1_ in initial setup above.
* **AuthorizedAudiences:** Use the Cognito `Audience ID` from _step 1_ in initial setup above.

Note the `IDC Application ARN` output of the stack creation step.

## 3/ Deploying IAM Roles required by sample web application
Use `<project_home>/cf/qb-api-idc-config.yaml` to configure IAM Roles and Policies required by web application. For the template parameters:
* **QBApplicationID:** Use the Amazon Q Business `Application ID` from _step 3_ in initial setup above.
* **IDCApiAppArn:** Use the `IDC Application ARN` output by Deploying Trusted token issuer (TTI) CFN.
* **ClientAppExecutionArn:** Use the AWS `IAM User/Role ARN` from _step 4_ in initial setup above.
* **KMSKeyId:** This is Optional. Leave the default value if the default AWS managed encryption key is used.

Note the `STS Assume Role` and `App Policy Add-On` output of the stack creation step.

> **_IMPORTANT:_** If your are using a non-admin `IAM User/Role` for executing web application, attach the `App Policy Add-On` to the `IAM User/Role` to enable access to `CreateTokenWithIAM` and `AssumeRole` API for your `IAM User/Role`.

## 4/ Configuring Web Application Environment
Make a copy of `<project_home>/webapp/config/.env.cognito.dist` file and rename it to `<project_home>/webapp/config/.env`. Update the environment variables as described below.

#### OAuth client configuration
* **issuer_url:** Use the Cognito `Issuer URL` from _step 1_ in initial setup above.
* **client_id:** Use the Cognito `Client ID` from _step 1_ in initial setup above.
* **client_secret:** Use the Cognito `Client Secret` from _step 1_ in initial setup above.

#### Application configuration
* **idc_provider_apl_arn:** Use the `IDC Application ARN` output by CFN for Deploying Trusted token issuer (TTI).
* **qb_sts_role:** Use the `STS Assume Role` output by CFN for Deploying IAM Roles required by sample web application CFN.
* **qb_apl_id:** Use the Amazon Q Business `Application ID` from _step 3_ in initial setup above.
* **app_domain:**  Use `localhost:8080`.
* **region_name:** Use the AWS Region where your Q Business application and Identity Center is deployed. Example, `us-east-1` or `us-west-2`.

## 5/ Launching sample web application
* From your command line interface change folder to `<project_home>`
* Install project libraries using Poetry. See `Repository Setup` section in [Project README](../../../README.md) for more information.
* Ensure your AWS CLI access is configured with `IAM User/Role` from _step 4_ in initial setup above.
* Ensure AWS CLI is working properly by executing any CLI command. Example, `aws qbusiness list-applications`.
* Launch web application using command: `poetry run python webapp/main.py`
* Open web browser in `InCognito` or `InPrivate` mode and navigate to http://localhost:8080/
* Click on `Login` button to start the sign-in process with Cognito.

If successful, you should be able to see a list of active conversations for the signed-in user.

> Review the debug messages in the command line for OIDC/Identity Center JWT tokens and any error messages to trouble shoot issues.

## 6/ Cleanup
To avoid incurring additional charges, make sure you delete any resources and services created for this tutorial.
* Delete the CFN stack for Deploying IAM Roles required by sample web application
* Delete the CFN stack for Deploying Trusted token issuer (TTI)
* Delete Amazon Q Business Application
* Delete Identity Center instance
* Delete web application registration from Cognito
* Delete samples users created in Cognito.
* Delete/disable Cognito user pool.
