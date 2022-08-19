import os.path
import base64
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
import logging

from browser.Miner import Miner


class Mail:
    def __init__(self):
        self.SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
        self.token_path = 'browser/credentials/token.json'
        self.creds = None
        self.service = None

    def log_in(self):
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, self.SCOPES)

        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())

            else:
                self.__authorize()

            with open(self.token_path, 'w+') as token:
                token.write(self.creds.to_json())

        self.service = build('gmail', 'v1', credentials=self.creds)

    def extract_data_from_mail(self, sender):
        links = []
        dates = []

        try:
            results = self.service.users().messages() \
                .list(userId='me', labelIds=['INBOX'], q=f"from:{sender}").execute()
            messages = results.get('messages', [])

            for message in messages:
                text = self.__read_message(message)
                miner = Miner(text)

                if miner.link and miner.date:
                    links.append(miner.link)
                    dates.append(miner.date)
            return links, dates

        except Exception as error:
            print(f'An error occurred: {error}')

    def __read_message(self, message):
        msg = self.service.users().messages().get(userId='me', id=message['id']).execute()
        email_data = msg['payload']['headers']
        for values in email_data:
            name = values['name']
            if name == 'From':
                from_name = values['value']
                logging.info(f'echo "INFO: Reading email from {from_name}"')

                for part in msg['payload']['parts']:
                    try:
                        data = part['body']["data"]
                        byte_code = base64.urlsafe_b64decode(data)
                        return byte_code.decode("utf-8")

                    except BaseException as error:
                        pass

    def __authorize(self):
        flow = InstalledAppFlow.from_client_secrets_file(f'browser/credentials/credentials.json', self.SCOPES)
        self.creds = flow.run_local_server(port=0)


if __name__ == '__main__':
    import os

    os.chdir(f"{os.path.dirname(os.path.abspath(__file__))}/..")

    mail = Mail()
    mail.log_in()

    # mail.extract_data_from_mail("kubaner1@gmail.com")
