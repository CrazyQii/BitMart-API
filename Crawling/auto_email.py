from email.mime.text import MIMEText  # 构造邮件
from email.mime.multipart import MIMEMultipart  # 多种形态邮件主题
from email.utils import formataddr
from email.header import Header
import smtplib  # 发送邮件


class AutoEmail(object):
    """ Auto Send Email """
    def __init__(self, stmp_server: str = None, sender_addr: str = None, sender_password: str = None, receiver_addr: list = None):
        if stmp_server is None or sender_addr is None or sender_addr is None or sender_addr is None or receiver_addr is None:
            self.smtp_server = 'smtp.qq.com'  # SMTP服务器地址
            self.sender_addr = '858590598@qq.com'   # 发件人email地址
            self.sender_password = 'thccrrfwonjgbahi'  # SMTP密码
            self.receiver_addr = ['simon@ponyft.com']   # 收件人地址
        else:
            self.smtp_server = stmp_server
            self.sender_addr = sender_addr
            self.sender_password = sender_password
            self.receiver_addr = receiver_addr

    def send(self):
        msg = MIMEMultipart()  # 创建带附件的实例
        # 附件主题以及信息
        msg['Subject'] = Header('Hugo发来的信息').encode('utf-8')
        msg['From'] = formataddr(('Hugo', self.sender_addr))  # 发件人
        msg['To'] = formataddr(('Simon', self.receiver_addr[0]))  # 收件人

        # 邮件正文
        msg.attach(MIMEText('Send by Hugo', 'plain', 'utf-8'))

        # 构造附件
        attach = MIMEText(open('data.xlsx', 'rb').read(), 'base64', 'utf-8')
        attach["Content-Type"] = 'application/octet-stream'
        attach["Content-Disposition"] = 'attachment; filename="data.xlsx"'
        msg.attach(attach)

        try:
            # SMTP协议
            server = smtplib.SMTP(self.smtp_server, 25)
            # server.set_debuglevel(1)  # 显示所有交互信息
            # 登录
            server.login(self.sender_addr, self.sender_password)
            # 发送邮件
            server.sendmail(self.sender_addr, self.receiver_addr, msg.as_string())
            server.quit()
            print('Send email successfully!')
        except smtplib.SMTPException as e:
            print(f'Send email fail! {e}')


# if __name__ == '__main__':
#     a = AutoEmail()
#     a.send()
