import serial
import time
import os

action = {'1': [b'D',b'L', b'T']}
program = None
D = None
act = None

class EstabelecimentoComm:
    def __init__(self, device):
        try:
            self.xbee = serial.Serial(
                port=device,
                baudrate = 9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                timeout=1            
            )

            print('Feito!')
            self.program =  True
            self.send = None
        
        except:
            print('Impossível estabelecer comunicação!')
            self.program  = False

    def sendData(self, dev, what):
        self.send = action[dev][int(what)]
        self.xbee.write(bytes(self.send))
        #print(action[dev][int(what)])

    def receiveData(self):
        data = None
        data = self.xbee.read()
        return data

if __name__ == '__main__':
    os.system('sudo chmod 777 /dev/ttyUSB0')
    coordenador = EstabelecimentoComm('/dev/ttyUSB0')
    
    while coordenador.program:
            
        print('\nQue dispositivo pretende controlar? \n')
        dev = input('1- Dispositivo 1\n\n->')
        print('\nQue ação pretende realizar? \n')
        act = input('1- Controlar o relé\n2- Valor da temperatura\n\n->')
            
        if act == '1':
            act = input('\n0- Desligar Relé\n1- Ligar Relé\n\n->')
            coordenador.sendData(dev, act)

        elif act == '2':
            coordenador.sendData(dev, act)
            time.sleep(0.25)
            D = coordenador.receiveData()
            print(D)
