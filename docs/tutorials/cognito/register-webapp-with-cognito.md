# Register web application with Amazon Cognito

In order to register your web application with Amazon Cognito (Cognito) you will need to have an existing user pool or create a new user pool and add your application to the user pool. To create user pool and register your application you can use the CloudFormation template [qb-api-poc-cognito.yaml](../../../cf/qb-api-poc-cognito.yaml), or follow steps listed at [Create a new user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/tutorial-create-user-pool.html).

To register your web application with Amazon Cognito, you need an existing user pool or must create a new one and add your application to it. You can create a user pool and register your application using the CloudFormation template [qb-api-poc-cognito.yaml](../../../cf/qb-api-poc-cognito.yaml), or by following the steps outlined in [Create a new user pool](https://docs.aws.amazon.com/cognito/latest/developerguide/tutorial-create-user-pool.html).

For the sample web application included in this repository, use the following callback and logout urls as default. You can update domain name and port as needed later.

* **Callback URL:** `http://localhost:8080/authorization-code/callback`
* **Logout URL (Optional):** `https://localhost:8080/logout`

