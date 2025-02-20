import threading
from time import sleep
import time
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
from datetime import datetime
from serial import Serial
from pyfirmata import Arduino, util

class Device(object):
    def __init__(self, source):
        self.model_id = source.get("model_id")
        self.name = source.get("name")
        self.connected = source.get("connected")
        self.door = source.get("door")
        self.light = source.get("light")
        self.heat = source.get("heat")
        self.humidifier = source.get("humidifier")
        self.vent = source.get("vent")

    def from_dict(self, source):
        #dict로부터 Device로 변환
        self.model_id = source.get("model_id")
        self.name = source.get("name")
        self.connected = source.get("connected")
        self.door = source.get("door")
        self.light = source.get("light")
        self.heat = source.get("heat")
        self.humidifier = source.get("humidifier")
        self.vent = source.get("vent")

    def to_dict(self):
        #Device로부터 dict로 변환
        new_dict = {
            "model_id" : self.model_id,
            "name" : self.name,
            "connected" : self.connected,
            "door" : self.door,
            "light" : self.light,
            "heat" : self.heat,
            "humidifier" : self.humidifier,
            "vent" : self.vent
        }
        return new_dict

class Cell(object):
    def __init__(self, source):
        self.model_id = source.get("model_id")
        self.name = source.get("name")
        self.humi = source.get("humi")
        self.soil = source.get("soil")
        self.temp = source.get("temp")
        self.viewtype = 1

    def from_dict(self, source):
        self.model_id = source.get("model_id")
        self.name = source.get("name")
        self.humi = source.get("humi")
        self.soil = source.get("soil")
        self.temp = source.get("temp")
        self.viewtype = 1

    def to_dict(self):
        new_dict = {
            "model_id": self.model_id,
            "name": self.name,
            "humi": self.humi,
            "soil": self.soil,
            "temp": self.temp,
            "viewtype": int(1)
        }
        return new_dict

    def diff_check(self, source):
        # dict형태로 데이터 받아서 현재 Cell 데이터에 변화가 없다면 True 반환
        if self.humi != source.get("humi"):
            return False
        elif self.soil != source.get("soil"):
            return False
        elif self.temp != source.get("temp"):
            return False
        else:
            return True

# 파이어베이스 연결용 비공개 키
cred = credentials.Certificate("./spam-85498-firebase-adminsdk-wsavj-7375d295d7.json")
firebase_admin.initialize_app(cred)
db = firestore.client() # Firestore 객체 생성

# 센싱아두이노 시리얼포트 연결-라즈베리파이
sen1=Serial('/dev/ttyUSB0',9600)    #센싱 아두이노1
sen2=Serial('/dev/ttyUSB1',9600)    #센싱 아두이노2
board=Arduino('/dev/ttyACM0')     #컨트롤 아두이노

# 전시회에서 사용하는 장비에 맞춰서 변경해야댐
user_email = "caesar2746@gmail.com"
model_id = "default"   # 모델명(고유값)
cell1 = "test1"
cell2 = "화초"

# 해당하는 모델명을 등록한 유저의 이메일 조회
doc_ref = db.collection("User_Email").document("default")
doc = doc_ref.get()
if doc.exists:
    user_email = doc.get("Email")
# 이메일에 들어간 필드가 mortality73@gmail.com 밖에 없어서
# 무슨 이메일로 접근하든 저장된거 확인불가임(추가안됨)


# 조회한 유저 이메일로 디바이스 정보 조회 -> 디바이스 실행시 한 번 수행한 뒤엔 제어신호 들어올 때만 조회 및 갱신
doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id)
device = Device(doc_ref.get())

# 디바이스에 연결된 모든 셀 정보 조회
doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Cell_Data").stream()
All_Cell = []   # 디바이스 내의 모든 Cell 정보를 저장하는 리스트
for doc in doc_ref:
    cell = Cell(doc)
    All_Cell.append(cell)

'''
callback_done = threading.Event()
def on_snapshot(doc_snapshot, changes, read_time):
    
    # 전송데이터 구성
    # 케이스제어신호: 케이스뚜껑, 조명, 가습, 환기
    # 셀단위제어신호: 수분, 열선
    
    senData=[]
    for doc in doc_snapshot:
        # User_info ~ Received 경로에서 Received에 변화가 있을 경우 아래 로직이 실행됨
        # 앱에서 제어신호를 Received로 보내면 이쪽에서 처리할 것
        
        senData[doc]
    callback_done.set()

doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Control").document("Received")
doc_watch = doc_ref.on_snapshot(on_snapshot)
'''

# 아두이노 제어핀 설정
#door1 = board.get_pin('s:2:o')
#door2 = board.get_pin('s:3:o')
airfan = board.get_pin('d:4:o')
water1 = board.get_pin('d:6:o')
water2 = board.get_pin('d:7:o')
aero1 = board.get_pin('d:9:o')
aero2 = board.get_pin('d:10:o')
heat1 = board.get_pin('d:11:o')
heat2 = board.get_pin('d:12:o')
led = board.get_pin('d:13:o')

# 아두이노 제어 메소드
def makeSign(s1,t1,h1,s2,t2,h2):
    # cell1의 토양수분공급코드
    if s1<5:
        water1.write(1)
        time.sleep(0.5)
    else:
        water1.write(0)
        time.sleep(0.5)
    # cell2의 토양수분공급코드
    if s2<20:
        water2.write(1)
        time.sleep(0.5)
    else:
        water2.write(0)
        time.sleep(0.5)

    # cell1의 온도제어코드
    if t1<25:
        heat1.write(1)
        time.sleep(0.5)
    else:
        heat1.write(0)
        time.sleep(0.5)
    # cell2의 온도제어코드
    if t1<30:
        heat2.write(1)
        time.sleep(0.5)
    else:
        heat2.write(0)
        time.sleep(0.5)

    # cell1의 습도제어코드
    if h1<60:
        aero1.write(1)
        time.sleep(0.5)
    else:
        aero1.write(0)
        time.sleep(0.5)
    # cell2의 습도제어코드
    if h2<40:
        aero2.write(1)
        time.sleep(0.5)
    else:
        aero2.write(0)
        time.sleep(0.5)

# DB에 접근하는 횟수 감소를 위해서 일정 주기가 아닌 센서값에 변화가 생길 때만 DB에 갱신
while(1):
    try:
        # 셀1로부터 데이터를 받는 부분
        # 메소드로 만드는게 맞는데 테스트용
        if sen1.readable():
            res1=sen1.readline()
            res1=str(res1)
            ref1=list(res1.split(','))
            ref1[0]=ref1[0][-1]
            ref1[3]=ref1[3][:-6]
            print(ref1) 
    
        received_data1 = {
            "name": "test1",
            "model_id": model_id,
            "humi": ref1[3],
            "soil": ref1[1],
            "temp": ref1[2],
            "viewtype": 1
        }
        cell1_update = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Cell_Data").document(received_data1.get("name"))
        cell1_update.set(received_data1)
        # print(received_data1)
    except:
        print('cell1 can`t read...')
    
    try:
        # 셀2로부터 데이터를 받는 부분
        # 메소드로 만드는게 맞는데 테스트용
        if sen2.readable():
            res2=sen2.readline()
            res2=str(res2)
            ref2=list(res2.split(','))
            ref2[0]=ref2[0][-1]
            ref2[3]=ref2[3][:-6]
            print(ref2)

        received_data2 = {
            "name": "화초",
            "model_id": model_id,
            "humi": ref2[3],
            "soil": ref2[1],
            "temp": ref2[2],
            "viewtype": 1
        }
        cell2_update = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Cell_Data").document(received_data2.get("name"))
        cell2_update.set(received_data2)
        # print(received_data2)
    except:
        print('cell2 can`t read...')

    #makeSign(int(ref1[1]),int(ref1[2]),int(ref1[3]),int(ref2[1]),int(ref2[2]),int(ref2[3]))
    
    # 제어신호를 받아 컨트롤하는 부분
    # 디바이스 제어
    doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Control").document("Received")
    doc = doc_ref.get()
    try:
        if doc.exists:
            door = doc.get("door")
            heat = doc.get("heat")
            humidifier = doc.get("humidifier")
            light = doc.get("light")
            vent = doc.get("vent")
            #print(door, heat, humidifier, light, vent)

            # 제어신호 처리하는부분
            # 열선제어
            if heat == "ON":
                heat1.write(0)
                heat2.write(0)
                time.sleep(1)
            elif heat == "OFF":
                heat1.write(1)
                heat2.write(1)
                time.sleep(1)
            else:
                pass
            # 가습제어
            if humidifier == "ON":
                aero1.write(1)
                aero2.write(1)
                time.sleep(1)
            elif humidifier == "OFF":
                aero1.write(0)
                aero2.write(0)
                time.sleep(1)
            else:
                pass
            # 조명제어
            if light == "ON":
                led.write(0)
                time.sleep(1)
            elif light == "OFF":
                led.write(1)
                time.sleep(1)
            else:
                pass
            # 환기팬제어
            if vent == "ON":
                airfan.write(0)
                time.sleep(1)
            elif vent == "OFF":
                airfan.write(1)
                time.sleep(1)
            else:
                pass
            
            up_data = {
                "heat": heat,
                "humidifier": humidifier,
                "light": light,
                "vent": vent
            }
            doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id)
            doc_ref.update(up_data)
            # 기존의 제어요청데이터 삭제
            doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Control").document("Received")
            doc_ref.update({
                "connected" : firestore.DELETE_FIELD,
                "door" : firestore.DELETE_FIELD,
                "heat" : firestore.DELETE_FIELD,
                "humidifier" : firestore.DELETE_FIELD,
                "light" : firestore.DELETE_FIELD,
                "model_id" : firestore.DELETE_FIELD,
                "name" : firestore.DELETE_FIELD,
                "vent" : firestore.DELETE_FIELD,
                "viewtype" : firestore.DELETE_FIELD
            })
    except:
        print("device wait...")
    
    # 제어신호를 받아 컨트롤하는 부분
    # 셀1 제어
    doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Cell_Data").document(cell1).collection("Control").document("Received")
    doc = doc_ref.get()
    try:
        if doc.exists:
            water = doc.get("Water")
            #print(water)

            # 제어신호 처리하는부분
            # 수분공급제어
            if water == "ON":
                water1.write(1)
                time.sleep(2.5)
                water1.write(0)
                time.sleep(0.5)
            else:
                water1.write(0)
                time.sleep(0.5)

            # 기존의 제어요청데이터 삭제
            doc_ref.update({
                "Water" : firestore.DELETE_FIELD
            })
    except:
        print("cell1 wait...")

    # 제어신호를 받아 컨트롤하는 부분
    # 셀2 제어
    doc_ref = db.collection("User_info").document(user_email).collection("User_Device").document(model_id).collection("Cell_Data").document(cell2).collection("Control").document("Received")
    doc = doc_ref.get()
    try:
        if doc.exists:
            water = doc.get("Water")
            #print(water)

            # 제어신호 처리하는부분
            # 수분공급제어
            if water == "ON":
                water2.write(1)
                time.sleep(2.5)
                water2.write(0)
                time.sleep(0.5)
            else:
                water2.write(0)
                time.sleep(0.5)

            # 기존의 제어요청데이터 삭제
            doc_ref.update({
                "Water" : firestore.DELETE_FIELD
            })
    except:
        print("cell2 wait...")
    
    # 한 번 스캔하는 일련의 과정 후 대기시간 -> 너무 짧으면 파이어베이스 업글해야댐
    time.sleep(5)