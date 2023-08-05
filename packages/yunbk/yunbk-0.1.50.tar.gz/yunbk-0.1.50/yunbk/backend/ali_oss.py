# -*- coding: utf-8 -*-
"""
OSS SDK: http://help.aliyun.com/view/13438815.html
"""

import os
from oss.oss_api import OssAPI
from .base import BaseBackend
from ..utils import filter_delete_filename_list


OSS_HOST = 'oss.aliyuncs.com'


class OSSBackend(BaseBackend):
    """
    阿里OSS后端
    """

    bucket_name = None
    oss = None

    def __init__(self, access_id, secret_access_key, bucket_name, host=None):
        super(OSSBackend, self).__init__()
        self.bucket_name = bucket_name
        self.oss = OssAPI(host or OSS_HOST, access_id, secret_access_key)

    def upload(self, file_path, category):
        """
        上传
        """

        filename = os.path.basename(file_path)

        # 尝试创建bucket
        rsp = self.oss.create_bucket(self.bucket_name)

        if rsp.status != 200:
            # 说明没有创建成功
            # 文档说409可能代表已经存在，但经过测试已经存在也会返回200
            raise Exception('create_bucket fail: <%s> %s' % (rsp.status, rsp.read()))

        rsp = self.oss.put_object_from_file(
            self.bucket_name,
            os.path.join(category, filename),
            file_path,
        )

        if rsp.status != 200:
            raise Exception('put_object_from_file fail: <%s> %s' % (rsp.status, rsp.read()))

    def clean(self, category, keeps):
        object_list = self.oss.list_objects(self.bucket_name, category+'/')

        delete_filename_list = filter_delete_filename_list(object_list, keeps)
        self.oss.delete_objects(self.bucket_name, delete_filename_list)
