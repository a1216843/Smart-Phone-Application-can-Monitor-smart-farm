from serial import Serial
import time

'''
# 센싱아두이노 시리얼포트 연결-라즈베리파이
ser1=Serial('/dev/ttyACM0',9600)
ser2=Serial('/dev/ttyACM1',9600)
'''
# 센싱아두이노 시리얼포트 연결-윈도우10
ser1=Serial('COM10',9600)    #sen
#ser2=Serial('COM10',9600)   #con

def conS(s,cel,con):
    '''
    토양수분센서 데이터를 받아 수분공급하는 코드
    코드표기방식
    토양수분공급 on/off : 1/2
    ''' 
    
    level=25    # 식물마다 정해진 적정수분량
                # 원래는 스마트팜API에서 받아온 변수로 설정해야함.
    if s<level:
        con.write(b'\x1f')
    else:
        con.write(b'\x2f')
    
    return

while ser1.readable()!='\0':
    if ser1.readable():
        res1=ser1.readline()
        res1=str(res1)
        ref1=list(res1.split(','))
        ref1[0]=ref1[0][-1]
        ref1[3]=ref1[3][:-6]

        print(ref1) 
        #conS(int(ref1[1]),'1',ser2)                                            

    time.sleep(5)