"""
@Time       :2026/9/7 16:11
@Author     :240227206@qq.com
@File       :upload_file_handler.py
"""
from dataclasses import dataclass

from injector import inject

from internal.schema.upload_file_schema import UploadFileReq, UploadFileResp, UploadImageReq
from internal.service import CosService
from pkg.response import validation_resp, success_resp


@inject
@dataclass
class UploadFileHandler:
    """上传文件处理器"""
    cos_service: CosService

    def upload_file(self):
        """上传文件/文档"""
        # 1.构建请求并校验
        req = UploadFileReq()
        if not req.validate():
            return validation_resp(req.errors)

        # 2.调用服务上传文件并获取记录
        upload_file = self.cos_service.upload_file(req.file.data)

        # 3.构建响应并返回
        resp = UploadFileResp()
        return success_resp(resp.dump(upload_file))

    def upload_image(self):
        """上传图片"""
        # 1.构建请求并校验
        req = UploadImageReq()
        if not req.validate():
            return validation_resp(req.errors)

        # 2.调用服务并上传文件
        upload_file = self.cos_service.upload_file(req.file.data, True)

        # 3.获取图片的实际URL地址
        image_url = self.cos_service.get_file_url(upload_file.key)

        return success_resp({"image_url": image_url})
