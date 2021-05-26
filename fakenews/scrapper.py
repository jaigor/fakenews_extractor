from django.utils.translation import gettext as _
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import json

from fakenews.csvDownloader import CsvDownloader

class NoSoupTypeError(Exception):
    pass
class NoLinksFoundError(Exception):
    pass
class NoOKResponseError(Exception):
    pass
class TooManyRequestError(Exception):
    pass

class Scrapper(CsvDownloader):

    def __init__(
        self,
        basepath,
        linkClass=None,
        dateType=None,
        dateId=None
    ):
        with open("soup/config.json", "r") as f:
            _keys = json.load(f)
            # constants
            self._pageMAX = _keys["pageMAX"]
            self._TimeBetweenReq = _keys["TimeBetweenReq"]

            self._basepath = basepath
            self._linkClass = linkClass
            self._dateType = dateType
            self._dateId = dateId
    
    def get_collection(self):
        links = []
        # collection (from 0 or 1 to N)
        page = 0
        try:
            r0 = requests.get(self._basepath + str(page))
            # 0 can be throw error, so test it for results
            if r0.status_code == 200: # success
                links = self._add_links(r0.content, links)

            # and continue with 1
            page = 1    
            r1 = requests.get(self._basepath + str(page))

            # no pages found
            if (r0.status_code != 200 and r1.status_code != 200):
                error_msg = (
                'Error de Página. \n'
                'No se han encontrado páginas para la url {} '
                ).format(self._basepath)
                raise NoSoupTypeError(_(error_msg))
            else:
                r = r1
                while r.status_code == 200 and page < self._pageMAX:
                    links = self._add_links(r.content, links)

                    page += 1
                    time.sleep(self._TimeBetweenReq)
                    r = requests.get(self._basepath + str(page))

        except requests.exceptions.ConnectionError:
            error_msg = (
                'Error de Conexión. \n'
                'Respuesta no encontrada para la url {} '
            ).format(self._basepath)
            raise NoOKResponseError(_(error_msg))

        # no links found
        if ( len(links) == 0):
            error_msg = (
                'Error en los enlaces. \n'
                'No se encuentran enlaces para la clase {} '
            ).format(self._linkClass)
            raise NoLinksFoundError(_(error_msg))

        return links
    
    def get_posts_content(self, links):
        try:
            posts = []
            for link in links:
                posts.append(self._get_fields(link))
                time.sleep(self._TimeBetweenReq)

            return posts
        except requests.exceptions.ConnectionError:
            error_msg = (
                'Error de Conexión. \n'
                'Respuesta no encontrada para la url {} '
            ).format(link)
            raise NoOKResponseError(_(error_msg))

    def _add_links(self, html_doc, links):
        soup = BeautifulSoup(html_doc, 'html.parser')
        # search by class link
        # base domain
        parsed_uri = urlparse(self._basepath)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        # delete last character if exists
        if domain.endswith('/'):
            domain = domain[:-1]

        # add all links to previous list
        divs = soup.find_all('div', class_=self._linkClass)
        for div in divs:
            # didnt find link
            if div.a != None: 
                links.append(domain + div.a['href'])
        return links

    def _get_title(self, soup):
        # possibilities    
        h1 = soup.find_all('h1')
        h2 = soup.find_all('h2')
        header = soup.find_all('header')

        if (len(h1) > 0):
            return h1[0].get_text()
        elif (len(h2) > 0):
            return h2[0].get_text()
        elif (len(header) > 0):
            return header[0].get_text()
        else:
            print('Internal Error: no title found')
            return "No Title"

    def _get_body(self, soup):
        divs = soup.find_all('div')
        i = 0
        max = 1
        for i in range(len(divs)):
            if len(divs[i]) > max:
                body = divs[i]
                max = len(divs[i])
        return body.get_text()

    def _get_date(self, soup):  
        html = ""
        if self._dateType == "1":      #ID
            html = soup.find(id=self._dateId).get_text()
        elif self._dateType == "2":    #CLASS
            html = soup.find(class_=self._dateId).get_text()
        else:
            print('Internal Error: dateType not found')
            return "No Date"

        return html

    def _get_fields(self, link):
        response = requests.get(link)
        if response.status_code == 200:
            html_doc = response.content
            soup = BeautifulSoup(html_doc, 'html.parser')

            # fields
            title = self._get_title(soup)
            content = self._get_body(soup)
            date = self._get_date(soup)

            return [date, link, title, content]
        else:
            error_msg = (
                'Demasiadas peticiones para la url {} '
            ).format(link)
            raise TooManyRequestError(_(error_msg))