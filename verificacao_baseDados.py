import os
from datetime import *
import sqlite3
import time

conn = sqlite3.connect('agendamento.db')
c = conn.cursor()

#c.execute('DELETE FROM schedule WHERE oid=1')
#c.execute('DELETE FROM schedule WHERE oid=2')
#c.execute('DELETE FROM schedule WHERE oid=3')

conn.commit()
conn.close()

while 1:
    conn = sqlite3.connect('agendamento.db')
    c = conn.cursor()
    c.execute('SELECT *, oid FROM schedule')
    sch = c.fetchall()

    data = date.today()
    data = str(data)
    print('Data atual: ' + data)
    hora = datetime.now()
    hora = str(hora.hour) + ':' + str(hora.minute)
    print('Tempo atual: ' + hora)

    for A in sch:
        print(A)
        if A[0] == data:
            if A[1] ==  hora:
                print(f'Ação {A[3]} a realizar para {A[2]}.')

    conn.commit()
    conn.close()
    time.sleep(20)
