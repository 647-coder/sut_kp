#coding: utf:8
import requests
import re
import sys
import pytesseract
import os
from PIL import Image

print("欢迎使用沈阳工业大学自动教评系统。Github: github.com/647-coder/sut_kp。")

header = {  "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding":"gzip, deflate",
            "Accept-Language":"zh-CN,zh;q=0.8",
            "Cache-Control":"max-age=0",
            "Connection":"keep-alive",
            "Content-Type":"application/x-www-form-urlencoded",
            "Upgrade-Insecure-Requests":"1",
            "User-Agent":"Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
            }

username = None
passowrd = None

if len(sys.argv) >= 3:
    username = sys.argv[1]
    password = sys.argv[2]
else:
    username = input('用户名 > ')
    password = input('密码 > ')

print("正在登录...账号：{0} 密码：{1}".format(username, password))

session = requests.Session()
session.get("http://jwc.sut.edu.cn/")

while True:
    res = session.get("http://jwc.sut.edu.cn/ACTIONVALIDATERANDOMPICTURE.APPPROCESS")
    with open('vcode.jpg', 'wb') as f:
        f.write(res.content)
    im = Image.open('vcode.jpg')
    vcode = pytesseract.image_to_string(im)

    loginparams = { 'WebUserNO' : username,
                    'Password' : password,
                    'Agnomen' : vcode,
                    'submit.x': '30' ,
                    'submit.y' : '20'
                    }

    login = session.post("http://jwc.sut.edu.cn/ACTIONLOGON.APPPROCESS", data=loginparams, headers=header)
    loginpage = login.text
    
    if u"个人信息" in loginpage:
        print("登录成功！")
        break
    elif u"错误的" in loginpage:
        print("用户名或密码错误。")
        os._exit(1)
        #username = input('用户名 > ')
        #password = input('密码 > ')
    else:
        print("自动识别验证码错误，正在重新尝试...")

session.get("http://jwc.sut.edu.cn/ACTIONJSATTENDAPPRAISE_001.APPPROCESS", headers=header)
res = session.get("http://jwc.sut.edu.cn/ACTIONJSCHOSEAPPRAISESERIESID.APPPROCESS", headers=header)
reg = "javascript:document.location='(.+)';"
com = re.compile(reg)
allurl = re.findall(com, res.text)

courses = []
for each in allurl:
    tempurl = 'http://jwc.sut.edu.cn/' + each
    res = session.get(tempurl, headers=header)
    page = res.text
    courses += re.findall(com, page)

print("共发现 {0} 个需要课评的课程。".format(len(courses)))
i = 1

for each in courses:
    tempurl = 'http://jwc.sut.edu.cn/' + each
    res = session.get(tempurl, headers=header)
    page = res.text
    reg1 = '<input type="hidden" name="SeriesID" value="([0-9]+)">'
    reg2 = 'name="adjustCode" value="([0-9]+)"'
    reg3 = '<input type="hidden" name="PaperID" value="([0-9]+)">'
    reg4 = '<input type="hidden" name="TaskID" value="([0-9a-zA-Z]+)">'
    reg5 = '<input type="hidden" name="TeacherNO" value="([0-9a-zA-Z&=]+)">'
    reg6 = 'name="ResultID" value="(.+)" checked'
    reg7 = 'type="radio" name="([0-9a-zA-Z_]+)" id='
    com1 = re.compile(reg1)
    com2 = re.compile(reg3)
    com3 = re.compile(reg4)
    com4 = re.compile(reg5)
    com5 = re.compile(reg6)
    com6 = re.compile(reg7)
    com7 = re.compile(reg2)
    params = {  'ItemTypeScore1': "98",
                'ItemTypeID': "1",
                'SeriesID' : str(re.findall(com1, page)[0]),
                'PaperID' : str(re.findall(com2, page)[0]),
                'TaskID' : str(re.findall(com3, page)[0]),
                'TeacherNO': str(re.findall(com4, page)[0]),
                'adjustCode' : str(re.findall(com7, page)[0]),
                'PaperScore' : "98",
                'ResultMemo' : "",
                'Score1_1': '100',
                'Score1_2': '100',
                'Score1_3': '100',
                'Score1_4': '100',
                'Score1_5': '100',
                'Score1_6': '80',
                'Score1_7': '100',
                'ResultID': ['1_1','1_2','1_3','1_4','1_5','1_6','1_7']
                }
    print("课评进度({0}/{1})...".format(i, len(courses)))
    i += 1
    session.post("http://jwc.sut.edu.cn/ACTIONJSUPDATECONTENTRESULT.APPPROCESS", data=params, headers=header)

print("已全部完成！")

os._exit(0)
