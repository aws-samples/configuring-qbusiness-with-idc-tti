#  Samples for Application Info and for SAML based Conversation API

Each method in the sample code represents a typical API usage use case. They are invoked from the main method. Comment/uncomment use case methods in the `main` method as needed.

> Note: Inspect the sample files and update `app_id`, `region_name`, `user_id` to your Amazon Q Business Application ID, AWS region name and test user.

## Application information samples (info.py)
* Print list of data source ids for an app filtered by data source type
* Iterate and print all indexed documents for an app
* Prints all indexed documents for an app filtered by data source type
* Print app info by iterating thru application objects
* Print list of application objects
* Print list of index ids for a given app
* Print all data source for an app

## Chat/conversation samples (chat.py)
* Print list of active conversations for a given user
* Delete all active conversations for a given user
* Delete all active conversations by age for a given user
* Ask simple question and get answer
* Have a conversation on a topic
* Have a private chat conversation with your file
* Enable/disable AI knowledge/enterprise data only mode using API with citations

## Custom Data Source (custom_ds.py)
* Create a custom data source
* Delete data source
* Use `BatchPutDocument` to sync data with custom data source with/without ACL (Access Control List)

### Executing the sample files
1. Ensure you have completed project installation steps listed in [Project README](../README.md).
2. Rename `<project_home>/samples/.env.dist` file to `<project_home>/samples/.env`
3. Update `.env` file values for region name, Q Business `app_id`, `index_id`, `custom_ds_id`.

```
poetry run python samples/info.py
poetry run python samples/chat.py
poetry run python samples/custom_ds.py
```
