from django.http import HttpResponse

from tempfile import NamedTemporaryFile
import os
import csv


class Downloader:

    def __init__(self):
        pass

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

    def _generate_csv_response(self, filename):
        response = HttpResponse(content_type="text/csv")
        response['Content-Disposition'] = 'attachment; filename=' + filename
        return response
