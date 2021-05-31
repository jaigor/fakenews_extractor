import csv
import os
from tempfile import NamedTemporaryFile

from django.http import HttpResponse


class CsvDownloader:

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
                    csvfile.flush()

                return response
        finally:
            print("Info: Closing and deleting file")
            csvfile.close()
            os.unlink(csvfile.name)

    def _generate_csv_response(self, filename):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response
