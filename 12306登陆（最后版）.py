import datetime
import re
import time
from urllib.parse import urlencode, unquote
import json
import requests
from urllib.parse import urlencode
import os
import cons


headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'zh-CN,zh;q=0.9',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
    'Host': 'kyfw.12306.cn',
    'Referer': 'https://kyfw.12306.cn/otn/index/initMy12306',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.99 Safari/537.36'
}

def main(trainDate=None):
    s = requests.Session()
    start_url = "https://kyfw.12306.cn/otn/login/init"
    response = s.get(start_url,headers = headers)

    img_url  = "https://kyfw.12306.cn/passport/captcha/captcha-image?login_site=E&module=login&rand=sjrand&0.24243568610669697"
    response2 = s.get(img_url,headers = headers).content
    with open("captcha.jpg","wb") as f:
        f.write(response2)
    print("验证码图片下载成功")

    code = {
            '1': '40,40',
            '2': '110,40',
            '3': '180,40',
            '4': '260,40',
            '5': '40,120',
            '6': '110,120',
            '7': '180,120',
            '8': '260,120'
        }

    captchacode = input('请输入验证码序号：')
    temp = captchacode.split(' ')
    tempcode = ''
    for i in temp:
        tempcode += code[i] + ','
    finalcode = tempcode.rstrip(',')

    data = {
        'answer': finalcode,
        'login_site': 'E',
        'rand': 'sjrand'
    }

    check_url = "https://kyfw.12306.cn/passport/captcha/captcha-check"
    response3 = s.post(check_url,headers = headers,data=data)
    if response3.status_code == 200:
        print('------验证成功------')
    elif response3.status_code !=200:
        print("------验证失败------")
        exit()

    login_url="https://kyfw.12306.cn/passport/web/login"
    username=input("请输入账号：")
    password=input("请输入密码：")
    data1={
        "username":username,
        "password":password,
        "appid":"otn"
           }

    login_res=s.post(login_url,data=data1)

    Uamtk_url="https://kyfw.12306.cn/passport/web/auth/uamtk"
    data2={"appid":"otn"}
    Uamtk_res=s.post(Uamtk_url,data=data2)
    jsons=json.loads(Uamtk_res.text)
    umtk_id=jsons["newapptk"]
    data4={"tk": umtk_id}
    uamtk_url="https://kyfw.12306.cn/otn/uamauthclient"
    uamtk_res=s.post(uamtk_url,data=data4)
    print("--------第二次验证成功----")


    data3={"_json_att":""}
    user_url="https://kyfw.12306.cn/otn/login/userLogin"
    use_res=s.post(user_url,data=data3)

    print("---------登录成功------")

    print("------进入查票页面------")
    check_picke = "https://kyfw.12306.cn/otn/leftTicket/query?"
    train_date = str(input("请输入要查询的时间(例：2018-07-18 一个月之内可查):"))


    if len(train_date)!= 10:
        print("输入的日期有错误，请重新输入：")
        train_date = str(input("请输入要查询的时间(例：2018-07-18 一个月之内可查):"))

    station  ={}
    for i in cons.station_name.split("@"):
        if i:
            tmp = i.split("|")
            station[tmp[1]] = tmp[2]


    sart_station = input("输入起始站点:")
    sart = station[sart_station]
    end_station = input("输入终点站点:")
    end = station[end_station]

    data5 = {
        'leftTicketDTO.train_date': train_date,
        'leftTicketDTO.from_station': sart,
        'leftTicketDTO.to_station': end,
        'purpose_codes': 'ADULT'
    }

    check_picke2 = check_picke + urlencode(data5)
    response4 = s.get(check_picke2,headers = headers)
    check_data = response4.text
    # print(check_data)

    chepiaolist = json.loads(check_data)
    carsdetails = chepiaolist['data']['result']
    print("=================================================================================")
    n = 0
    for car in carsdetails:
        n += 1
        banci = car.split('|')[3]
        facheshijian = car.split('|')[8]
        daodashijian = car.split('|')[9]
        luchengshijian = car.split('|')[10]
        erdengzuoshuliang = car.split('|')[31]
        if erdengzuoshuliang == "":
            erdengzuoshuliang = '--'

        print('======',
              '[%d]'%n,'班次:', banci.ljust(4) + "\t",
              '发车时间:', facheshijian + "\t",
              '到达时间:', daodashijian + "\t",
              '历程时间:', luchengshijian + "\t",
              '二等座数量:', erdengzuoshuliang.ljust(3) + "\t",
              '======')
    print("=================================================================================")
    CARNUM = int(input("输入想预订的车票的标号>>>"))
    c = carsdetails[CARNUM - 1]

    banci = c.split('|')[3]
    facheshijian = c.split('|')[8]
    daodashijian = c.split('|')[9]
    luchengshijian = c.split('|')[10]
    erdengzuoshuliang = c.split('|')[31]
    # -------------待会再用----------------------------------
    secretStr = c.split('|')[0]
    train_no = c.split('|')[2]




    print('======',
          '班次:', banci.ljust(4) + "\t",
          '发车时间:', facheshijian + "\t",
          '到达时间:', daodashijian + "\t",
          '历程时间:', luchengshijian + "\t",
          '二等座数量:', erdengzuoshuliang.ljust(3) + "\t", '======')


    checkUser_url = "https://kyfw.12306.cn/otn/login/checkUser"
    data_1 = {'_json_att':'' }
    response_4 = s.post(checkUser_url,data =data_1,headers = headers)


    dingpiao_url = 'https://kyfw.12306.cn/otn/leftTicket/submitOrderRequest'
    secretStr = unquote(secretStr)
    now_time = time.strftime("%Y-%m-%d", time.localtime())
    # print(str(now_time))
    data6 = {
    'secretStr': secretStr,
    'train_date': train_date,
    'back_train_date': now_time,
    'tour_flag': 'dc',
    'purpose_codes': 'ADULT',
    'query_from_station_name': sart_station,
    'query_to_station_name': end_station,
    'undefined':''
    }
    response5 = s.post(dingpiao_url,data =data6,headers =headers)



    get_dataurl = 'https://kyfw.12306.cn/otn/confirmPassenger/initDc'
    data7 = {
        '_json_att': ''
    }
    response6 = s.post(get_dataurl, headers=headers, data=data7)
    html = response6.text



    pattern1 = re.compile("globalRepeatSubmitToken ='(.*?)'")
    pattern2 = re.compile("leftTicketStr':'(.*?)'")



    pattern3 = re.compile("purpose_codes':'(.*?)'")
    pattern4 = re.compile("train_location':'(.*?)'")
    pattern5 = re.compile("'key_check_isChange':'(.*?)'")


    rep = re.findall(pattern1, html)
    lef = re.findall(pattern2, html)
    pur = re.findall(pattern3, html)
    tra = re.findall(pattern4, html)
    key = re.findall(pattern5, html)


    RepeatSubmitToken = str(rep[0])
    leftTicketStr = str(lef[0])
    purpose_codes = str(pur[0])
    train_location = str(tra[0])
    key_check_isChange = str(key[0])


    getPassenger_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getPassengerDTOs'
    data8 = {
        '_json_att': '',
        'REPEAT_SUBMIT_TOKEN': RepeatSubmitToken,
    }
    response7 = s.post(getPassenger_url,data= data8,headers = headers)
    print("----------获取乘客及关联的信息---------")



    print("---------检查订单信息---------------")
    data9 = {
        'cancel_flag': '2',
        'bed_level_order_num': '000000000000000000000000000000',
        'passengerTicketStr': 'O,0,1,(买票人姓名),1,(买票人身份证),（买票人电话）,N',
        'oldPassengerStr': '(买票人姓名),1,(买票人身份证),1_',
        'tour_flag': 'dc',
        'randCode':'',
        'whatsSelect': '1',
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN': RepeatSubmitToken
    }
    # print("RepeatSubmitToken---response8",RepeatSubmitToken)
    checkOrderInfo_url = 'https://kyfw.12306.cn/otn/confirmPassenger/checkOrderInfo'
    response8 = s.post(checkOrderInfo_url,data = data9,headers =headers)
    # print('response8:>>',response8.text)


    n = int(train_date.split('-')[0])
    y = int(train_date.split('-')[1])
    r = int(train_date.split('-')[2])
    at = datetime.datetime(n, y, r).strftime("%w")
    d = {
        '0': "Sun",
        '1': "Mon",
        '2': "Tue",
        '3': "Wed",
        '4': "Thu",
        '5': "Fri",
        '6': "Sat", }
    t3 = (n, y, r, 00, 00, 00, 00, 00, 00,)
    t = time.asctime(t3).split(" ")[1:4]
    t.insert(0, d[str(at)])
    t.insert(3, str(n))
    t1 = " ".join(t)
    train_date1 = str(t1) + " GMT+0800 (中国标准时间)"

    data10 = {
            'train_date': train_date1,
            'train_no': train_no,
            'stationTrainCode': banci,
            'seatType': 'O',
            'fromStationTelecode': sart,
            'toStationTelecode': end,
            'leftTicket': leftTicketStr,
            'purpose_codes': '00',
            'train_location': train_location,
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN': RepeatSubmitToken

    }

    getQueueCount_url = 'https://kyfw.12306.cn/otn/confirmPassenger/getQueueCount'
    response9 = s.post(getQueueCount_url,data = data10,headers=headers)
    print('------------开始抢票----------')


    data11 = {
        'passengerTicketStr': 'O（买的座位序列号）,0,1,(买票人姓名),1,(买票人身份证),（买票人电话）,N',
        'oldPassengerStr': '(买票人姓名),1,(买票人身份证),1_',
        'randCode':'',
        'purpose_codes': purpose_codes,
        'key_check_isChange': key_check_isChange ,
        'leftTicketStr': leftTicketStr,
        'train_location': train_location,
        'choose_seats':'',
        'seatDetailType': '000',
        'whatsSelect': '1',
        'roomType': '00',
        'dwAll': 'N',
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN': RepeatSubmitToken,

        }
    confirmSingleForQueue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
    response10 = s.post(confirmSingleForQueue_url,data=data11,headers=headers)

    data12={

            'passengerTicketStr':'O,0,1,(买票人姓名),1,(买票人身份证),（买票人电话）,N',
            'oldPassengerStr':'(买票人姓名),1,(买票人身份证),1_',
            'randCode':'',
            'purpose_codes':'00',
            'key_check_isChange':key_check_isChange,
            'leftTicketStr':leftTicketStr,
            'train_location':train_location,
            'choose_seats':'',
            'seatDetailType':'000',
            'whatsSelect':'1',
            'roomType':'00',
            'dwAll':'N',
            '_json_att':'',
            'REPEAT_SUBMIT_TOKEN':RepeatSubmitToken
            }


    confirmSingleForQueue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/confirmSingleForQueue'
    response11 = s.post(confirmSingleForQueue_url,data=data12,headers=headers)

    print('------------排队等待--------------')

    data13={
        'random': str(time.time()),
        'tourFlag': 'dc',
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN': RepeatSubmitToken

    }
    queryOrderWaitTimeurl = 'https://kyfw.12306.cn/otn/confirmPassenger/queryOrderWaitTime'
    while True:
        response12 = s.post(queryOrderWaitTimeurl,data=data13,headers=headers)
        buydetail = response12.text
        d1= json.loads(buydetail)
        orderId = d1['data']['orderId']
        waitTime = d1['data']['waitTime']

        print('\r 还需要等待的时间:>>{}'.format(waitTime), end='')
        if orderId != None:
            new_orderId = orderId
            break


    resultOrderForDcQueue_url = 'https://kyfw.12306.cn/otn/confirmPassenger/resultOrderForDcQueue'
    data14={
        'orderSequence_no': new_orderId,
        '_json_att':'',
        'REPEAT_SUBMIT_TOKEN': RepeatSubmitToken
    }
    response13 = s.post(resultOrderForDcQueue_url,data = data14,headers= headers)
    print('\n'+'--------订单已生成，请进入12306官网付款--------')

if __name__ == "__main__":
    main()






















# # check_picke = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2018-07-18&leftTicketDTO.from_station=SZQ&leftTicketDTO.to_station=HAN&purpose_codes=ADULT"
# check_picke = "https://kyfw.12306.cn/otn/leftTicket/query?"
#
# data5 = {
#     # 'leftTicketDTO.train_date': train_date,
#     'leftTicketDTO.train_date': '2018-08-10',
#     'leftTicketDTO.from_station': 'SZQ',
#     'leftTicketDTO.to_station': 'HAN',
#     'purpose_codes': 'ADULT'
# }
#
# check_picke2 = check_picke + urlencode(data5)
# response4 = s.get(check_picke2,headers = headers)
# check_data = response4.text
# print(check_data)
# # chepiaolist = json.loads(check_data)
# # print(chepiaolist)
# cars = check_data['data']['result']
# for car in cars:
#     print('班次:',car.split('|')[3]+"\t",
#           '发车时间:',car.split('|')[8]+"\t",
#           '到达时间:',car.split('|')[9])































# check_picke = "https://kyfw.12306.cn/otn/leftTicket/query?leftTicketDTO.train_date=2018-07-18&leftTicketDTO.from_station=SZQ&leftTicketDTO.to_station=HAN&purpose_codes=ADULT"
# response4 = s.get(check_picke,headers = headers)
# print(response4.text)



# ---------------------查询票----------------------------
# train_date = str(input("请输入要查询的时间(例：2018-07-18):"))
# print(type(train_date))
# # from_station =  input("请输入出发地：")
# # to_station =  input("请输入目的地：")
#
# data = {
#     'leftTicketDTO.train_date': train_date,
#     # 'leftTicketDTO.train_date': '2018-08-10',
#     'leftTicketDTO.from_station': 'SZQ',
#     'leftTicketDTO.to_station': 'HAN',
#     'purpose_codes': 'ADULT'
# }
# url = 'https://kyfw.12306.cn/otn/leftTicket/query?'
# url2 = url+urlencode(data)
# print(url2)
# data = s.get(url2,headers = headers).text
# print(data)
# datas = data.json()
# print(datas)
# cars = datas['data']['result']
# for car in cars:
#     print('班次:',car.split('|')[3]+"\t",
#           '发车时间:',car.split('|')[8]+"\t",
#           '到达时间:',car.split('|')[9])