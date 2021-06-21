from django.utils.translation import gettext as _
from pages.downloader import Downloader


# Custom Exceptions
class ResponseHandlerError(Exception):
    pass


class DownloadResponseHandler:

    def __init__(self, objects=None, headers=None, filename=None):
        self._objects = objects
        self._headers = headers
        self._filename = filename

    def handle_all_response(self):
        try:
            return Downloader().get_csv_response(self._filename, self._objects, self._headers)
        except (
                Exception
        ) as err:
            raise ResponseHandlerError(_(str(err)))
