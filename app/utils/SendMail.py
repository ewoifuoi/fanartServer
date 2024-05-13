import zmail

class ZMailObject(object):

    def __init__(self):
        # 邮箱账号
        self.username = '745918851@qq.com'

        # 邮箱授权码
        self.authorization_code = 'zprgorkvguiibeaj'

        # 构建一个邮箱服务对象
        self.server = zmail.server(self.username, self.authorization_code)

    # 邮件主体
    mail_body = {
        'subject': '测试报告',
        'content_text': '这是一个测试报告',  # 纯文本或者HTML内容

    }

    # 收件人
    # 可以指定一个人，字符串；也可以是多个人，列表

    def sendMail(self, mail_to):

        # 发送邮件
        self.server.send_mail(mail_to, self.mail_body)

