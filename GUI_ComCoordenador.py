from tkinter import *
import tkinter.messagebox
from digi.xbee.devices import XBeeDevice
from digi.xbee.devices import RemoteXBeeDevice
from digi.xbee.models.address import XBee64BitAddress
from digi.xbee.reader import XBeeMessage
import time
import os 
from datetime import *
from tkcalendar import Calendar
import sqlite3

os.system('sudo chmod 777 /dev/ttyUSB0')

coordenador = XBeeDevice('/dev/ttyUSB0', 9600)    
router1 = RemoteXBeeDevice(coordenador, XBee64BitAddress.from_hex_string("0013A200409BAF15"))
router2 = RemoteXBeeDevice(coordenador, XBee64BitAddress.from_hex_string("0013A200409BAF12"))

print('Done')
try:
    coordenador.open()
        
except:
    print('\n\nERRO NA COMUNICAÇÃO!\n\n')
    exit()

DATABASE_EXISTS = False

if (os.path.isfile('agendamento.db') == False):
    DATABASE_EXISTS = False
else:
    DATABASE_EXISTS = True

conn = sqlite3.connect('agendamento.db')
c = conn.cursor()

if not DATABASE_EXISTS:
    c.execute('''CREATE TABLE schedule(date text, time text, device text, action text)''')
    conn.commit()
    conn.close()

def controlRele(device, data):
    req = tkinter.messagebox.askquestion(f"Transmit Request", f'Quer proceder ao envio do pedido {data} para o {device}?')
    
    if req == 'yes':
        try:
            coordenador.send_data(device, data)
        except:
            tkinter.messagebox.askokcancel("Transmit Status", "Problema com a transmissão do pedido!")

def introDataBase(data_s, hora_s, dev_s, act_s):
    conn = sqlite3.connect('agendamento.db')
    c = conn.cursor()
    c.execute('INSERT INTO schedule (date, time, device, action) VALUES (?, ?, ?, ?)', (data_s, hora_s, dev_s, act_s))
    conn.commit()
    conn.close()
    tkinter.messagebox.askokcancel("Agendamento de Ação", f"Foi agendado para {data_s} às {hora_s}: {act_s} {dev_s}!")

def checkDataBase():
    conn = sqlite3.connect('agendamento.db')
    c = conn.cursor()

    c.execute('SELECT *, oid FROM schedule')
    sch = c.fetchall()


    data = date.today()
    data = str(data)
    print(data)
    hora = datetime.now()
    hora = str(hora.hour) + ':' + str(hora.minute)
    print(hora)

    for A in sch:
        if A[0] == data:
            if A[1] ==  hora:
                if A[2] == 'Router 1':
                    if A[3] == 'Ligar':
                        coordenador.send_data(router1, 'L')
                    elif A[3] == 'Desligar':
                        coordenador.send_data(router1, 'D')
                    c.execute(f'DELETE FROM schedule WHERE oid = {A[4]}')
                elif A[2] == 'Router 2':
                    if A[3] == 'Ligar':
                        coordenador.send_data(router2, 'L')
                    elif A[3] == 'Desligar':
                        coordenador.send_data(router2, 'D')
                    c.execute(f'DELETE FROM schedule WHERE oid = {A[4]}')
                elif A[2] == 'Ambos':
                    if A[3] == 'Ligar':
                        coordenador.send_data_broadcast('L')
                    elif A[3] == 'Desligar':
                        coordenador.send_data_broadcast('D')
                    c.execute(f'DELETE FROM schedule WHERE oid = {A[4]}')

    conn.commit()
    conn.close()
    app.after(30000, checkDataBase)

def controlAll(data):
    req = tkinter.messagebox.askquestion(f"Transmit Request", f'Quer proceder ao envio do pedido {data} para todos os dispositivos?')

    if req == 'yes':
        try:
            coordenador.send_data_broadcast(data)
        except:
            tkinter.messagebox.askokcancel("Problema com a transmissão do pedido...")

def checkTemp(device, data):
    req = tkinter.messagebox.askquestion(f"Transmit Request", f'Quer proceder ao envio do pedido {data} para o {device}?')
    message = None
    if req == 'yes':
        try:
            coordenador.send_data(device, data)
        except:
            tkinter.messagebox.askokcancel('Transmit Request', "Problema com a transmissão do pedido!")

        while message == None:
            message = coordenador.read_data()

        temper = bytes(message.data)
        temper = int.from_bytes(temper, byteorder='big')
        print(temper)
        
        if device == router1:
            ControlPage.updateLabel1(ControlPage, temper)
        elif device == router2:
            ControlPage.updateLabel2(ControlPage, temper)

def closeProg():
    coordenador.close()
    app.destroy()

class LAMEC(Tk):
    def __init__(self, *args, **kwargs):
        Tk.__init__(self, *args, **kwargs)
        container = Frame(self)

        container.pack(side='top', fill='both', expand=True)

        self.frames = {}

        for F in (ControlPage, SchedulePage):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky='nsew')
        
        self.show_frame(ControlPage)

    def show_frame(self, cont):

        frame = self.frames[cont]
        frame.tkraise()

class ControlPage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        router1_on = Button(self, text='Ligar Router1', command= lambda: controlRele(router1, 'L'))
        router1_on.grid(row=0, column=0)
        #router1_on.pack()

        router1_off = Button(self, text='Desligar Router1',  command= lambda: controlRele(router1, 'D'))
        router1_off.grid(row=0, column=1)
        #router1_off.pack()

        router1_temp = Button(self, text='Verificar Temperatura', command= lambda: checkTemp(router1, 'T'))
        router1_temp.grid(row=0, column= 3)
        #router1_temp.pack()

        ControlPage.temp1Label = Label(self, text='')
        ControlPage.temp1Label.grid(row=0, column=4)
        #ControlPage.temp1Label.pack()

        router2_on = Button(self, text='Ligar Router2',  command= lambda: controlRele(router2, 'L'))
        router2_on.grid(row=1, column=0)
        #router2_on.pack()

        router2_off = Button(self, text='Desligar Router2',  command= lambda: controlRele(router2, 'D'))
        router2_off.grid(row=1, column=1)
        #router2_off.pack()

        router2_temp = Button(self, text='Verificar Temperatura', command= lambda: checkTemp(router2, 'T'))
        router2_temp.grid(row=1, column= 3)
        #router2_temp.pack()

        ControlPage.temp2Label = Label(self, text='')
        ControlPage.temp2Label.grid(row=1, column=4)
        #ControlPage.temp2Label.pack()

        all_on = Button(self, text='Ligar Tudo!', command = lambda:controlAll('L'))
        all_on.grid(row=2,column=0)
        #all_on.pack()

        all_off = Button(self, text='Desligar Tudo!', command = lambda:controlAll('D'))
        all_off.grid(row=2,column=1)
        #all_off.pack()

        agendButton = Button(self, text='Agendar Ações', command=lambda: controller.show_frame(SchedulePage))
        agendButton.grid(row = 3, column = 0)
        #agendButton.pack()

        quitButton = Button(self, text='Sair do Programa', command=closeProg)
        quitButton.grid(row=3, column=1)
        #quitButton.pack()
    
    def updateLabel1(self, temp):
        ControlPage.temp1Label['text'] = str(temp) + 'ºC'

    def updateLabel2(self, temp):
        ControlPage.temp2Label['text'] = str(temp) + 'ºC'

class SchedulePage(Frame):
    def __init__(self, parent, controller):
        Frame.__init__(self, parent)
        
        calendarButton = Button(self, text = 'Calendário', command=self.calendario)
        calendarButton.pack()
        
        SchedulePage.dataLabel = Label(self, text='')
        SchedulePage.dataLabel.pack()

        SchedulePage.hourstr=StringVar(self,'10')
        SchedulePage.hour = Spinbox(self,from_=0,to=23,wrap=True,textvariable=self.hourstr,width=2)
        SchedulePage.minstr= StringVar(self,'30')
        SchedulePage.min = Spinbox(self,from_=0,to=59,wrap=True,textvariable=self.minstr,width=2)
        SchedulePage.hour.pack()
        SchedulePage.min.pack()

        choicesD = ['Router 1', 'Router 2', 'Ambos']
        SchedulePage.dispositivo = StringVar(self)
        SchedulePage.dispositivo.set('Router 1')

        mD = OptionMenu(self, SchedulePage.dispositivo, *choicesD)
        mD.pack()
        
        choicesA = ['Ligar', 'Desligar']
        SchedulePage.acao = StringVar(self)
        SchedulePage.acao.set('Ligar')

        mA = OptionMenu(self, SchedulePage.acao, *choicesA)
        mA.pack()

        agendarButton = Button(self, text='Agendar', command = lambda: SchedulePage.updateDB(SchedulePage))
        agendarButton.pack()
        controlButton = Button(self, text='Página de Controlo', command=lambda: controller.show_frame(ControlPage))
        controlButton.pack()

        quitButton1 = Button(self, text='Sair do Programa', command=closeProg)
        quitButton1.pack()
        
    def updateDB(self):
        hs = str(SchedulePage.hour.get())
        ms = str(SchedulePage.min.get())
        H= hs + ':' + ms
        d = str(SchedulePage.dispositivo.get())
        a = str(SchedulePage.acao.get())

        introDataBase(SchedulePage.DATA, H, d, a)

    def calendario(self):
        def selectData():
            SchedulePage.DATA = cal.selection_get()
            SchedulePage.DATA = str(SchedulePage.DATA)
            SchedulePage.dataLabel['text'] = 'Data: ' + SchedulePage.DATA
            top.destroy()
        
        top = Toplevel(self)
        data = datetime.now()
        cal = Calendar(top,selectmode='day', cursor="hand1", year=data.year, month=data.month, day=data.day)
        cal.pack()

        dataButton = Button(top, text='OK', command = selectData)
        dataButton.pack()

app = LAMEC()
app.after(30000, checkDataBase)
app.mainloop()
