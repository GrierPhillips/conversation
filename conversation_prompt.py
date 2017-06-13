# -*- coding: utf-8 -*-
import json
from watson_developer_cloud import ConversationV1


# BEGIN of python-dotenv section
from os.path import join, dirname
from dotenv import load_dotenv
import os
# END of python-dotenv section

with open('documentation_links.json', 'r') as docs:
    DOCUMENTS = json.load(docs)


def parse_conversation_response(json_data):
    """Parse the response from Conversation and act accordingly.

    Parameters
    ----------
    json_data : {dict} json response from Conversation.

    Returns
    -------
    dict : containing the main elements parsed from the response
           ("text", "action", "entities", "intents"...)

    Notes
    -----
    For an example of the JSON structure, see file 'pytest_data/conversation_hello.json'
    """
    out_dict = {
        'text': '\n'.join(json_data['output']['text']),
        'action': json_data['output'].get('action')
    }
    return(out_dict)


def handle_conversation_data(parsed_data):
    print(f'Conversation> {parsed_data["text"]}')
    action = parsed_data.get('action')
    if action:
        for key, value in action.items():
            result = globals()[key](value)
            print(f'Conversation> I found the following results related to {value}:\n{result}')


def search_document(documentation):
    """Search for links related to documentation."""
    return DOCUMENTS[documentation]


def main_loop(conversation, workspace_id):
    """Loops the dialog by asking for a prompt,
    submitting to Watson Conversation, parsing and handling the response.

    Parameters
    ----------
    conversation : {ConversationV1} the connector to Conversation (Watson API).
    workspace_id : {str} id to workspace in Conversation instance.

    Returns
    -------
    None
    """
    # just for debugging
    print('*** Connecting to your workspace...')

    # connects to conversation to start dialog, retrieves the json respose.
    response = conversation.message(workspace_id=workspace_id)

    # sends the response to our functions
    data = parse_conversation_response(response)
    handle_conversation_data(data)

    # prompt at the beginning of the conversation
    print('(say anything... type quit to quit)')

    # let's do an infinite loop
    context = response['context']
    while True:
        # gets some input from the prompt
        input_content = input('You> ')

        # if you type one of those words, it will exit the while loop
        if (input_content.lower() in {'exit', 'quit', 'q', 'n'}):
            break

        # sends the input to conversation and retrieves the json response.
        response = conversation.message(workspace_id=workspace_id,
                                        message_input={'text': input_content},
                                        context=context)
        context = response['context']

        # sends the response to our functions
        data = parse_conversation_response(response)
        handle_conversation_data(data)


if __name__ == '__main__':
    # BEGIN of python-dotenv section
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)
    # END of python-dotenv section

    # create an instance of the API ConversationV1 object
    conversation_apiobj = ConversationV1(
        username=os.environ.get("CONVERSATION_USERNAME"),
        password=os.environ.get("CONVERSATION_PASSWORD"),
        version='2016-09-20')

    # obtain the workspace id from dotenv
    workspace_id_env = os.environ.get("CONVERSATION_WORKSPACE_ID")

    main_loop(conversation_apiobj, workspace_id_env)
