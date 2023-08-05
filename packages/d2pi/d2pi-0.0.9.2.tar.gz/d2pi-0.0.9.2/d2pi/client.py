# -*- coding: utf-8 -*-
import os
import socket

from .config import config
from .utils import get_logger

from .cache import d2_files_list

logger = get_logger(config.path_to_watch)


class Client(object):
    '''
    A simple interface of Dropbox Client
    '''
    @classmethod
    def upload(cls, file_name, as_file_name):
        '''
        upload file_name to as_file_name
        '''
        if '.DS_Store' in file_name:
            return False
        d2_files_list.delete(file_name)
        d2_files_list.delete(as_file_name)

        return cls._upload(file_name, as_file_name)

    @classmethod
    def _upload(cls, file_name, as_file_name):
        socket.setdefaulttimeout(10)
        client = config.client
        logger.info('upload file %s to %s' % (file_name,
                                              as_file_name))
        try:
            if not client:
                return False
            _size = os.path.getsize(file_name)
            _large_file = False
            if _size > config.chunk_upload_max:
                logger.error('file size is limited, '
                             'should not larger than %s',
                             config.chunk_upload_max)
                return False
            if _size > config.upload_max:
                _large_file = True
            if not _large_file:
                with open(file_name, 'r') as f:
                    client.put_file(as_file_name, f, overwrite=True)
            else:
                with open(file_name, 'rb') as f:
                    uploader = client.get_chunked_uploader(f, _size)
                    logger.info('upload big file size: %s' % _size)
                    while uploader.offset < _size:
                        try:
                            logger.info('uploading offset %d'
                                        % uploader.offset)
                            uploader.upload_chunked()
                        except:
                            return
                    uploader.finish(as_file_name)
            logger.info('uploaded')
        except:
            logger.error('upload error')
            return False
        return True

    @classmethod
    def create_folder(cls, path):
        '''
        create folder
        '''
        d2_files_list.delete(path)
        return cls._create_folder(path)

    @classmethod
    def _create_folder(cls, path):
        logger.info('create folder %s' % path)
        socket.setdefaulttimeout(10)
        client = config.client
        try:
            client.file_create_folder(path)
        except:
            logger.error('create folder error')
            return False
        return True

    @classmethod
    def delete(cls, local_path, server_path):
        '''
        delete a path
        '''
        d2_files_list.delete(server_path)
        d2_files_list.delete_by_prefix(local_path)
        return cls._delete(local_path, server_path)

    @classmethod
    def _delete(cls, local_path, server_path):
        logger.info('delete %s' % local_path)
        socket.setdefaulttimeout(10)
        client = config.client
        try:
            client.file_delete(server_path)
            os.system('rm -rf %s' % local_path)
        except:
            logger.error('delete file error')
            return False
        return True

    @classmethod
    def move(cls, local_path, path, to_path):
        '''
        move file from path to to_path
        '''
        d2_files_list.delete_by_prefix(local_path)
        d2_files_list.delete_by_prefix(path)
        d2_files_list.delete(to_path)
        return cls._move(path, to_path)

    @classmethod
    def _move(cls, path, to_path):
        logger.info('move %s to %s' % (path, to_path))
        socket.setdefaulttimeout(10)
        client = config.client
        try:
            client.file_move(path, to_path)
        except:
            client.file_delete(path)
            logger.error('move file error')
        return True

    @classmethod
    def download(cls, file_path, save_to_path):
        '''
        download file from server
        from file_path to save_to_path
        '''
        if d2_files_list.has_value(save_to_path):
            logger.info('file %s in downloded list, not download'
                        % file_path)
            return False
        r = cls._download(file_path, save_to_path)
        if r:
            d2_files_list.set(save_to_path)
        return r

    @classmethod
    def _download(cls, file_path, save_to_path):
        socket.setdefaulttimeout(10)
        if '/' == save_to_path[-1]:
            save_to_path = save_to_path[:-1]
        client = config.client
        if not client:
            return False
        # pylint: disable=E1103
        f, m = client.get_file_and_metadata(file_path)
        if m.get('bytes', 0) > config.download_max:
            Client.prepare_download_bigfile(file_path)
            return False
        logger.info('downloading %s and save to %s' % (file_path,
                                                       save_to_path))
        try:
            with f:
                d = f.read()
                with open(save_to_path, 'w') as f:
                    f.write(d)
                logger.info('downloaded')
            # pylint: enable=E1103
            return True
        except:
            return False

    @classmethod
    def prepare_download_bigfile(cls, file_path):
        '''
        if download a big file, then share file to a url
        and call Client.download_bigfile
        '''
        def _prepare_download_bigfile():
            client = config.client
            try:
                # pylint: disable=E1103
                file_url = client.share(file_path)
                file_url = file_url.get('url', '')
                # pylint: enable=E1103
                if file_url:
                    logger.info('file share to %s' % file_url)
                    Client.download_bigfile(file_url)
                else:
                    logger.info('can not share')
            except:
                logger.error('file %s can not share' % file_path)
        _prepare_download_bigfile()

    @classmethod
    def download_bigfile(cls, file_url):
        '''
        overwrite this method to download big file
        '''
        logger.info('start download big file on url %s' % file_url)
        logger.info('overwrite this method to download')

    @classmethod
    def check_dir_deleted(cls, path=''):
        '''
        check dir is is_deleted
        if is deleted in server
        local path should be deleted too
        but if config.delete_local_file is False
        this will not delete file
        '''
        socket.setdefaulttimeout(10)
        path = path or config.path_to_watch

        for l in os.listdir(path):
            tmp_path = path + '/' + l
            if os.path.isdir(tmp_path):
                cls.check_dir_deleted(tmp_path)
            cls._check_delete(tmp_path)

        cls._check_delete(path)

    @classmethod
    def _check_delete(cls, path):
        if not config.delete_local_file:
            return
        if path == config.path_to_watch:
            return
        local_path = path
        try:
            path = path.replace(config.path_to_watch, '')
        except:
            path = path.decode()
            path = path.replace(config.path_to_watch, '')
            path = path.encode()
        client = config.client
        try:
            # pylint: disable=E1103
            m = client.metadata(path, include_deleted=True)
            if m.get('is_deleted'):
                cls.delete(local_path, path)
            # pylint: enable=E1103
        except:
            pass

client = Client
