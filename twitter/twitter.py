from django.http import HttpResponse
from django.utils.translation import gettext as _

from tempfile import NamedTemporaryFile
import requests
import os
import csv
import json


# Custom Exceptions
class TweetsRequestError(Exception):
    pass


class UserRequestError(Exception):
    pass


# Base Class
class TwitterAPI:

    def __init__(self):
        self._keys = self._auth()
        self._bearer_token = self._keys["Bearer token"]
        self._headers = self._create_headers(self._bearer_token)

    def get_csv_response(self, filename, objects, headers):
        csvfile = NamedTemporaryFile(delete=False)
        try:
            # create csv file
            with open(filename, 'a', encoding="utf-8", newline='') as csvfile:
                response = self._generate_csv_response(filename)
                csvwriter = csv.writer(response)

                # csv header
                csvwriter.writerow(headers)
                for obj in objects:
                    csvwriter.writerow(obj)
                    csvfile.flush()

                return response
        finally:
            print("Info: Closing and deleting file")
            csvfile.close()
            os.unlink(csvfile.name)

    # To set your envionment variables in your terminal run the following line:
    # export 'BEARER_TOKEN'='<your_bearer_token>'

    def _auth(self):
        with open("twitter/config.json", "r") as f:
            keys = json.load(f)
        return keys

    def _create_headers(self, bearer_token):
        headers = {
            "Authorization": "Bearer {}".format(bearer_token)
        }
        return headers

    def _connect_to_endpoint(self, url):
        response = requests.request("GET", url, headers=self._headers)
        print(response.status_code)
        if response.status_code != 200:
            raise Exception(
                "Request returned an error: {} {}".format(
                    response.status_code, response.text
                )
            )
        return response.json()

    def _generate_csv_response(self, filename):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response


class TweetLookup(TwitterAPI):

    def __init__(
            self,
            query
    ):
        super().__init__()
        self._query = query

    def _create_tweet_url(self):
        # Tweet fields are adjustable.
        # Options include:
        # attachments, author_id, context_annotations,
        # conversation_id, created_at, entities, geo, id,
        # in_reply_to_user_id, lang, non_public_metrics, organic_metrics,
        # possibly_sensitive, promoted_metrics, public_metrics, referenced_tweets,
        # source, text, and withheld
        tweet_fields = "tweet.fields={}&max_results={}".format(
            self._keys["tweet_fields"], self._keys["max_results"]
        )
        url = "https://api.twitter.com/2/tweets/search/recent?query={}&{}".format(
            self._query, tweet_fields
        )
        return url

    def search_tweets(self):
        try:
            url = self._create_tweet_url()
            json_response = self._connect_to_endpoint(url)
            # print(json.dumps(json_response, indent=4, sort_keys=True))
            return json_response['data']

        except requests.exceptions.RequestException as err:
            error_msg = (
                'No se ha encontrado un tweet de Twitter válido'
                'Por favor, pruebe otra consulta'
            )
            raise TweetsRequestError(_(error_msg))


class UserLookup(TwitterAPI):

    def __init__(
            self,
            author_id
    ):
        super().__init__()
        self._author_id = author_id

    def _create_user_url(self):
        # Specify the usernames that you want to lookup below
        # You can enter up to 100 comma-separated values.
        # usernames = "usernames=TwitterDev,TwitterAPI"
        user_fields = "user.fields={}".format(
            self._keys["user_fields"]
        )
        # User fields are adjustable, options include:
        # created_at, description, entities, id, location, name,
        # pinned_tweet_id, profile_image_url, protected,
        # public_metrics, url, username, verified, and withheld
        url = "https://api.twitter.com/2/users/{}?{}".format(
            self._author_id, user_fields
        )
        return url

    def search_user(self):
        try:
            url = self._create_user_url()
            json_response = self._connect_to_endpoint(url)
            # print(json.dumps(json_response, indent=4, sort_keys=True))
            return json_response['data']

        except requests.exceptions.RequestException as err:
            error_msg = (
                'No se ha encontrado un Usuario de Twitter válido'
                'Por favor, pruebe otra consulta'
            )
            raise UserRequestError(_(error_msg))
