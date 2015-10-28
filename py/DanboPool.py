import os
import argparse
import configparser
from Utils.PoolLoader import PoolLoader

def getOptions():
    parser = argparse.ArgumentParser(description =  'Download pools from Danbooru')
    parser.add_argument('pool', help='The pool number')
    parser.add_argument('-s', '--settings', action='store_true', help='Change the program settings')
    parser.add_argument('-o', '--output', help='The folder to download to')
    args = parser.parse_args()
    return args

def loadConfig():
    config = configparser.ConfigParser()
    if not os.path.isfile('config.ini'):
        config['Settings'] = { 'DownloadDirectory' : '',
                               'DownloadOriginal' : 'No'}
        saveConfig(config)
        print('\nNo configuration file found.\nA new configuration file has been created.')
        response = input('Would you like to set the configuration now? yes/no\n')
        if response.lower() == 'yes':
            editConfig(config)
    config.read('config.ini')
    return config

def editConfig(config):
    config['Settings']['DownloadDirectory'] = input('Enter your default download directory.\n')
    newOrig = input('Do you want to download the original size files instead of the resampled versions?\n'
                    '(Warning: Some original files are very large.)\nPress enter for default "No"\n')
    if newOrig.lower() == 'Yes':
        config['Settings']['DownloadOriginal'] = 'Yes'
    saveConfig(config)

def saveConfig(config):
    with open('config.ini', 'w') as file:
        config.write(file)

def main():
    args = getOptions()

    config = loadConfig()

    if args.settings:
        editConfig()

    poolLoader = PoolLoader(args.pool, config)
    poolLoader.getImgs()

try:
    main()
except KeyboardInterrupt:
    print('Download interrupted')