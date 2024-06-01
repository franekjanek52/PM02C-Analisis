import re
import csv
import serial
import numpy as np
import PySimpleGUI as sg
import matplotlib.pyplot as plt

#stwórz Okno
sg.theme('Dark Amber')
Input_column = [

     
    [sg.Text("Serial data control:")],
    [
    sg.Button('Start', button_color=('white', 'black'), key='start'),
    sg.Button('Stop', button_color=('white', 'black'), key='stop'),
    sg.Button('Submit', button_color=('white', 'springgreen4'), key='submit'),
    sg.Radio('Drukarka',group_id='tryb',disabled=True),
    sg.Radio('Komputer',group_id='tryb',default=True),
    ],
    [sg.Multiline(key='-MLIN-', write_only=True, size=(80,3))],
     [sg.Text("Data:")],
    [sg.Multiline(key='-ML-', write_only=True, size=(80,25))],
]
Data_column = [
     [sg.Text('plik arkusza'), sg.Input(key='-csvfile-', size=(45, 1)),
               sg.FileBrowse(button_text=("wybierz"),file_types=(("plik arkusza", "*.csv"),))],
              [sg.Frame('Output', font='Any 15', layout=[
                        [sg.Output(size=(65, 15), font='Courier 10')]])],
]
sButton_column = [
[sg.Button('Save', button_color=('black', 'springgreen'), key='save', size=(6,3))],
[sg.Button('PLOT', button_color=('black', 'CadetBlue2'), key='PLOT', size=(6,3))],
[sg.Button('Reset', button_color=('white', 'firebrick3'), key='reset', size=(6,3))],
]
layout = [
            [
            sg.Column(Input_column),
            sg.VSeparator(),
            sg.Column(sButton_column),
            sg.Column(Data_column), 
            
            ]
]
window = sg.Window("PM02C Analisis", layout, margins=(15, 15,)) 

com = "/dev/ttyUSB0" #wybór portu szeregowego
baud = 4800          #szybkość transmisji
try:
    x = serial.Serial(com, baud, timeout = 0.1)
    #x.close()
except: 
    print("Brak portu /dev/ttyUSB0")
    x = serial.Serial()
#event, values = window.read(timeout=100)
activity = False
Parametry = {
    "GLOWICA": "N/A",
    "TYP": "N/A",
    "LPOM": 0,
    "AD_MAX": 0,
    "AD_MIN": 0,
    "AD_POL": 0,
    "Z": "N/A",
    "L": "N/A",
    "v": "N/A",
    "FILTR": "N/A",
    "DANE": "N/A",

}

while True :
    event, values = window.read(timeout=100) #wywołanie okna i odczyt stanu (blokujące!!)
    match event:              #przypisanie funkcji do przycisków
        case sg.WIN_CLOSED:    #wyjdź z pętli abyzamknąć okno
            break
        case 'Exit':
            break 
        case 'start':
            try:
                 x.open()
                 window['-MLIN-'].print("Port otwarty")
            except:
                window['-MLIN-'].print("Nie mozna otworzyc")  
        case 'stop':
            x.close()
            window['-MLIN-'].print("Port Zamkniety")
        #case 'submit':     
        #case 'reset':  
        case 'save':
            with open('SensorData.csv', mode='w') as sensor_file:
             sensor_writer = csv.writer(sensor_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
             sensor_writer.writerow([data2D])
             window['-MLIN-'].print("Zapisano jako SensorData.csv")       
    if x.isOpen() == True:    #gotowść do odczyru danych
        recived = ""
        array = []
        activity = False
        window['-MLIN-'].print("czekam na dane",text_color='olivedrab3') 
    while x.isOpen() == True: #odczyt danych z portu szeregowego
        if event == sg.WIN_CLOSED:  #sprawdz czy okno nie zostało zamknięte
            break  
        data = str(x.readline().decode('latin-1')).rstrip()
        if data != '':
            activity = True
            recived += " "
            recived += data
            window['-MLIN-'].print("Odbieram dane",text_color='cyan3')
        if activity== True and data == '' :
            x.close()
            window['-MLIN-'].print("Dane odebrane", text_color='springgreen')
            window['-MLIN-'].print("Port zamkniety")
        else:
            event, values = window.read(timeout=300)
        if event == 'stop':
            x.close()
            window['-MLIN-'].print("Port zamkniety")      
    if activity == True:      #Przetwarzanie odczytanych danych
        schGlow = re.search( r' GLOWICA=', recived)
        schTYP = re.search( r' TYP=', recived)
        schLPOM = re.search( r' LPOM=', recived)
        schAD_MAX = re.search( r' AD_MAX=', recived)
        schAD_MIN = re.search( r' AD_MIN=', recived)
        schAD_POL = re.search( r' AD_POL=', recived)
        schZ = re.search( r' Z=', recived)
        schL = re.search( r' L=', recived)
        schv = re.search( r' v=', recived)
        schFILTR = re.search( r' FILTR=', recived)
        schDANE = re.search( r' DANE=', recived)
        

        try:    #przypisanie rodzaju głowicy
            Parametry['GLOWICA'] = recived[schGlow.end():schTYP.start()]
            print("Glowica:",Parametry['GLOWICA'])
        except:
            print("brak danych o glowicy")
        try:    #przypisanie TYPU danych
            Parametry['TYP'] = recived[schTYP.end():schLPOM.start()]
            print("TYP:",Parametry['TYP'])
        except:
            print("brak danych o TYPIE")
        try:    #przypisanie Liczby Pomiarów 
            Parametry['LPOM'] = int(recived[schLPOM.end():schAD_MAX.start()])
            print("Liczba Poliarow:",Parametry['LPOM'])
        except:
            print("brak danych o Ilosci Pomiarow")
        try:    #przypisanie max wartosci Z ADC
            Parametry['AD_MAX'] = int(recived[schAD_MAX.end():schAD_MIN.start()])
            print("MAX wartosc ADC:",Parametry['AD_MAX'])
        except:
            print("brak danych o MAX wartosci z ADC")
        try:    #przypisanie MIN wartości z ADC
            Parametry['AD_MIN'] = int(recived[schAD_MIN.end():schAD_POL.start()])
            print("MIN wartosc ADC:",Parametry['AD_MIN'])
        except:
            print("brak danych o MIN wartosci z ADC ")
        try:    #przypisanie wartośći odwrócenia znaku (ZERA) 
            Parametry['AD_POL'] = int(recived[schAD_POL.end():schZ.start()])
            print("polorzenie 'ZERA':",Parametry['AD_POL'])
        except:
            print("brak danych o polozeniu 'ZERA'")
        try:    #przypisanie Zakresu Pomiaru
            Parametry['Z'] = recived[schZ.end():schL.start()]
            Parametry['Z'] = int(re.sub(r'[ umM/s]', "", Parametry['Z']))
            print("Zakres:",Parametry['Z'],"um")
        except:
            print("brak danych o Zakresie Pomiaru")
        try:    #przypisanie Długości odcinka pomiarowego
            Parametry['L'] = recived[schL.end():schv.start()]
            Parametry['L'] = float(re.sub(r'[ umM/s]',"",Parametry['L']))
            print("Dlugosc odcinka pomiarowego:",Parametry['L'],"mm")
        except:
            print("brak danych o Odcinku Pomiarowym ")
        try:    #przypisanie Prędkośći Przesuwu
            Parametry['v'] = recived[schv.end():schFILTR.start()]
            Parametry['v'] = float(re.sub(r'[ umM/s]',"",Parametry['v']))
            print("Predkosc przesuwu:",Parametry['v'],"mm/s")
        except:
            print("brak danych o Predkosci przesuwu")
        try:    #przypisanie wartośći Filtra falistości
            Parametry['FILTR'] = recived[schFILTR.end():schDANE.start()]
            Parametry['FILTR'] = float(re.sub(r'[ umM/s]',"",Parametry['FILTR']))
            print("FILTR:",Parametry['FILTR'],"mm")
        except:
            print("brak danych o zastosowanym Filtrze")
        try:    #przypisanie osi Danych? 
            Parametry['DANE'] = recived[schDANE.end():schDANE.end()+2]
            print("Dane:",Parametry['DANE'])
        except:
            print("brak danych o osi? Danych")
        try:    #stwórz listę danych
           array = recived[schDANE.end()+2:].split()
           array.pop() #usuń ostatnią komurke(symbol końca przesyłu danych) z listy
           print("array: ",len(array))
           data2D = np.array(array, int)
           print("Data2D: ",len(data2D))
           window['-ML-'].print(data2D)
        except:
            print("nie mozna utworzyc listy danych")
        
        activity = False 
    if event == 'PLOT':       #rysuj zależnośći
        fig, axs = plt.subplots(1, 2,)
        ydata = data2D - Parametry['AD_POL']
        xdata = np.linspace(0, Parametry['L'], len(data2D))  
        axs[0].plot(xdata, ydata)
        axs[1].set_yscale('log')
        axs[1].plot(xdata, ydata)
        plt.show()
window.close() #poza główną pętlą = zamknij okno