from django.http import HttpResponse
from django.utils.translation import gettext as _

import requests
from tempfile import NamedTemporaryFile
import os
import time
import csv
import json

class NoOKResponseError(Exception):
    pass

class TooManyRequestError(Exception):
    pass

class WordpressAPI:

    def __init__(
        self, 
        basepath
    ):
        with open("wordpress/config.json", "r") as f:
            _keys = json.load(f)
            # constants
            self._endpoint = _keys["endpoint"] # API Endpoint for Wordpress
            self._route = _keys["route"]
            self._pageINIT = _keys["pageINIT"]
            # limitation to not overload server
            # or find security issues   
            self._per_page = _keys["per_page"]
            self._pageMAX = _keys["pageMAX"]
            self._TimeBetweenReq = _keys["TimeBetweenReq"]

            self._querystring = "?per_page=" + str(self._per_page) +"&page="
            self._basepath = basepath + self._endpoint

    def get_posts_types(self):
        url = self._basepath + self._route
        try:
            r = requests.get(url)
            if r.status_code == 200:
                types = {}
                data = r.json()
                # get collection of urls
                for key in data:
                    types[data[key]['name']] = data[key]['_links']['wp:items'][0]['href']                    
                
                return types
            else:
                error_msg = (
                    'Error de Conexión. \n'
                    'Demasiadas peticiones para la url {} '
                ).format(url)
                raise TooManyRequestError(_(error_msg))
        except (requests.exceptions.ConnectionError, 
                requests.exceptions.MissingSchema):
            error_msg = (
                'Error de Conexión. \n'
                'Respuesta no encontrada para la url {} '
            ).format(url)
            raise NoOKResponseError(_(error_msg))
        except (requests.exceptions.TooManyRedirects):
            error_msg = (
                'Error de Conexión. \n'
                'Demasiadas peticiones para la url {} '
            ).format(url)
            raise TooManyRequestError(_(error_msg))
        except json.decoder.JSONDecodeError:
            error_msg = (
                'Error de Wordpress. \n'
                'No se usa Wordpress o se permite el acceso  para la url {} '
            ).format(url)
            raise NoOKResponseError(_(error_msg))

    def get_posts_content(self, url):
        posts = []
        # Wordpress module
        # iterate for each post
        page = self._pageINIT
        r = requests.get(url + self._querystring + str(page))

        while r.status_code == 200 and page < self._pageMAX:
            for post in r.json():
                posts.append(self._get_post_fields(post))

            page += 1
            time.sleep(self._TimeBetweenReq)
            r = requests.get(url + self._querystring + str(page))
        
        return posts

    def get_csv_response(self, filename, posts):
        csvfile = NamedTemporaryFile(delete=False)
        try:
            # create csv file
            with open(filename, 'a', encoding="utf-8", newline='') as csvfile:
                response = self._generate_csv_response(filename)
                csvwriter = csv.writer(response)

                # csv header
                csvwriter.writerow(['date', 'link', 'title', 'content'])
                for post in posts:
                    csvwriter.writerow(post)
                
                return response
        finally:
            print("closing and deleting file")
            csvfile.close()
            os.unlink(csvfile.name)

    def _generate_csv_response(self, filename):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response

    def _get_post_fields(self, post):
        # get required fields
        date = post['date']
        link = post['link']
        title = post['title']['rendered']
        content = post['content']['rendered']
        
        return [date, link, title, content]