# Julian Domingo

# Temporary script to gather 1,000,000 MAL users to use as a
# training set for testing purposes.

import re
import requests
from lxml.html import fromstring
from xml.etree import ElementTree

element_trees = dict()
# TODO: Fix second regex.
regex = {"\n": "", "'s.*": ""}

def retrieve_usernames(number_of_requests):
    users = 0

    while users < number_of_requests:
        response = requests.get("https://myanimelist.net/comments.php?id="
                                + str(request))
        
        if response.status_code == 404:
            continue

        raw_user = fromstring(response.content).findtext(".//title")

        # Does both regex replacements in a single pass.
        regex = dict((re.escape(k), v) for k, v in list(regex.items()))
        pattern = re.compile("|".join(regex.keys()))
        username = pattern.sub(lambda x: regex[re.escape(x.group(0))], raw_user) 

        element_trees.setdefault(text, None)    
        users += 1


def retrive_element_trees():
    for user in element_trees.keys():
        response = requests.get("https://myanimelist.net/malappinfo.php?u=" + user) 
        element_trees[user] = ElementTree.fromstring(response.content) 


retrieve_usernames(1000000)
retrieve_element_trees()

