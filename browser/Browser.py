import json
import os
import time
import logging
import random

from config import config
from .Mail import Mail
from .MeetingsOpener import meeting_opener


class Browser:
    def __init__(self):
        meetings_path = "variables/meetings.json"
        with open(meetings_path, "a+") as file:
            # if file is empty give necessary data
            if os.stat(meetings_path).st_size == 0:
                json.dump({}, file, indent=2)
                self.__meetings = {}

            else:
                with open(meetings_path, "r") as data:
                    self.__meetings = json.load(data)

    def search_meetings_periodically(self):
        while True:
            self.search_meetings()
            time.sleep(3 * 60 * 60)

    def search_meetings(self):
        if config["searching_flag"]:
            logging.info('Searching mode already on')
            return

        logging.info('Started searching now')
        config["searching_flag"] = True

        logging.info('start searching')
        disposable_meetings = {}

        mailbox = Mail()
        if not mailbox.log_in():
            return

        try:
            for email in self.get_emails():
                urls, dates = mailbox.extract_data_from_mail(email)

                for i in range(len(urls)):
                    name = email + str(random.randint(1000, 10000))
                    disposable_meetings.update({
                        name: {
                            "date": dates[i],
                            "link": urls[i]
                        }
                    })

        except:
            logging.error('ERROR: Lack of internet connection!')

        self.__meetings.update(disposable_meetings)

        with open("variables/meetings.json", "w") as data:
            json.dump(self.__meetings, data, indent=2)

        name_of_next = list(self.__meetings.keys())[0]
        meeting_opener.check_meeting(self.__meetings[name_of_next])
        config["searching_flag"] = True
        logging.info('Finished searching')

    def get_emails(self):
        emails = []
        for name in self.__meetings:
            if '@' in name and name not in emails:
                emails.append(name[:-4])
        return emails
