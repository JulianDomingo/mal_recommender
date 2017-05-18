# Temporary script to gather 1,000,000 MAL users to use as a
# training set for testing purposes.

from lxml.html import fromstring
from xml.etree import ElementTree
import re
import requests


class DataGenerator(object):
    def __init__(self):
        self.element_trees = dict()
        # A unique, descriptive user-agent string is needed to avoid
        # the 429 status code.
        self.user_agent_header = {"User-Agent": "Data Scraper Script by user Almiria"} 


    def retrieve_usernames(self, number_of_requests):
        user = 1
        counter = 0

        while counter < number_of_requests:
            response = requests.get("https://myanimelist.net/comments.php?id="
                                    + str(user), headers=self.user_agent_header)
            user += 1
          
            if response.status_code == 404:
                continue

            raw_title = fromstring(response.content).findtext(".//title")
            username = re.sub("'s.*$|\n", "", raw_title)
            self.element_trees.setdefault(username, [None]) 
            
            counter += 1


    def retrieve_element_trees(self):
        for user in self.element_trees.keys():
            response = requests.get("https://myanimelist.net/malappinfo.php?u="
                                    + user, headers=self.user_agent_header) 
            self.element_trees[user][0] = ElementTree.fromstring(response.content) 
             

    def extract_animes(self):
        for user_info in self.element_trees.values():
            self.record_rated_shows(user_info)


    def record_rated_shows(self, user_info):
        tree = user_info[0]

        for anime in tree.findall("anime"):
            if self.is_completed(anime):
                user_info.append((anime.find("series_title").text, anime.find("my_score").text))


    def is_completed(self, anime):
        watched = int(anime.find("my_watched_episodes").text) 
        total   = int(anime.find("series_episodes").text) 
        return (watched == total) and (watched > 0 and total > 0)


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
    generator.retrieve_usernames(5)
    generator.retrieve_element_trees()
    generator.extract_animes()
    generator.write_data()


if __name__ == "__main__":
    main()
