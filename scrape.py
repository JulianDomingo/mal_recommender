# Scrapes the watched shows of users by their username, then stores their data
# to a DynamoDB table.
#
#     User = {
#       'username' : 'username',
#       'show_ratings' :
#       {
#           'show1': 'show1_rating',
#           'show2': 'show2_rating',
#           ...
#       }
#     }
#
# This scraper will not run in parallel with the actual recommender. 

import sys
import re
sys.path.insert(0, '.')
import constants
import boto3
import requests

import spice_api as spice

from bs4 import BeautifulSoup
from lxml.html import fromstring

class Scraper:
    def __init__(self):
        self.client = boto3.client(constants.AWS_RESOURCE)
        self.resource = boto3.resource(constants.AWS_RESOURCE)
        self.table = self.fetch_users_table()


    def scrape(self):
        """
        Retrieves the username string from the given ID number,
        given the ID maps to a valid username (4XX HTTP status
        code is not returned).
        """
        with open(constants.LAST_UNCHECKED_ID_FILE, 'r') as id_file:
            last_id_unchecked = long(id_file.read())
            id_file.close()

        for user_id in range(last_id_unchecked, last_id_unchecked + constants.MAX_USERS):
            response = requests.get(constants.MAL_COMMENTS_URL_PREFIX +
                                    str(user_id), headers=constants.USER_AGENT_HEADER)

            last_id_unchecked += 1

            if response.status_code >= 400 and response.status_code < 500:
                continue

            raw_title = fromstring(response.content).findtext(constants.USERNAME_HTML_TAG)
            username = re.sub("'s.*$|\n", "", raw_title)

            print "Storing shows and ratings for '" + username + "'..."

            self.store_watched_shows_and_corresponding_ratings(username)

        with open(constants.LAST_UNCHECKED_ID_FILE, 'w') as id_file:
            id_file.write(str(last_id_unchecked)) 
            id_file.close()


    def store_watched_shows_and_corresponding_ratings(self, username):
        """
        Retrieves and stores the mapping of shows and corresponding 
        ratings for the given user. If the request fails due to 
        too many requests, the request is re-issued after a specified
        amount of time.
        :param username Used to fetch all shows and corresponding 
        ratings related to that user. 
        """
        response = requests.get(constants.MAL_PROFILE_URL_PREFIX + username +
                                constants.MAL_PROFILE_URL_POSTFIX, headers=constants.USER_AGENT_HEADER)

        if constants.TOO_MANY_REQUESTS in response.text: 
            self.reschedule(self.store_watched_shows_and_corresponding_ratings,
                            constants.DEFAULT_WAIT_SECONDS,
                            username)
        
        soup = BeautifulSoup(response.text, 'lxml')          
        medium_list = spice.objects.MediumList(spice.tokens.Medium.ANIME, soup)
        show_ratings = dict(zip(medium_list.get_titles(), medium_list.get_scores()))

        self.table.put_item(
            Item={
                'username': username,
                'show_ratings': show_ratings,
            }
        )
        

    def fetch_users_table(self):
        """
        Returns the DynamoDB table named 'constants.TABLE_NAME'  
        """
        return self.resource.Table(constants.TABLE_NAME) 


    def contains_table(self, table_name):
        """
        Returns true if the table name 'table_name' exists
        within the AWS client's DynamoDB. 
        :param table_name The name of the table to check for.
        """
        return constants.TABLE_NAME in self.client.list_tables()


    def create_table(self, table_name):
        """
        Creates a new table named 'table_name', with the
        partition key indicated by the username and a
        read/write throughput of 20 per second. Finally,
        waits until the table is truly created in DynamoDB
        before returning.
        :param table_name The name of the table to check for.
        """
        local_table = self.resource.create_table(
            TableName=table_name,
            KeySchema=[
                {
                    'AttributeName': 'username',
                    'KeyType' : 'HASH' # Partition Key
                }
            ],
            AttributeDefinitions=[
                {
                    'AttributeName': 'username',
                    'AttributeType': 'S' # String
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 20,
                'WriteCapacityUnits': 20 
            }
        ) 

        # Wait until the table exists.
        local_table.meta.resource.get_waiter('table_exists').wait(TableName=table_name)

        self.table = local_table


    def reschedule(self, func, wait, *args):
        sleep(wait)
        return func(*args)


def main():
    scraper = Scraper()
    scraper.scrape()


if __name__ == "__main__":
    main()
