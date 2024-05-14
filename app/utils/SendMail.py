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
<body >
    <div style="background-color: gainsboro;">
        <div style="
        display: flex;
        align-items: center;
        justify-content: center;">
            <div style="
            
            align-items: top;
            justify-content: center;
            max-width: 600px;
            width: 800px;
            height: 40rem;">

                <div style="
                display: flex; 
                justify-content: center; 
                padding: 20px 10px 0px 10px">
                    <img src="data:image/svg+xml;base64,CjxzdmcgdD0iMTcxNTY2OTI5OTk0MiIgY2xhc3M9Imljb24iIHZpZXdCb3g9IjAgMCAxMDI0IDEwMjQiIHZlcnNpb249IjEuMSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIiBwLWlkPSI0MjgzIiB3aWR0aD0iNzAiIGhlaWdodD0iNzAiPjxwYXRoIGQ9Ik05NjAgMjc1LjVsLTExMi02NC43VjEyOGMwLTguOC03LjItMTYtMTYtMTZINzExLjJjLTIyLjUgMC00NC41LTUuOS02NC0xNy4xTDU0My40IDM1YTY0LjE1OCA2NC4xNTggMCAwIDAtNjQgMEwzNzUuNyA5NC44Yy0xOS41IDExLjItNDEuNSAxNy4yLTY0IDE3LjJIMTkyYy04LjggMC0xNiA3LjItMTYgMTZ2ODIuMUw2NCAyNzQuOEMyNC40IDI5Ny43IDAgMzM5LjkgMCAzODUuN1Y5MjhjMCAzNS4zIDI4LjcgNjQgNjQgNjRoODk2YzM1LjMgMCA2NC0yOC43IDY0LTY0VjM4Ni4zYzAtNDUuNy0yNC40LTg4LTY0LTExMC44ek01MjcuNiA5OS44bDguMSA0LjdjMy41IDIuMSAyLjEgNy41LTIgNy41aC00NC40Yy00LjEgMC01LjUtNS40LTItNy41bDguMS00LjdjOS45LTUuOCAyMi4yLTUuOCAzMi4yIDB6TTI0MCAxODRjMC00LjQgMy42LTggOC04aDUyOGM0LjQgMCA4IDMuNiA4IDh2Mzc0LjVjMCA1LjctMyAxMS04IDEzLjlsLTE2Mi4zIDkzLjdjLTUgMi45LTExLjEgMi45LTE2LjEgMGwtNTQuOC0zMmMtMTkuOS0xMS42LTQ0LjQtMTEuNy02NC4zLTAuMmwtNTIuNCAzMC4yYy01IDIuOS0xMS4xIDIuOS0xNiAwTDI0OCA1NzAuNWMtNS0yLjktOC04LjEtOC0xMy45VjE4NHpNNjQgMzg4LjdjMC0yMi43IDEyLjEtNDMuOCAzMS43LTU1LjNsODAuMy00N1Y1MjJjMCAzLjEtMy4zIDUtNiAzLjVMNjggNDY2LjdjLTIuNS0xLjQtNC00LjEtNC02Ljl2LTcxLjF6IG0wIDQ3MC43VjU1MmMwLTYuMiA2LjctMTAgMTItNi45bDEwMCA1Ny43IDY0IDM3IDEwMi4yIDU5YzUuMyAzLjEgNS4zIDEwLjggMCAxMy45bC0xMDIuMiA1OS02NCAzNy0xMDAgNTcuNmMtNS4zIDMuMS0xMi0wLjgtMTItNi45ek04OTMuNCA5MjhIMTI3Yy04LjIgMC0xMS4xLTEwLjgtNC0xNC45bDUzLTMwLjYgNjQtMzcgMTc4LjItMTAyLjkgNjQtMzcgMTItNi45YzkuOS01LjcgMjIuMS01LjcgMzIgMGwxNS41IDguOSA2NCAzNyAxNzguMyAxMDMgNjQgMzcgNDkuNCAyOC41YzcuMSA0LjEgNC4yIDE0LjktNCAxNC45eiBtNjYuNi02Ni41YzAgNi4yLTYuNyAxMC0xMiA2LjlsLTEwMC01Ny43LTY0LTM3LTEwMi4zLTU5LjFjLTUuMy0zLjEtNS4zLTEwLjggMC0xMy45bDEwMi4zLTU5IDY0LTM3TDk0OCA1NDdjNS4zLTMuMSAxMiAwLjggMTIgNi45djMwNy42eiBtMC0zOTkuNWMwIDIuOS0xLjUgNS41LTQgNi45bC0xMDIgNTguNGMtMi43IDEuNS02LTAuNC02LTMuNVYyODYuN2w4MC4yIDQ2LjhDOTQ3LjkgMzQ1IDk2MCAzNjYgOTYwIDM4OC44VjQ2MnoiIHAtaWQ9IjQyODQiPjwvcGF0aD48cGF0aCBkPSJNNzA0IDIzMnY0OGMwIDQuNC0zLjYgOC04IDhIMzI4Yy00LjQgMC04LTMuNi04LTh2LTQ4YzAtNC40IDMuNi04IDgtOGgzNjhjNC40IDAgOCAzLjYgOCA4ek03MDQgMzYwdjQ4YzAgNC40LTMuNiA4LTggOEgzMjhjLTQuNCAwLTgtMy42LTgtOHYtNDhjMC00LjQgMy42LTggOC04aDM2OGM0LjQgMCA4IDMuNiA4IDh6TTcwNCA0ODh2NDhjMCA0LjQtMy42IDgtOCA4SDMyOGMtNC40IDAtOC0zLjYtOC04di00OGMwLTQuNCAzLjYtOCA4LThoMzY4YzQuNCAwIDggMy42IDggOHoiIHAtaWQ9IjQyODUiPjwvcGF0aD48L3N2Zz4K" alt="">
                </div>
                <div style="padding: 5px; display: flex; justify-content: center;">
                    <h1>确认电子邮件地址</h1>
                </div>
                <div style="
                display: flex;
                align-items: top;
                justify-content: center;
                background-color: white;
                width: 600px;
                height: 360px;
                box-shadow: 0 8px 20px rgba(0, 0, 0, 0.112);">
                    <div style="padding: 5px;">
                        <div style="display: flex;justify-content: center;">
                            <h3>尊敬的 {name}</h3>
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
                            font-size: large;
                            
                                ">
                                验证您的电子邮件
                            </a>
                        </div>
                        <div style="display: flex;justify-content: center;">
                            <p>或者将本链接复制并粘贴到您的浏览器中进行访问</p>
                        </div>
                        <div style="padding: 10px; display: flex;justify-content: center;">
                            <a  style="
                                max-width: 400px;
                                word-wrap:break-word;
                                color: rgb(67, 179, 141);" 
                                href="{link}">{link}</a>
                        </div>
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



