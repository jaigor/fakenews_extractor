from django.utils.translation import gettext as _
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import time
import json

from fakenews.url_extractor import UrlExtractor
from pages.downloader import Downloader


class NoSoupTypeError(Exception):
    pass


class NoLinksFoundError(Exception):
    pass


class NoOKResponseError(Exception):
    pass


class TooManyRequestError(Exception):
    pass


class Scrapper(Downloader):

    def __init__(self, basepath, linkClass=None, dateType=None, dateId=None, body_class=None):
        super().__init__()
        with open("fakenews/config.json", "r") as f:
            _keys = json.load(f)
            # constants
            self._pageMAX = _keys["pageMAX"]
            self._TimeBetweenReq = _keys["TimeBetweenReq"]

            self._basepath = basepath
            self._linkClass = linkClass
            self._dateType = dateType
            self._dateId = dateId
            self._body_class = body_class

    def get_collection(self):
        links = []
        # collection (from 0 or 1 to N)
        page = 0
        try:
            print(self._basepath + str(page))
            r0 = requests.get(self._basepath + str(page))
            # 0 can be throw error, so test it for results
            if r0.status_code == 200:  # success
                links = self._add_links(r0.content, links)

            # and continue with 1
            page = 1
            print(self._basepath + str(page))
            r1 = requests.get(self._basepath + str(page))

            # no pages found
            if r0.status_code != 200 and r1.status_code != 200:
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
        except requests.exceptions.MissingSchema:
            error_msg = (
                'Error de clase de enlace. \n'
                'Respuesta no encontrada para la clase {} '
            ).format(self._linkClass)
            raise NoOKResponseError(_(error_msg))

        # no links found
        if len(links) == 0:
            error_msg = (
                'Error en los enlaces. \n'
                'No se encuentran enlaces para la clase {} '
            ).format(self._linkClass)
            raise NoLinksFoundError(_(error_msg))

        return links

    def get_posts_content(self, links, url_nodes=None):
        try:
            posts = []
            for link in links:
                fields = self._get_fields(link)
                fields.append(UrlExtractor(fields[3], url_nodes).get_source_links())
                posts.append(fields)
                time.sleep(self._TimeBetweenReq)

            return posts
        except requests.exceptions.ConnectionError:
            error_msg = (
                'Error de Conexión. \n'
                'Respuesta no encontrada para la url {} '
            ).format(self._basepath)
            raise NoOKResponseError(_(error_msg))

    def _add_links(self, html_doc, links):
        soup = BeautifulSoup(html_doc, 'html.parser')
        # base domain in case the need to add to post url
        parsed_uri = urlparse(self._basepath)
        domain = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
        # delete last character if exists
        if domain.endswith('/'):
            domain = domain[:-1]

        # search by class link
        # add all links to previous list
        divs = soup.find_all('div', class_=self._linkClass)
        print("links")
        for div in divs:
            # did find link
            if div.a is not None:
                # check if has protocol
                if div.a['href'].startswith('/'):
                    print(domain + div.a['href'])
                    links.append(domain + div.a['href'])
                else:
                    print(div.a['href'])
                    links.append(div.a['href'])
        return links

    def _get_title(self, soup):
        # possibilities    
        h1 = soup.find_all('h1')
        h2 = soup.find_all('h2')
        header = soup.find_all('header')

        if len(h1) > 0:
            return h1[0].get_text()
        elif len(h2) > 0:
            return h2[0].get_text()
        elif len(header) > 0:
            return header[0].get_text()
        else:
            print('Internal Error: no title found')
            return "No Title"

    def _get_body(self, soup):
        body = ""
        # check if body is not blank
        if self._body_class is not None:
            # search by class div
            body = soup.find_all('div', class_=self._body_class)
            return body
        else:
            divs = soup.find_all('div')
            max = 1
            for i in range(len(divs)):
                if len(divs[i]) > max:
                    body = divs[i]
                    max = len(divs[i])
            if max > 1:
                return body.get_text()
            return body

    def _get_date(self, soup):
        html = ""
        if self._dateType == "1":  # ID
            html = soup.find(id=self._dateId).get_text()
        elif self._dateType == "2":  # CLASS
            html = soup.find(class_=self._dateId).get_text()
        else:
            print('Internal Error: dateType not found')
            html = "No Date"

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
