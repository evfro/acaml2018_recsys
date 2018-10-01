import pandas as pd
from io import BytesIO, StringIO

try:
    from pandas.io.common import ZipFile
except ImportError:
    from zipfile import ZipFile


def get_bx_data(local_file=None, get_ratings=True, get_users=False, get_books=False, encoding='unicode_escape'):
    if not local_file:
        zip_file_url = 'http://www2.informatik.uni-freiburg.de/~cziegler/BX/BX-CSV-Dump.zip'
        # downloading data
        import urllib.request
        with urllib.request.urlopen(zip_file_url) as zip_response:
            zip_contents = BytesIO(zip_response.read())
    else:
        zip_contents = local_file

    ratings = users = books = None

    with ZipFile(zip_contents) as zfile:
        zip_files = pd.Series(zfile.namelist())
        zip_file = zip_files[zip_files.str.contains('ratings', flags=2)].iat[0]

        delimiter = ';'
        if get_ratings:
            zdata = zfile.read(zip_file)
            ratings = pd.read_csv(BytesIO(zdata), encoding=encoding,
                                  sep=delimiter, header=0, engine='c')

        if get_users:
            zip_file = zip_files[zip_files.str.contains('users', flags=2)].iat[0]
            zdata = zfile.read(zip_file)
            users = pd.read_csv(ByteIO(zdata), sep=delimiter, header=0, engine='c',)

        if get_books:
            zip_file = zip_files[zip_files.str.contains('books', flags=2)].iat[0]
            zdata = zfile.read(zip_file)
            books = pd.read_csv(BytesIO(zdata), encoding=encoding,
                                sep=delimiter, header=0, engine='c',
                                quoting=1, escapechar='\\',
                                usecols=['ISBN', 'Book-Author', 'Publisher'])

    res = [data.rename(columns=lambda x: x.lower().replace('book-', '')
                                                  .replace('-id', 'id'), copy=False)
           for data in [ratings, users, books] if data is not None]
    if len(res)==1: res = res[0]
    return res
