from lxml.html import fromstring
from xml.etree import ElementTree
import re
import requests

USERS_TO_ADD = 15


class UsernameGenerator(object):
    def __init__(self):
        self.usernames = [] 

        temp = open("blacklist.txt", "r")
        self.starting_id = int(temp.readlines()[len(temp.readlines()) - 1]) + 1

        self.blacklist = [] 
        temp.close()

        self.user_agent_header = {"User-Agent": "Usernames Scraper by Almiria"}
 

    def retrieve_usernames(self):
        user = self.starting_id
        counter = 0

        while counter < USERS_TO_ADD:
            response = requests.get("https://myanimelist.net/comments.php?id="
                                    + str(user), headers=self.user_agent_header)
            user += 1

            if response.status_code >= 400 and response.status_code < 500:
                self.blacklist.append(user - 1)
                continue

            self.add_user(response)
            counter += 1

   
    def add_user(self, response):
        raw_title = fromstring(response.content).findtext(".//title")
        username = re.sub("'s.*$|\n", "", raw_title)
        self.usernames.append(username)


    def record_users(self):
        users = open("usernames.txt", "a")
        users.write("\n".join(username for username in self.usernames) + "\n")
        users.close()

        blacklist = open("blacklist.txt", "a")
        blacklist.write("\n".join(str(user_id) for user_id in self.blacklist) + "\n")
        blacklist.close()


def main():
    generator = UsernameGenerator()
    generator.retrieve_usernames()
    generator.record_users()


if __name__ == "__main__":
    main()
