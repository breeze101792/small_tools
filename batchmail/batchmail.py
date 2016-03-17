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
            'sender name': '', 'signature': 'Sent by batchmail'}
mail = {'subject':"", 'content':'', 'file':[]}

def sentmail(mail_server, user_info, mail, address_list):
    print(mail_server, user_info, mail, address_list)

    msg = MIMEMultipart()
    msg['From'] = userInfo['sender name']
    # msg['To'] = address_list[0]
    msg['Subject'] = mail['subject']
    msg.attach(MIMEText(mail['content'] + "<br><br>" + userInfo['signature'], 'html'))

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
    for idx, each_addr in enumerate(address_list):
        log_file = open("batchmail.log", 'a')
        try:
            msg['To'] = each_addr
            print(idx, " sent to ", each_addr, end="")
            mailServer.sendmail(user_info['username'], each_addr, msg.as_string())
            print(" is done!")
        except:
            log_file.write(idx.__str__() + each_addr + " is faild to sent\n")
            print( " failed to sent!");
            raise
    # Should be mailServer.quit(), but that crashes...
    mailServer.close()


def main():
    parser = OptionParser(usage='Usage: login ......')
    parser.add_option("-c", "--smtp-config", dest="smtp_config",
                      help="Smtp server and login infomation", action="store")
    parser.add_option("-m", "--mail", dest="mail",
                      help="The mail content you wish to send", action="store")
    parser.add_option("-s", "--mail-subject", dest="mail_subject",
                      help="The mail subject you wish to send", action="store")
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
        mail_list = open(options.mail_list)
        for each_mail in mail_list.readlines():
            address_list.append(each_mail.strip())
        mail_list.close()
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
    if not options.mail:
        parser.error("No mail")
    else:
        config = configparser.RawConfigParser()
        config.read(options.mail)

        if config.has_option('Mail', 'subject'):
            mail['subject'] = config.get('Mail', 'subject')
        if config.has_option('Mail', 'content'):
            mail['content'] = config.get('Mail', 'content')

    if options.file_list:
        mail['file'].extend(options.file_list)
    # if options.mail_content:
    #     mail['content'] = open(options.mail_content).read()
    # if options.mail_subject:
    #     mail['subject'] = options.mail_subject

    sentmail(mailServer, userInfo, mail, address_list)


if __name__ == '__main__':
    main()
    exit()
