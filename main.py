'''Emilidos: Send automatic e-mails to new contacts.'''
import re
import pickle
import base64
import sys
import os
from apiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools

match_mail = re.compile(r'''([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4})''')

label_body = {"addLabelIds": ['checked'], "ids": [], "removeLabelIds": []}

def look_for_keywords(message, sender):
    '''Looks if the message has any keword, if yes then calls send_mail'''
    keywords_file = open('keywords.txt')
    message_deep = message['payload']
    while 'parts' in message_deep:
        message_deep = message_deep['parts'][0]
    message_text = message_deep['body']['data']
    message_text = base64.urlsafe_b64decode(message_text)
    for keyword in keywords_file.readlines():
        match_keyword = re.compile(keyword, re.I)
        find_keyword = match_keyword.search(message_text)
        if find_keyword:
            send_mail(sender)

def send_mail(sender):
    '''Sends draft e-mail to sender'''
    original_draft = gmail.users().drafts().list(userId='me', q='to:emilidos@mail.com').execute()
    if original_draft['resultSizeEstimate'] == 0:
        sys.exit('''Draft message not found.
                 \n Please create a draft message with
                destinatary \'emilidos@mail.com\'''')
    if original_draft['resultSizeEstimate'] > 1:
        sys.exit('''Too many draft messages with
                 subject destinatary \'emilidos@mail.com\'.
                 Please delete all but one.''')

    mail_to_send_raw = original_draft['message']['raw']
    mail_to_send_decoded = base64.urlsafe_b64decode(mail_to_send_raw)
    mail_to_send_decoded = re.sub('emilidos@mail.com', sender, mail_to_send_decoded)
    mail_to_send_raw = base64.urlsafe_b64encode(mail_to_send_raw)
    mail_to_send = {"message": {"raw": mail_to_send_raw}}
    mail_to_send = gmail.users().drafts().create(userId='me', body=mail_to_send)
    # Now mail_to_send stores the id of the draft that is going to be sended.

    mail_to_send_body = {'id':mail_to_send['id']}
    gmail.users().drafts().send(userId='me', body=mail_to_send_body)
    # Sends the e-mail

def get_senders(look_labels=True):
    '''look_labels defines what the function does.
    If True, then looks if each message has the label 'checked'.

    If a message is 'checked' then goes to the next message.

    If a message is not 'checked', then adds the label and tries to add the
    sender to senders.txt. If it does, looks for the keywords.

    If false, just gets the senders to sender.txt and labels them'''
    page_token = None
    while True:
        # Loop for email pages
        read_label_file = open('label.txt', 'rb')
        read_label_file_p = pickle.load(read_label_file)
        read_label_file.close()

        if look_labels:
            # The list of messages without label 'checked'
            label_query = '{}{}'.format('-label:', read_label_file_p['id'])
            list_messages = gmail.users().messages().list(
                userId='me', pageToken=page_token, q=label_query).execute()
        else:
            # List of all messages
            list_messages = gmail.users().messages().list(
                userId='me', pageToken=page_token).execute()

        list_messages = list_messages['messages']
        # list_messages is a list of the messages IDs
        mails_tobe_labeled = []

        for message in list_messages: # Loop for mails inside the same page
            # Checks for the sender of each message and stores it to a text file.
            get_message = gmail.users().messages().get(userId='me', id=message['id']).execute()
            mails_tobe_labeled.append(message['id'])

            new_sender = False # Inicializes the variable
            # This only executes when the message is new or look_labels = False
            headers = get_message['payload']['headers']
            for header in headers:
                if header['name'] == 'From':
                    match = match_mail.search(header['value'])
                    if not match:
                        sys.exit(header['value'] + ' doesnt match')
                    sender = match.groups()[0] # String
                    sendern = sender + ' \n'

            senders_r = open('senders.txt')
            if sendern not in senders_r.readlines():
                senders_a = open('senders.txt', 'a')
                senders_a.write(sendern)
                senders_a.close()
                new_sender = True
            senders_r.close()

            if new_sender and look_labels:
                look_for_keywords(get_message, sender)

        # Look for next page // Stop looking messages
        if 'nextPageToken' in list_messages:
            page_token = list_messages['nextPageToken']
        else:
            # Labels the messages and stops looking at them.
            add_labels = {'ids':[], 'addLabelIds':[], 'removeLabelIds':[]}
            add_labels['addLabelIds'].append(read_label_file_p['id'])
            add_labels['ids'] = mails_tobe_labeled
            gmail.users().messages().batchModify(userId='me', body=add_labels).execute()
            # This will raise an error if there are more than 1000 messages
            # to be labeled
            break


def main():
    main_path = os.path.realpath(__file__)
    dir_path = os.path.dirname(main_path)
    os.chdir(dir_path)

    # Credentials ( Get / Send Mail / Modify draft and labels)
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

    gmail = discovery.build('gmail', 'v1', http=credentials.authorize(Http()))
    # Get access to gmail methods

    if first_time:
        # Creates the label 'checked'
        label_body = {'messageListVisibility': 'hide',
                      'name': 'checked',
                      'labelListVisibility': 'labelHide'}
        checked_label = gmail.users().labels().create(userId='me', body=label_body).execute()
        # Saves the label info
        write_label_file = open('label.txt', 'wb')
        pickle.dump(checked_label, write_label_file)
        write_label_file.close()
        # Gets all the senders to senders.txt
        get_senders(look_labels=False)

    get_senders()

if __name__ == '__main__':
    main()
