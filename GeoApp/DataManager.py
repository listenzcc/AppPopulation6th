'''
File: DataManager.py
Author: Chuncheng
Version: 0.0
'''

import os
import re
import urllib.request
import pandas as pd
import traceback

from bs4 import BeautifulSoup
from . import logger, PackageInfo

contents_url = 'http://www.stats.gov.cn/tjsj/pcsj/rkpc/6rp/left.htm'


def merge_objs(lst):
    '''Merge objs from the [lst]'''
    lst = list(lst)
    res = [''.join(e.split()) for n, e in enumerate(lst) if e not in lst[:n]]
    return '-'.join(res)


def parse_dataFrame(df):
    ''' Parse the DataFrame [df] into known structure.

    Args:
    - @df: The DataFrame to be parsed.

    Returns:
    - @title: The title of the table;
    - @columns: The columns of the table;
    - @body: The table of the DataFrame.
    '''
    # Get the Title from the (0, 0) position
    title = df[0][0]

    # Parse Header
    # We interest on the Rows with the first column is '地 区',
    # [tt] is the string in the first column and the second row,
    # normally, the value is '地 区'.
    tt = df[0].to_list()[1]
    _df = df[df[0] == tt]
    columns = _df.apply(merge_objs)

    # Parse Body
    # The other Rows are the body contents
    _df = df.iloc[1:]
    body = _df[_df[0] != tt].copy()

    # Make the body better
    columns = columns.to_list()
    # for j, e in enumerate(columns):
    #     if e == '现住地':
    #         columns[j] = '地区'
    #         break
    body.columns = columns
    print(body.columns)

    if '地区' in body.columns:
        body['Location'] = body['地区'].map(lambda e: ''.join(e.split()))
        body = body[body['Location'] != '全国']
    body.index = range(len(body))

    return title, columns, body


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

        try:
            self.load_contents()
        except:
            err = traceback.format_exc()
            logger.error(f'Failed to load contents, the error is "{err}"')

        logger.info('Initialized DataManager.')

    def fetch_path(self, path):
        ''' Fetch the content of the [path]

        Args:
        - @path: The path to be fetched.
        '''
        p = os.path.join(PackageInfo['dataDir'], path)
        d = os.path.dirname(p)
        if not os.path.isdir(d):
            os.makedirs(d)
            logger.debug(f'Made dir "{d}"')

        pp = f'{p}.json'
        if os.path.isfile(pp):
            df = pd.read_json(pp)
            logger.debug(f'Read DataFrame from {pp}')
        else:
            url = '/'.join([self.url[:-9], path])
            df = pd.read_html(url)[0]
            df = df.dropna()
            df.to_json(pp)
            logger.debug(f'Wrote DataFrame to {pp}')

        title, columns, body = parse_dataFrame(df)
        # print(title)
        # print(columns)
        # print(body)
        return title, columns, body

    def get_uniques(self):
        ''' Get available uniques in self.contents.

        Return:
        - The list of uniques.
        '''
        if self.contents is None:
            logger.error(f'Failed since contents is None')
            return None

        logger.debug(f'Got {len(self.contents)} unique entries')
        return self.contents['unique'].to_list()

    def get_path_by_unique(self, unique):
        ''' Get the path by [unique]

        Args:
        - @name: The unique id of the path to get.
        '''
        if self.contents is None:
            logger.error(f'Failed since contents is None')
            return None

        found = self.contents.query(f'unique == "{unique}"')
        if len(found) > 0:
            logger.debug(f'Got path for unique of "{unique}"')
            return found['path'].to_list()[0]
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
        # Load
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

        # Parse
        soup = BeautifulSoup(raw, 'html.parser')
        c = re.compile('html/[ABf].*\.htm')
        lst = soup.find_all('a', attrs={'href': c})

        # Make DataFrame table
        contents = pd.DataFrame(columns=['path', 'name'])
        values = []
        for e in lst:
            values.append([e.text, e.attrs['href']])
        contents = pd.DataFrame(values)
        contents.columns = ['name', 'path']
        contents['unique'] = contents['name'] + ': ' + contents['path']

        self.contents = contents
        logger.debug(f'Parsed contents for {len(contents)} entries.')
        return contents
