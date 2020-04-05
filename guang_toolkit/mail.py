# -*- coding: utf-8 -*-
# @Time    : 2019/3/31 11:26 AM
# @Author  : 章光辉
# @FileName: mail.py
# @Software: PyCharm

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path
import logging

from jinja2 import Template

try:
    from .basic import Basic
except (ValueError, ImportError):
    from guang_toolkit.basic import Basic

logger = logging.getLogger(__name__)

file_signature = Path(__file__).parent / 'static/signature.html'


def login_logout(func):
    """
    装饰器，用于邮件类的自动登入登出
    :param func:
    :return:
    """

    def in_out(cls, *args, **kwargs):
        cls.login()
        results = func(cls, *args, **kwargs)
        cls.quit()
        return results

    return in_out


class Mail(Basic):
    def __init__(self,
                 path_config=None,
                 user_name=None,
                 password=None,
                 host=None,
                 port=None,
                 isTLS=True):
        """
        初始化邮箱实例
        :param path_config: 邮箱配置文件
        :param user_name: user_name
        :param password: password
        :param host: host
        :param port: port
        :param isTLS: 加密方式是否为TLS，默认为是
        """

        self.user_name = None
        self.password = None
        self.host = None
        self.port = None
        self.set_input(keys=['user_name', 'password', 'host', 'port'],
                       values=[user_name, password, host, port],
                       path_config=path_config)

        self.messages = []
        self.signature = Template(file_signature.read_text(encoding='utf-8-sig'))
        self.signature_keywords = {}
        self.use_signature = False

        self.isTLS = isTLS
        self.server = None

    def clear_messages(self):
        """
        清空邮件列表
        :return:
        """
        self.messages = []

    def clear_signature(self):
        """
        清除签名
        :return:
        """
        self.signature_keywords = {}
        self.use_signature = False

    def set_signature(self,
                      chinese_name,
                      english_name,
                      position,
                      department,
                      phone_number,
                      chinese_company,
                      english_company,
                      chinese_address,
                      english_address):
        """
        添加邮件签名
        :param english_name: 英文名
        :param chinese_name: 中文名
        :param position: 中文职位
        :param department: 英文部门
        :param phone_number: 中国电话
        :param english_company: 英文公司名
        :param chinese_company: 中文公司名
        :param chinese_address: 中文地址
        :param english_address: 英文地址
        :return:
        """
        self.signature_keywords = dict(
            english_name=english_name,
            chinese_name=chinese_name,
            chinese_position=position,
            english_department=department,
            phone_number=str(phone_number),
            english_company=english_company,
            chinese_company=chinese_company,
            chinese_address=chinese_address,
            english_address=english_address,
        )
        self.use_signature = True

    def write_mail(self,
                   receivers: (list, tuple, str),
                   subject='',
                   text: (str, list, tuple) = '',
                   pathes_attachment=None):
        """
        写邮件，支持连续写多封
        :param receivers: 收件人邮箱列表(可多个），如果不指定则发送给自己
        :param subject: 主题，如果不指定则为空
        :param text: 正文，如果不指定则为空
        :param pathes_attachment: 附件的路径(可多个）
        :return:
        """
        if isinstance(receivers, str):
            receivers = [receivers]

        # 创建信息实例
        message = MIMEMultipart()
        message['From'] = self.user_name  # 发件人
        message['To'] = ','.join(receivers)  # 收件人，如果有多个邮件地址，用","分隔即可。
        message['Subject'] = subject  # 主题

        # 添加正文
        if isinstance(text, str):
            text = text.split('\n')
        self.add_main_body(message, text)

        # 添加附件
        if pathes_attachment is not None:
            self.add_attachments(message, pathes_attachment)

        self.messages.append(message)

        return self

    def add_main_body(self,
                      message,
                      texts):
        """
        添加正文
        :param message:
        :param texts:
        :return:
        """
        # 添加正文，设置成html格式更比plain更方便
        signature_keywords = self.signature_keywords.copy() if self.use_signature else {}
        signature_keywords['texts'] = texts
        main_body = self.signature.render(**signature_keywords)
        message.attach(MIMEText(main_body, 'html', 'utf-8'))

    @staticmethod
    def add_attachments(message,
                        attachments: (list, tuple, str)):
        """
        在邮件里添加附件
        :param message:
        :param attachments:
        :return:
        """
        if not isinstance(attachments, (list, tuple)):
            attachments = [attachments]

        for path_attachment in attachments:
            path_attachment = Path(path_attachment)
            if path_attachment.exists():
                with open(str(path_attachment), 'rb') as f:
                    # 不管什么类型的附件，都用MIMEApplication，MIMEApplication默认子类型是application/octet-stream。
                    # 表明这是个二进制的文件，然后客户端收到这个声明后，会根据文件扩展名来猜测。
                    attachment = MIMEApplication(f.read())
                attachment.add_header('Content-Disposition', 'attachment', filename=path_attachment.name)
                message.attach(attachment)
        return message

    def login(self):
        """
        登陆
        :return:
        """

        try:
            # 连接smtp服务器，明文 / SSL / TLS三种方式，根据你使用的SMTP支持情况选择一种
            # server = smtplib.SMTP_SSL(self.host, self.port)  # SSL加密
            self.server = smtplib.SMTP(self.host, self.port)
            if self.isTLS:
                self.server.starttls()
            # server.set_debuglevel(1)  # 打印出和SMTP服务器交互的所有信息
            self.server.login(self.user_name, self.password)
            logger.debug('登陆成功')
        except smtplib.SMTPException as e:
            logger.debug('error', e)

    def quit(self):
        """
        退出
        :return:
        """
        try:
            self.server.quit()
            logger.debug('退出成功')
        except smtplib.SMTPException as e:
            logger.debug('error', e)

    @login_logout
    def send_mail(self):
        """
        发送邮件
        :return:
        """

        # 登录，发送，再退出
        for index, message in enumerate(self.messages):
            self.server.sendmail(message['From'], message['To'].split(','), message.as_string())

        # 清空邮件列表
        self.clear_messages()


class Mail163(Mail):
    def __init__(self, user_name, password):
        super().__init__(
            user_name=user_name,
            password=password,
            host='smtp.163.com',
            port=25
        )
