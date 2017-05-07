from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
import re, pickle

matchMail = re.compile(r'''<(
    [a-zA-Z0-9._%+-]+               # username
    @                               # arroba
    [a-zA-Z0-9.-]+                  # domain name
    \.[a-zA-Z]{2,4}                 # dot something
    )>''', re.VERBOSE)

label_body = {"addLabelIds": ['checked'],"ids": [],"removeLabelIds": []}

def getSenders(creds, look_labels = True):
    # look_labels defines what the function does.
    # If True, then looks if each message has the label 'checked'.
    # If a message is 'checked' then does nothing.
    # If a message is not 'checked', then adds the label and tries to add the
    # sender to senders.txt. If it does, looks for the keywords.
    # If false, just gets the senders to sender.txt and labels them
    page_token = None
    while True:
        # list_messages is a list of the messages IDs
        list_messages = gmail_api.list(userId = 'me', pageToken = page_token).execute()
        list_messages = list_messages['messages']
        read_label_file = open('label.txt','rb')

        for message in list_messages:
            # Checks for the sender of each message and stores it to a text file.
            get_message = gmail_api.get(userId = 'me', id = message['id']).execute()
            if look_labels:
                if read_label_file['id'] in get_message['labelIds']:
                    # In this case the message has been checked before.
                    continue # Look for the next message
                else:
            else: #
                if read_label_file['id'] not in get_message['labelIds']:

            new_sender = False # Inicializes the variable
            # This only executes when the message is new or look_labels = False
            headers = get_message['payload']['headers']
            for header in headers:
                if header['name'] = 'From':
                    match = matchMail.search(header['value'])
                    sender = match.groups()[0] # String
                    sender = sender + ' \n'

            senders_r = open('senders.txt')
            if sender not in senders_r.readlines():
                senders_a = open('senders.txt', 'a')
                senders_a.write(sender)
                senders_a.close()
                new_sender = True
            senders_r.close()

            if new_sender:
                # AQUÍ LA FUNCIÓN PARA VER SI EL EMAIL CONTIENE KEYWORDS

        # Look for next page // Stop looking messages
        if 'nextPageToken' in list_messages:
            page_token = list_messages['nextPageToken']
        else:
            break

# Credentials ( Get / Send Mail )
scopes = ['https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.modify']

storage = file.Storage('storage.json') # Storage for acces tokens
credentials = storage.get() # Gets an access token
first_time = False

if not credentials or credentials.invalid:
    auth_flow = client.flow_from_clientsecrets('client_secret.json', scopes)
    tools.run_flow(auth_flow, storage)
    credentials = storage.get()
    first_time = True
    # Creates a flow object and opens browser to get
    # the credentials in case we don't have already

gmail = discovery.build('gmail', 'v1', http = credentials.authorize(Http()))
gmail_api = gmail.users().messages() # Just simplicity
# Get access to gmail methods

if first_time:
    # Creates the label 'checked'
    checked_label = gmail.users().labels().create(labelListVisibility = 'labelHide', messageListVisibility = 'hide', name = 'checked')
    # Saves the label info
    write_label_file = open('label.txt','wb')
    pickle.dump(checked_label, write_label_file)
    write_label_file.close()
    # Writes all the senders in the inbox when getting the credentials.
    getSenders(credentials, look_labels = False)


### GETING THE MAILS ###

list_messages = gmail_api.list(userId='me').execute()
list_messages = list_messages['messages']
# Now list_messages has a list of dicts with ids of the messages in the first
# page (Must get all if needed)

for message in list_messages:
    get_message = gmail_api.get(userId = 'me', id = message['id']).execute()
    headers = get_message['payload']['headers']
    for header in headers:
        # Gets Sender and Date of the message
        if header['name'] = 'From':
            match = matchMail.search(header['value'])
            sender = match.groups()[0] # String


    # Now check 2 conditions:
    #   1. Is the sender new?
    #   2. Is the message new?
    # If both true, then look if the message has any of the keywords
