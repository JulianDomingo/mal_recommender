# Temporary script to gather user data from usernames.txt to use as a
# training set (testing purposes).

from lxml.html import fromstring
from xml.etree import ElementTree
import re
import requests

# TODO: Consider using scrapy instead of requests

class DataGenerator(object):
    def __init__(self):
        with open("usernames.txt") as temp_file:        
            usernames = temp_file.read().splitlines()
        self.element_trees = {user: [None] for user in usernames}
        self.anomalies = dict() 
        # A unique, descriptive user-agent string is needed to avoid
        # the 429 status code.
        self.user_agent_header = {"User-Agent": "Data Scraper Script by user Almiria"}

    
    def retrieve_element_trees(self):
        for user in self.element_trees.keys():
            response = requests.get("https://myanimelist.net/malappinfo.php?u="
                                    + user, headers=self.user_agent_header) 
            self.element_trees[user][0] = ElementTree.fromstring(response.content) 
             

    def extract_animes(self):
        for user, user_info in self.element_trees.items():
            self.record_rated_shows(user_info)


    def record_rated_shows(self, user, user_info):
        tree = user_info[0]

        for anime in tree.findall("anime"):
            if self.is_completed(anime):
                user_info.append((anime.find("series_title").text, anime.find("my_score").text))
        
        if len(user_info) == 1:
            self.anomalies.setdefault(user, tree[0][0].text)


    def is_completed(self, anime):
        watched = int(anime.find("my_watched_episodes").text) 
        total   = int(anime.find("series_episodes").text) 
        return (watched == total) and (watched > 0 and total > 0)


    def handle_anomalies(self):
        with open("usernames.txt") as temp_file:
            usernames = set(temp_file.read().splitlines())
            temp_file.write("\n".join(set(usernames) - set(self.anomalies.keys()))) 
        
        with open("blacklist.txt") as temp_file:
            blacklisted = set(temp_file.read().splitlines())
            temp_file.write("\n".join(set(blacklisted) - set(self.anomalies.values())))

    
    def write_data(self):
        data = ""

        for username, user_info in self.element_trees.items():
            data += "\n".join(username + " " + show[1] + " " + show[0] for show in user_info[1:])
            data += "\n"
        
        training_set = open("training_set.txt", "w")
        training_set.write(data)
        training_set.close()


def main():
    generator = DataGenerator()
    generator.retrieve_element_trees()
    generator.extract_animes()
    generator.handle_anomalies()
    generator.write_data()


if __name__ == "__main__":
    main()
