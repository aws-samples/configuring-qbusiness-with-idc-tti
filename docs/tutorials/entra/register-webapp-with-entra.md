# Register web application with Okta

Use the steps listed at [Register an application with the Microsoft identity platform](https://learn.microsoft.com/en-us/entra/identity-platform/quickstart-register-app?tabs=certificate#register-an-application) to register your web application. For the sample web application included in this repository, use the following callback and logout urls as default. You can update domain name and port as needed later.

* **Application Type:** Web
* **Callback URL:** `http://localhost:8080/authorization-code/callback`
* **Logout URL:** `http://localhost:8080/logout`

Image below illustrates web application creation configuration.
![okta-create-app](../../../docs/images/entra-create-app.png)

## Entra Token Issuer URI
See [How to find Okta authorization servers Issuer URI](./find-okta-issuer-url.md) to obtain the `Issuer URI` for your web application integration with Okta.

**Issuer URI format:** `https://login.microsoftonline.com/<tenant-id>/v2.0`
![okta-issuer-uri](../../images/entra-issuer-uri.png)

## Validating your web application integration with Okta
1. After registering web application integration as provided in the instructions above, navigate to [Entra Admin Center](https://entra.microsoft.com/) web console.
2. From the left navigation under `Applications` section, select `App registrations`.
3. Click on the Entra app integration for your web application.
4. Select `Overview` side menu item and expand `Essentials` section.
    * Note the `Application (client) ID` as this will be the `Client ID` and `Audience` for your web integration. Also note the `Directory (tenant) ID` as this is the application `Tenant ID` for use with issuer URI above.
    ![okta-client-id](../../images/entra-client-id.png)
5. From `Overview > Essentials` section, click on link for `Redirect URIs` and verify if the callback logout URL is configured correctly as shown in image below.
    ![okta-callback-uri](../../../docs/images/entra-callback-uri.png)
5. From `Overview > Essentials` section, click on link for `Redirect URIs` and verify if.
    * From the `OpenID Connect ID Token` section, note the `Audience` value. By default, the `Audience` and `Client ID` are same. See image below.
    * See [How to find Okta authorization servers Issuer URI](./find-okta-issuer-url.md) to obtain the `Issuer URI` for your web application integration with Okta.
    ![okta-app-issuer](../../../docs/images/okta-app-issuer.png)
