import zmail
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from utils.Log import Log, Error

class Mail(object):
    smtp_server = 'smtp.qq.com'
    smtp_port = 587
    stmp_user = '745918851@qq.com'
    stmp_password = 'zprgorkvguiibeaj'
    subject = '注册邮箱验证'


    def SendMail(self, receiver, name, link):
        msg = MIMEMultipart()
        msg['From'] = self.stmp_user
        msg['To'] = receiver
        msg['Subject'] = self.subject

        # 构建邮件的HTML正文内容
        body_html = f'''
        <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Document</title>
            </head>
            <body style="background-color: gainsboro;">
                <div style="
                    display: flex;
                    align-items: center;
                    justify-content: center;">
                    <div style="
                    align-items: top;
                    justify-content: center;
                    max-width: 600px;
                    width: 70%;
                    height: 40rem;">
                        <div style="
                        display: flex; 
                        justify-content: center; 
                        padding: 20px 10px 0px 10px">
                            <svg t="1715669299942" class="icon" viewBox="0 0 1024 1024" version="1.1" xmlns="http://www.w3.org/2000/svg" p-id="4283" width="70" height="70"><path d="M960 275.5l-112-64.7V128c0-8.8-7.2-16-16-16H711.2c-22.5 0-44.5-5.9-64-17.1L543.4 35a64.158 64.158 0 0 0-64 0L375.7 94.8c-19.5 11.2-41.5 17.2-64 17.2H192c-8.8 0-16 7.2-16 16v82.1L64 274.8C24.4 297.7 0 339.9 0 385.7V928c0 35.3 28.7 64 64 64h896c35.3 0 64-28.7 64-64V386.3c0-45.7-24.4-88-64-110.8zM527.6 99.8l8.1 4.7c3.5 2.1 2.1 7.5-2 7.5h-44.4c-4.1 0-5.5-5.4-2-7.5l8.1-4.7c9.9-5.8 22.2-5.8 32.2 0zM240 184c0-4.4 3.6-8 8-8h528c4.4 0 8 3.6 8 8v374.5c0 5.7-3 11-8 13.9l-162.3 93.7c-5 2.9-11.1 2.9-16.1 0l-54.8-32c-19.9-11.6-44.4-11.7-64.3-0.2l-52.4 30.2c-5 2.9-11.1 2.9-16 0L248 570.5c-5-2.9-8-8.1-8-13.9V184zM64 388.7c0-22.7 12.1-43.8 31.7-55.3l80.3-47V522c0 3.1-3.3 5-6 3.5L68 466.7c-2.5-1.4-4-4.1-4-6.9v-71.1z m0 470.7V552c0-6.2 6.7-10 12-6.9l100 57.7 64 37 102.2 59c5.3 3.1 5.3 10.8 0 13.9l-102.2 59-64 37-100 57.6c-5.3 3.1-12-0.8-12-6.9zM893.4 928H127c-8.2 0-11.1-10.8-4-14.9l53-30.6 64-37 178.2-102.9 64-37 12-6.9c9.9-5.7 22.1-5.7 32 0l15.5 8.9 64 37 178.3 103 64 37 49.4 28.5c7.1 4.1 4.2 14.9-4 14.9z m66.6-66.5c0 6.2-6.7 10-12 6.9l-100-57.7-64-37-102.3-59.1c-5.3-3.1-5.3-10.8 0-13.9l102.3-59 64-37L948 547c5.3-3.1 12 0.8 12 6.9v307.6z m0-399.5c0 2.9-1.5 5.5-4 6.9l-102 58.4c-2.7 1.5-6-0.4-6-3.5V286.7l80.2 46.8C947.9 345 960 366 960 388.8V462z" p-id="4284"></path><path d="M704 232v48c0 4.4-3.6 8-8 8H328c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h368c4.4 0 8 3.6 8 8zM704 360v48c0 4.4-3.6 8-8 8H328c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h368c4.4 0 8 3.6 8 8zM704 488v48c0 4.4-3.6 8-8 8H328c-4.4 0-8-3.6-8-8v-48c0-4.4 3.6-8 8-8h368c4.4 0 8 3.6 8 8z" p-id="4285"></path></svg>
                        </div>
                        <div style="padding: 5px; display: flex; justify-content: center;">
                            <h1>确认电子邮件地址</h1>
                        </div>
                        <div style="
                        display: flex;
                        align-items: top;
                        justify-content: center;
                        background-color: white;
                        width: 100%;
                        height: 360px;">
                            <div style="padding: 5px;">
                                <div style="display: flex;justify-content: center;">
                                    <h3>尊敬的{name}</h3>
                                </div>
                                <div style="display: flex;justify-content: center;">
                                    <p>出于安全考虑,在平台注册前,需要验证您的邮箱</p>
                                </div>
                                <div style="display: flex;justify-content: center;">
                                    <a href="{link}" style="
                                    font-weight: bold;
                                    color: white;
                                    background-color: rgb(67, 179, 141);
                                    border-radius: 5px;
                                    padding: 18px 55px 18px 55px;
                                    margin: 10px;
                                    text-decoration: none;
                                        ">
                                        验证您的电子邮件
                                    </a>
                                </div>
                                <div style="display: flex;justify-content: center;">
                                    <p>或者将本链接复制并粘贴到您的浏览器中进行访问</p>
                                </div>
                                <div style="display: flex;justify-content: center;">
                                    <a style="
                                        color: rgb(67, 179, 141);" href="{link}">{link}</a>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </body>
        </html>
        '''
        # 添加HTML内容到邮件中
        msg.attach(MIMEText(body_html, 'html'))

        try:
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.stmp_user, self.stmp_password)
                server.sendmail(self.stmp_user, receiver, msg.as_string())
            Log('邮件发送成功')
            return True
        except Exception as e:
            Error(f'邮件发送失败:{e}')
            return False



