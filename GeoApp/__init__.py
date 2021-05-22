'''
File: __init__.py
Author: Chuncheng
Version: 0.0
Purpose: Ensure the folder is a Package
'''

# Imports
import os
import json
import logging

# Package Info
PackageInfo = dict(
    packageName='GeoApp',
    rootDir=os.path.join(os.path.dirname(__file__)),
    dataDir=os.path.join(os.environ['SYNC'], 'GeoAppData'),
    mapboxToken=open(os.path.join(
        os.environ['Onedrive'], 'SafeBox', '.mapbox_token')).read()
)

if not os.path.isdir(PackageInfo['dataDir']):
    os.mkdir(PackageInfo['dataDir'])

alias_province_name = dict()
alias_province_name['广西壮族自治区'] = '广西'
alias_province_name['内蒙古自治区'] = '内蒙古'
alias_province_name['宁夏回族自治区'] = '宁夏'
alias_province_name['新疆维吾尔自治区'] = '新疆'
alias_province_name['西藏自治区'] = '西藏'
with open(os.path.join(PackageInfo['rootDir'],
                       'china_province.geojson'), encoding='utf-8') as f:
    ProvinceMap = json.load(f)
for feature in ProvinceMap['features']:
    name = feature['properties']['NL_NAME_1']
    print(name)
    if name in alias_province_name:
        feature['properties']['NL_NAME_1'] = alias_province_name[name]
        print(name, '-->', alias_province_name[name])

# Make Logger


def mk_logger(name, level, fmt):
    logger = logging.getLogger(name)
    logger.setLevel(level=level)
    handler = logging.StreamHandler()
    formatter = logging.Formatter(fmt)
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


kwargs = dict(
    name='GeoApp',
    level=logging.DEBUG,
    fmt='%(asctime)s - %(levelname)s - %(message)s - (%(filename)s %(lineno)d)'
)

logger = mk_logger(**kwargs)
logger.info('Package Initialized')
