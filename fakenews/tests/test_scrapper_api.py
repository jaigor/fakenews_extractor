from django.test import TestCase
import pytest

from fakenews.scrapper import NoLinksFoundError, NoOKResponseError, Scrapper, TooManyRequestError, NoSoupTypeError


class TestScrapperAPI(TestCase):

    def test_get_posts_collection_missing_protocol_url_raises_NoOKResponseError(self):
        with pytest.raises(NoOKResponseError):
            soup = Scrapper(
                basepath="www.wrongurl.com",
                linkClass="class",
                dateId=1,
                dateType="date"
            )
            soup.get_collection()

    def test_get_posts_collection_missing_schema_in_link_class_raises_NoOKResponseError(self):
        with pytest.raises(NoOKResponseError):
            soup = Scrapper(
                basepath="http://www.wrongurl.com"
            )
            soup.get_collection()

    def test_get_posts_collection_with_wrong_links_raises_NoOKResponseError(self):
        with pytest.raises(NoLinksFoundError):
            soup = Scrapper(
                basepath="http://www.maldita.es/malditobulo/",
                linkClass="class",
                dateId=1,
                dateType="date"
            )
            soup.get_collection()

    def test_get_posts_collection_and_return_some(self):
        correct_soup = Scrapper(
            basepath="https://www.maldita.es/malditobulo/",  # this can change with time
            linkClass="section-card-headline"
        )
        collection = correct_soup.get_collection()
        assert len(collection) > 0

    def test_get_posts_content_and_return_posts(self):
        correct_soup = Scrapper(
            basepath="https://www.maldita.es/malditobulo/",  # this can change with time
            linkClass="section-card-headline",
            dateId=1,
            dateType="article-date"
        )
        links = ['https://www.maldita.es/malditobulo/20210610/iman-vial-vacuna-covid-19-nanoparticulas-magneticas/']
        posts = correct_soup.get_posts_content(links)
        assert len(posts) > 0

    def test_get_posts_content_with_wrong_post_url_raises_TooManyRequestError(self):
        with pytest.raises(TooManyRequestError):
            correct_soup = Scrapper(
                basepath="https://www.maldita.es/malditobulo/",  # this can change with time
                linkClass="section-card-headline",
            )
            links = ['https://www.maldita.es/malditobulo/20210610/iman-vial-vacuna-covid-19-nanoparticulas-magnetic']
            posts = correct_soup.get_posts_content(links)