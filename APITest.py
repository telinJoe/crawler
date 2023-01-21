# -*- coding: utf-8 -*-
"""
Created on Fri Nov 18 11:32:01 2022
Modified on 2022-11-30

@author: User
"""
import sys, os

from flask import Flask, jsonify
from flask import request
from flask_cors import CORS
import datetime
import threading
import time

from flask_socketio import SocketIO  # , emit
from flask_socketio import send, emit

from crawler3 import crawler as CrawlerReq

app = Flask(__name__)
# app.config.from_object(configs)
# app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*")

CORS(app)

stop_flag = 0
update_cwb_idx = 0
update_ept_idx = 0
update_tpc_idx = 0


########## read #####

@app.route("/")
def pyConnTest():
    global stop_flag
    print('Hello Flask !')
    Tnow_local = datetime.datetime.today()
    print('stop_flag = ', stop_flag)
    return jsonify(Tnow_local)


########## GET only ##########

@app.route("/Get_TPC_PowerNeed_Pre")
def pyGet_TPC_PowerNeed_Pre():
    tnow_local = datetime.datetime.today().date()
    print('into Get_TPC_PowerNeed_Pre OK...... \n')
    print(tnow_local)
    eInfo = CrawlerReq.electricityInfo_yday(tnow_local);
    print(eInfo)
    return jsonify(eInfo)


@app.route("/Get_TPC_PowerNeed_Now")
def pyGet_TPC_PowerNeed_Now():
    tnow_local = datetime.datetime.today().date()
    eInfo_cur = CrawlerReq.electricityinfo_current(tnow_local)
    return jsonify(eInfo_cur)


@app.route("/Get_TPC_PowerNeed_Post")
def pyGet_TPC_PowerNeed_Post():
    tnow_local = datetime.datetime.today().date()
    eInfo_Next = CrawlerReq.electricityInfo_future(tnow_local)
    return jsonify(eInfo_Next)


@app.route("/Get_TPC_SolarInfo")
def pyGet_TPC_SolarInfo():
    tnow_local = datetime.datetime.today().date()
    eSolar_data = CrawlerReq.solar_info(tnow_local)
    return jsonify(eSolar_data)


@app.route("/Get_ETP_MktInfo")
def pyGet_ETP_MktInfo():
    tnow_local = datetime.datetime.today().date()
    eDeal_data = CrawlerReq.electricity_deal(tnow_local)
    return jsonify(eDeal_data)


@app.route("/Get_ETP_Deal_Spinning")
def pyGet_ETP_Deal_Spinning():
    tnow_local = datetime.datetime.today().date()
    eDeal_Spinning = CrawlerReq.electricity_deal_realtimeStored(tnow_local, CrawlerReq.eacHourValue)
    return jsonify(eDeal_Spinning)


@app.route("/Get_ETP_Deal_Supplemental")
def pyGet_ETP_Deal_Supplemental():
    tnow_local = datetime.datetime.today().date()
    eDeal_Supplemental = CrawlerReq.electricity_deal_replenishStore(tnow_local, CrawlerReq.eacHourValue)
    return jsonify(eDeal_Supplemental)


########## GET and POST ##########
area_id = 'Lukang'
weather2req = {"weather": "none"}


def Read_CWB_Weather():
    global area_id
    global weather2req

    tnow_local = datetime.datetime.today().date()
    weather2req = {"weather": "none"}
    if (area_id == 'Lukang'):
        print("Lukang----")
        weather2req = CrawlerReq.cwb_LugangInfo(tnow_local)
    elif (area_id == 'Lunbei'):
        print("Lunbei---")
        weather2req = CrawlerReq.cwb_LunbeiInfo(tnow_local)
    elif (area_id == 'Budai'):
        print("Budai---")
        weather2req = CrawlerReq.cwb_BudaiInfo(tnow_local)
    elif (area_id == 'Qigu'):
        print("Qigu---")
        weather2req = CrawlerReq.cwb_QiguInfo(tnow_local)
    else:
        print("error")
        # return request.get_json()


@app.route('/Get_CWB_Weather2FC', methods=['POST'])
def pyGet_CWB_Weather2FC():
    global area_id
    global weather2req

    tnow_local = datetime.datetime.today().date()
    # area_req = json.loads(request.get_json())
    area_req = request.get_json()
    area_id = area_req.get("area")
    print(tnow_local)
    print(area_req)
    print(area_id)

    if False:
        # area_req = json.loads (request)
        weather2req = {"weather": "none"}

        if (area_id == 'Lukang'):
            # print ("Lukang----")
            weather2req = CrawlerReq.cwb_LugangInfo(tnow_local)
        elif (area_id == 'Lunbei'):
            # print ("Lunbei---")
            weather2req = CrawlerReq.cwb_LunbeiInfo(tnow_local)
        elif (area_id == 'Budai'):
            # print ("Budai---")
            weather2req = CrawlerReq.cwb_BudaiInfo(tnow_local)
        elif (area_id == 'Qigu'):
            # print ("Qigu---")
            weather2req = CrawlerReq.cwb_QiguInfo(tnow_local)
        else:
            # print ("error")
            return request.get_json()

    Read_CWB_Weather()
    print(weather2req)
    return jsonify(weather2req)


########## socket_io #####
@app.route('/SocketConnTest')
def SocketConnTest():
    global update_cwb_idx
    global update_ept_idx
    global update_tpc_idx

    update_cwb_idx = 0
    update_ept_idx = 0
    update_tpc_idx = 0
    print('Test Begin')
    socketio.emit('apiReply', 'Socket Msg', broadcast=True)
    print('Send Success!')
    print('Test End')
    return 'SocketIO connect ok'


@socketio.on('message')
def Recive(msg):
    print('Recive From Client Message : ', msg)
    socketio.emit('apiReply', 'Socket Connect Success', broadcast=True)


@socketio.on('eventCWB', namespace='/updateCWB')
def pyUpdate_CWB_Info():
    global update_cwb_idx
    global weather2req
    global area_id

    print('updateCWB, update_crawler_idx = ', update_crawler_idx)

    weather2req = {"weather": "none"}

    if (update_cwb_idx == 0):
        area_id = 'Lukang'
        update_cwb_idx = 1
    else:
        if (update_cwb_idx == 1):
            area_id = 'Lunbei'
            update_cwb_idx = 2
        else:
            if (update_cwb_idx == 2):
                area_id = 'Budai'
                update_cwb_idx = 3
            else:
                if (update_cwb_idx == 3):
                    area_id = 'Qigu'
                    update_cwb_idx = 0
                else:
                    update_cwb_idx = 0;

    if (update_cwb_idx <= 3):
        ## push_auto_read ##
        Read_CWB_Weather()
        print(weather2req)
        ## push_auto_emit ##
        # socketio.emit('apiReply' , weather2req ,  broadcast = True)
    return ['updateCWB Sucess', update_cwb_idx]


##### end of pyUpdate_CWB_info


@socketio.on('eventTPC', namespace='/updateTPC')
# @app.route('/updateTPC')
def pyUpdate_TPC_Info():
    global update_tpc_idx

    tnow_local = datetime.datetime.today().date()

    print('updateTPC, update_tpc_idx = ', update_tpc_idx)

    if (update_tpc_idx == 0):
        ## push_auto_read ##
        eInfo = CrawlerReq.electricityInfo_yday(tnow_local)
        ## push_auto_emit ##
        # socketio.emit('apiReply' , eInfo ,  broadcast = True)
        update_tpc_idx = 1
        print(eInfo)
    else:
        if (update_tpc_idx == 1):
            ## push_auto_read ##
            eInfo_cur = CrawlerReq.electricityinfo_current(tnow_local)
            ## push_auto_emit ##
            # socketio.emit('apiReply' , eInfo_cur ,  broadcast = True)
            update_tpc_idx = 2
            print(eInfo_cur)
        else:
            if (update_tpc_idx == 2):
                ## push_auto_read ##
                eInfo_Next = CrawlerReq.electricityInfo_future(tnow_local)
                ## push_auto_emit ##
                # socketio.emit('apiReply' , eInfo_Next ,  broadcast = True)
                update_tpc_idx = 3
                print(eInfo_Next)
            else:
                if (update_tpc_idx == 3):
                    ## push_auto_read ##
                    eSolar_data = CrawlerReq.solar_info(tnow_local)
                    ## push_auto_emit ##
                    # socketio.emit('apiReply' , eSolar_data ,  broadcast = True)
                    update_tpc_idx = 0
                    print(eSolar_data)
                else:
                    update_tpc_idx = 0
    return ['updateTPC Sucess', update_tpc_idx]


@socketio.on('eventEPT', namespace='/updateEPT')
# @app.route('/updateEPT')
def pyUpdate_EPT_info():
    global update_ept_idx

    print('updateEPT, update_ept_idx = ', update_ept_idx)

    tnow_local = datetime.datetime.today().date()
    if update_ept_idx == 0:
        ## push_auto_read ##
        eDeal_data = CrawlerReq.electricity_deal(tnow_local)
        ## push_auto_emit ##
        # socketio.emit('apiReply' , eDeal_data ,  broadcast = True)
        print(eDeal_data)
        update_ept_idx = 1
    else:
        if update_ept_idx == 1:
            ## push_auto_read ##
            eDeal_Spinning = CrawlerReq.electricity_deal_realtimeStored(tnow_local)
            ## push_auto_emit ##
            # socketio.emit('apiReply' , eDeal_Spinning ,  broadcast = True)
            update_ept_idx = 2
            print(eDeal_Spinning)
        else:
            if update_ept_idx == 2:
                ## push_auto_read ##
                eDeal_Supplemental = CrawlerReq.electricity_deal_replenishStore(tnow_local)
                ## push_auto_emit ##
                # socketio.emit('apiReply' , eDeal_Supplemental ,  broadcast = True)
                update_ept_idx = 0
                print(eDeal_Supplemental)
            else:
                update_ept_idx = 0
    return ['updateEPT Sucess', update_ept_idx]


########## Thread declaration ##########
def thread1_run():
    global stop_flag

    # while True:
    #    app.run()
    print('socketio.run ()')
    socketio.run(app, port=5000, allow_unsafe_werkzeug=True)
    # socketio.run(app, port= 5000)
    while True:
        # time.sleep(1)
        if (stop_flag == 1):
            break


# CWB讀取週期 = 30 seconds
#### start --> 30秒 --> 鹿港 --> 30秒 --> 崙背 --> 30秒 --> 布袋 --> 30秒 --> 七股 --> 30秒 --> 鹿港 --> .....

# EPT讀取週期 = 30 seconds
#### 因要錯開30秒，第一個讀取週期是19秒，之後才會是30秒
#### start --> 19秒 --> 昨日電力 --> 30秒 --> 今日電力 --> 30秒 --> 未來電力 --> 30秒 --> 太陽能 --> 30秒 -->  昨日電力 --> .....

# TPC讀取週期 = 25 seconds
#### 因要錯開25秒，第一個讀取週期是6秒，之後才會是25秒
#### start --> 6秒 --> 電力交易 --> 25秒 --> 即時備轉 --> 25秒 --> 補充備轉電力 --> 25秒 --> 電力交易 --> 25秒 -->  即時備轉 --> .....

## push_auto_read ## : 讀crawler
## push_auto_emit ## : socketio emit


tick_start_emit = 0


def thread2_SocketIO_CWB():
    global tick_start_emit
    global update_cwb_idx

    print('thread -- socketIO.run')
    update_cwb_idx = 0
    tick_start_emit = time.perf_counter()
    while True:
        tick_end = time.perf_counter()
        if (tick_end - tick_start_emit) >= 30:
            tick_start_emit = tick_end
            pyUpdate_CWB_Info()
            Tnow_local = datetime.datetime.today()
            print(Tnow_local)


tick_start_ept = 0


def thread3_SocketIO_EPT():
    global tick_start_ept
    global update_ept_idx

    print('thread -- socketIO_EPT.run')
    update_ept_idx = 0
    tick_start_ept = time.perf_counter() - 11
    while True:
        tick_end = time.perf_counter()
        if (tick_end - tick_start_ept) >= 30:
            tick_start_ept = tick_end
            Tnow_local = datetime.datetime.today()
            pyUpdate_EPT_info()
            print('socketIO_EPT ', Tnow_local)


tick_start_tpc = 0


def thread3_SocketIO_TPC():
    global tick_start_tpc
    global update_tpc_idx

    print('thread -- socketIO_TPC.run')
    update_tpc_idx = 0
    tick_start_tpc = time.perf_counter() - 19
    while True:
        tick_end = time.perf_counter()
        if (tick_end - tick_start_tpc) >= 25:
            tick_start_tpc = tick_end
            pyUpdate_TPC_Info()
            Tnow_local = datetime.datetime.today()
            print('socketIO_TPC ', Tnow_local)


########## __main__ ##########
if __name__ == "__main__":

    # app.run()
    # socketio.run(app, debug=True)
    # socketio.run(app)
    try:
        print('App Run !')
        # app.run()
        # socketio.run(app , port= 6000, allow_unsafe_werkzeug=True)

        stop_flag = 0
        update_crawler_idx = 0
        update_tpc_idx = 0
        update_ept_idx = 0
        pth_run = threading.Thread(target=thread1_run)
        pth_SocketIO_CWB = threading.Thread(target=thread2_SocketIO_CWB)
        pth_SocketIO_EPT = threading.Thread(target=thread3_SocketIO_EPT)
        pth_SocketIO_TPC = threading.Thread(target=thread3_SocketIO_TPC)

        pth_run.start()
        pth_SocketIO_CWB.start()
        pth_SocketIO_EPT.start()
        pth_SocketIO_TPC.start()

        pth_run.join()
        pth_SocketIO_CWB.join()
        pth_SocketIO_EPT.join()
        pth_SocketIO_TPC.join()


    except KeyboardInterrupt:
        print('Interrupted')

        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
