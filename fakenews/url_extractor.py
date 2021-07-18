from bs4 import BeautifulSoup, ResultSet
import re
import requests


class UrlNode:

    def __init__(self, text_search=None):
        self._text_search = text_search

    def get_text_to_search(self):
        return self._text_search


class UrlPattern(UrlNode):

    def __init__(self, start_pattern=None, get_entire_link=False):
        super().__init__(start_pattern)
        self._get_entire_link = get_entire_link

    def is_entire_link(self):
        return self._get_entire_link


class UrlClass(UrlNode):

    def __init__(self, link_class=None):
        super().__init__(link_class)


class UrlExtractor:

    def __init__(self, content, url_nodes=None):
        self._content = content
        self._url_nodes = url_nodes
        if self._url_nodes is not None:
            if len(url_nodes) > 1:
                self._is_a_chain = True
            else:
                self._is_a_chain = False

        # self._pattern = '^https://web.archive.org/web/\w*/$'

    def get_source_links(self):
        if self._url_nodes is None:
            return []

        source_links = self._get_node_links(self._content, self._url_nodes[0])

        #print(self._is_a_chain)
        # check need to access other url
        if self._is_a_chain:
            prov_links = []
            for link in source_links:
                r = requests.get(link)
                #print(r.status_code)
                if r.status_code == 200:
                    prov_links += self._get_node_links(r.content, self._url_nodes[1])

            source_links = prov_links

        return source_links

    def _get_node_links(self, content, node):
        if isinstance(node, UrlPattern):
            return self._get_all_links_with_starting_pattern(content, node.get_text_to_search(), node.is_entire_link())
        else:
            return self._get_all_links_with_class(content, node.get_text_to_search())

    def _get_all_links_with_starting_pattern(self, content, text, entire_link):
        start_links = []

        pattern = self._convert_pattern(text)
        print(pattern)

        links = self._get_all_content_links(content)
        for link in links:
            url = link['href']
            # print(entire_link)
            if re.match(pattern, url):
                #print(url)
                # cut or not the link
                if entire_link:
                    result = url
                    #print(result)
                    start_links.append(result)
                else:
                    # get rest part of the link
                    result = re.split(pattern, url)
                    #print(result[1])
                    start_links.append(result[1])

        return start_links

    def _get_all_content_links(self, content):
        if isinstance(content, ResultSet):
            links = []
            for c in content:
                links += c.find_all('a')
            return links
        else:
            soup = BeautifulSoup(content, 'html.parser')
            return soup.find_all('a')

    def _convert_pattern(self, text):
        # start
        pattern = '^'
        pattern += text
        pattern = pattern.replace('{*}', '\w*')

        return pattern

    def _get_all_links_with_class(self, content, text):
        soup = BeautifulSoup(content, 'html.parser')
        links = []
        for link in soup.find_all('a', class_=text):
            links.append(link['href'])
        return links
