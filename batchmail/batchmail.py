#!/bin/env python3
from optparse import OptionParser
import configparser
import smtplib
import os
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import COMMASPACE, formatdate
from email.mime.base import MIMEBase
from email import encoders as Encoders
import re

address_list = []
mailServer = {'host': '', 'port': 0}
userInfo = {'username': '', 'password': '',
            'sender': '', 'signature': 'Sent by batchmail'}
mail = {'subject':"", 'content':'', 'file':[]}

def sentmail(mail_server, user_info, mail, address_list):
    print(mail_server, user_info, mail, address_list)
    msg = MIMEMultipart()

    msg['From'] = user_info['sender']
    msg['To'] = address_list[0]
    msg['Subject'] = mail['subject']
    msg.attach(MIMEText(mail['content'], 'html'))

    for each_file in mail['file']:

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(open(each_file, 'rb').read())
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition',
                        "attachment; filename=%s" % os.path.basename(each_file))
        msg.attach(part)

    mailServer = smtplib.SMTP(mail_server['host'], mail_server['port'])
    mailServer.ehlo()
    mailServer.starttls()
    mailServer.ehlo()
    mailServer.login(user_info['username'], user_info['password'])
    mailServer.sendmail(user_info['username'], address_list[0], msg.as_string())
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()


def main():
    parser = OptionParser(usage='Usage: login ......')
    parser.add_option("-c", "--smtp-config", dest="smtp_config",
                      help="Smtp server and login infomation", action="store")
    parser.add_option("-m", "--mail-content", dest="mail_content",
                      help="The mail content you wish to send", action="store")
    parser.add_option("-l", "--mail-list", dest="mail_list",
                      help="The mail list you wish to send", action="store")
    parser.add_option("-g", "--generate-config", dest="gerenate_config",
                      help="Generate template config file", default=False, action="store_true")
    parser.add_option("-f", "--file", dest="file_list",
                      help="Generate template config file", default=[], action="append")

    (options, args) = parser.parse_args()
    # if len(args) < 2:
    #     print("args !!")
    #     exit()

    if options.gerenate_config:
        server_cfg = open('ex_server.cfg', 'w')
        config = configparser.ConfigParser()
        config.add_section('Mail Server')
        config.set('Mail Server', 'host', 'smtp.gmail.com')
        config.set('Mail Server', 'port', '587')
        config.add_section('User Info')
        config.set('User Info', 'username', 'username')
        config.set('User Info', 'password', 'password')
        config.set('User Info', 'sender name', 'Example Name')
        config.set('User Info', 'signature', 'Sent by batchmail')
        config.write(server_cfg)
        server_cfg.close()
    if not options.mail_list:
        parser.error("no mail list ")
    else:
        with open(options.mail_list) as each_mail:
            address_list.append(each_mail.read().strip())
    if not options.smtp_config:
        parser.error("Not server config")
    else:
        config = configparser.RawConfigParser()
        config.read(options.smtp_config)

        if config.has_option('Mail Server', 'host'):
            mailServer['host'] = config.get('Mail Server', 'host')
        if config.has_option('Mail Server', 'port'):
            mailServer['port'] = config.get('Mail Server', 'port')

        if config.has_option('User Info', 'username'):
            userInfo['username'] = config.get('User Info', 'username')
        if config.has_option('User Info', 'password'):
            userInfo['password'] = config.get('User Info', 'password')
        if config.has_option('User Info', 'sender name'):
            userInfo['sender name'] = config.get('User Info', 'sender name')
        if config.has_option('User Info', 'signature'):
            userInfo['signature'] = config.get('User Info', 'signature')
    if options.file_list:
        mail['file'].extend(options.file_list)
    if options.mail_content:
        mail['content'] = options.mail_content

    sentmail(mailServer, userInfo, mail, address_list)


if __name__ == '__main__':
    main()
    exit()
