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

### Executing the sample files
Ensure you have completed project installation steps listed in [Project README](../README.md).
Update  `app_id`, `region_name`, `user_id` in `main` method as needed. From the project home folder, execute the following commands to run the code.

```
poetry run python samples/info.py
poetry run python samples/chat.py
```
