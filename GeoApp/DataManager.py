'''
File: DataManager.py
Author: Chuncheng
Version: 0.0
'''

import os
import re
import urllib.request
import pandas as pd
from bs4 import BeautifulSoup
from . import logger, PackageInfo

contents_url = 'http://www.stats.gov.cn/tjsj/pcsj/rkpc/6rp/left.htm'


class DataManager(object):
    ''' Manage the Internet Data.
    - The object keeps the contents of the database;
    - All the pages being accessed will be saved to the local disk.
    '''

    def __init__(self, contents_url=contents_url):
        ''' Initialize the manager.

        Args:
        - @contents_url: The url contains the contents of the database.

        Generate:
        - @self.url: The contents_url will be saved to the self.url.
        '''
        self.url = contents_url
        logger.info('Initialized DataManager.')

    def get_uniques(self):
        ''' Get available uniques in self.contents.

        Return:
        - The list of names.
        '''
        logger.debug(f'Got {len(self.contents)} unique entries')
        return self.contents['unique'].to_list()

    def get_path_by_unique(self, unique):
        ''' Get the path by [unique]

        Args:
        - @name: The unique id of the path to get.
        '''
        found = self.contents.query(f'unique == "{unique}"')
        if len(found) > 0:
            logger.debug(
                f'Got path for unique of "{unique}", the entry is "{found}"')
            return found['path'][0]
        else:
            logger.error(f'Failed got path, invalid unique of "{unique}"')
            return None

    def load_contents(self):
        ''' Load contents from the [self.url].
        Parse the contents using BeautifulSoup.

        ---- Load ----
        If the 'left.htm' exists in the 'dataDir', we will use it;
        Otherwise, we will fetch the raw from the [self.url],
        and the raw will be saved to the file immediately.

        ---- Parse ----
        The tables of interest will be saved into a DataFrame table,
        the entry has 'path', 'name' and 'unique' columns.
        Since there are 'long table' and 'total table' in the database,
        we make 'unique' column to make **UNIQUE** id for the entries.

        Generate:
        - @self.contents: The DataFrame table.

        Return:
        - @contents: The DataFrame table.
        '''
        path = os.path.join(PackageInfo['dataDir'], 'left.htm')
        if not os.path.isfile(path):
            resp = urllib.request.urlopen(self.url)
            raw = resp.read()
            with open(path, 'wb') as f:
                f.write(raw)
            logger.debug(f'Wrote content to {path}')
        else:
            raw = open(path).read()
            logger.debug(f'Read content from {path}')

        soup = BeautifulSoup(raw, 'html.parser')
        c = re.compile('html/[ABf].*\.htm')
        lst = soup.find_all('a', attrs={'href': c})

        contents = pd.DataFrame(columns=['path', 'name'])
        values = []
        for e in lst:
            values.append([e.text, e.attrs['href']])
            # contents[e.text] = e.attrs['href']
        contents = pd.DataFrame(values)
        contents.columns = ['name', 'path']

        contents['unique'] = contents['name'] + ': ' + contents['path']

        self.contents = contents
        logger.debug(f'Parsed contents for {len(contents)} entries.')
        return contents


if __name__ == '__main__':
    print('Hello China.')
