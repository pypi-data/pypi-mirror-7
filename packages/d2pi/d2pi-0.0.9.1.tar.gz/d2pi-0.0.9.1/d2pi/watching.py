# -*- coding: utf-8 -*-

import sys
from config import config
from client import client
from watch import Watcher


def run():
    # TODO: should use argparser
    # so it will be better
    w = Watcher()
    w.init()
    args = sys.argv
    args = args[1:]
    watch = True
    download = True
    upload = True
    delete = True
    if args:
        if '-c' == args[0]:
            w.clean()
        if '-e' == args[0]:
            watch = False
        if '-r' == args[0]:
            download = False
        if '-u' == args[0]:
            upload = False
        if '-s' == args[0]:
            delete = False
    if download:
        print('Start download files...')
        w.sync_download()
        client.check_dir_deleted()
        print('Sync server end.')
    print('Start end.')
    if watch:
        while True:
            w.run(upload=upload, download=download, delete=delete)

if __name__ == '__main__':
    print('******************************************')
    print('        THANKS FOR USING DROP2PI')
    print('         GUOJING soundbbg@gmail')
    print('           thanks to bettylwx')
    print('******************************************')
    print('Starting...')
    if not config.is_useable():
        print('ERROR: Please set config of %s' % config.filename)
    else:
        run()
