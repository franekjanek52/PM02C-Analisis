#======================= Biblioteki ==========================#

import re
import serial
import numpy as np
import pandas as pd
import PySimpleGUI as sg
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, FigureCanvasAgg
from scipy.interpolate import CubicSpline
from scipy.ndimage import gaussian_filter

#========================== Dane =============================#

df = pd.DataFrame()     # Pandas Dataframe
Dane = {
    'Blok': [],#"[Blok 1] Ra=00",
    'Parametry_0': ['N/A','n/a',1,1,0,0,1,1,0,'n/a'], # 0:głowica, 1:TYP, 2:LPOM, 3:AD_MAX, 4:AD_MIN, 5:AD_POL, 6:Z, 7:L, 8:V, 9:FILTR, 10:DANE,
    'DaneADC_0': [0],
    'Dane_um_0': [0],
    'Parametry_prof_0': [], #0:Ra,1:Rz,2:Rm
}
Kolory = {
    "linia": 'yellow'
}

#========================= Funkcje ===========================#

def open_file():                          #Do naprawy!!!
    try:
        df = pd.read_csv(values["-FILE-"])
        #data2D = df['Wartosc ADC'].to_numpy(dtype=int)
        #data_um = df['wartosc um'].to_numpy(dtype=int)
        
        window['-ML-'].print(df)
       # create_plot(ax, np.linspace(0, Parametry['L'], len(dane_um)), dane_um, Kolory['linia'])
        update_figure(figure_canvas_agg)
    except:
        print('nie udało się otworzyć') 
def data_from_com(recived,number):        # Stwórz dane z otrzymanych informacji za pomocą REGEX
    Parametry = {   
        'GLOWICA': "N/A",
        'TYP': "N/A",
        'LPOM': 0,
        'AD_MAX': 0,
        'AD_MIN': 0,
        'AD_POL': 0,
        'Z': 0,
        'L': 0,
        'v': "N/A",
        'FILTR': "N/A",
        'DANE': "N/A",
    }
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
        Dane[Parametry] = Parametry['GLOWICA'] = recived[schGlow.end():schTYP.start()]
        window['-ML-'].print("Glowica:",Parametry['GLOWICA'])
    except:
        print("brak danych o glowicy")
    try:    #przypisanie TYPU danych
        Parametry['TYP'] = recived[schTYP.end():schLPOM.start()]
        window['-ML-'].print("TYP:",Parametry['TYP'])
    except:
        print("brak danych o TYPIE")
    try:    #przypisanie Liczby Pomiarów 
        
        Parametry['LPOM'] = int(recived[schLPOM.end():schAD_MAX.start()])
        window['-ML-'].print("Liczba Poliarow:",Parametry['LPOM'])
    except:
        print("brak danych o Ilosci Pomiarow")
    try:    #przypisanie max wartosci Z ADC
        Parametry['AD_MAX'] = int(recived[schAD_MAX.end():schAD_MIN.start()])
        window['-ML-'].print("MAX wartosc ADC:",Parametry['AD_MAX']) 
    except:
        print("brak danych o MAX wartosci z ADC")
    try:    #przypisanie MIN wartości z ADC
        Parametry['AD_MIN'] = int(recived[schAD_MIN.end():schAD_POL.start()])
        window['-ML-'].print("MIN wartosc ADC:",Parametry['AD_MIN'])
    except:
        print("brak danych o MIN wartosci z ADC ")
    try:    #przypisanie wartośći odwrócenia znaku (ZERA) 
        Parametry['AD_POL'] = int(recived[schAD_POL.end():schZ.start()])
        window['-ML-'].print("polorzenie 'ZERA':",Parametry['AD_POL'])
    except:
        print("brak danych o polozeniu 'ZERA'")
    try:    #przypisanie Zakresu Pomiaru
        Parametry['Z'] = recived[schZ.end():schL.start()]
        Parametry['Z'] = int(re.sub(r'[ umM/s\n]', "", Parametry['Z']))
        window['-ML-'].print("Zakres:",Parametry['Z'],"um")
    except:
        print("brak danych o Zakresie Pomiaru")
    try:    #przypisanie Długości odcinka pomiarowego
        Parametry['L'] = recived[schL.end():schv.start()]
        Parametry['L'] = float(re.sub(r'[ umM/s\n]',"",Parametry['L']))
        window['-ML-'].print("Dlugosc odcinka pomiarowego:",Parametry['L'],"mm")
    except:
        print("brak danych o Odcinku Pomiarowym ")
    try:    #przypisanie Prędkośći Przesuwu
        Parametry['v'] = recived[schv.end():schFILTR.start()]
        Parametry['v'] = float(re.sub(r'[ umM/s\n]',"",Parametry['v']))
        window['-ML-'].print("Predkosc przesuwu:",Parametry['v'],"mm/s")
    except:
        print("brak danych o Predkosci przesuwu")
    try:    #przypisanie wartośći Filtra falistości
        Parametry['FILTR'] = recived[schFILTR.end():schDANE.start()]
        Parametry['FILTR'] = float(re.sub(r'[ umM/s]',"",Parametry['FILTR']))
        window['-ML-'].print("FILTR:",Parametry['FILTR'],"mm")
    except:
        print("brak danych o zastosowanym Filtrze")
    try:    #przypisanie osi Danych? 
        Parametry['DANE'] = recived[schDANE.end():schDANE.end()+2]
        window['-ML-'].print("Dane:",Parametry['DANE'])
    except:
        print("brak danych o osi? Danych")
    try:    #stwórz listy danych
        keyParametry = f'Parametry_{number}'
        keyADC = f'DaneADC_{number}'
        array = recived[schDANE.end()+2:].split()
        array.pop() #usuń ostatnią komurke(symbol końca przesyłu danych) z listy
        Dane[keyADC] = np.array(array, int)
        #print(Dane[keyADC])
        Dane[keyParametry] = [Parametry['GLOWICA'],Parametry['TYP'],Parametry['LPOM'],Parametry['AD_MAX'],Parametry['AD_MIN'],Parametry['AD_POL'],Parametry['Z'],
                              Parametry['L'],Parametry['v'],Parametry['FILTR'],Parametry['DANE']]
        # 0:głowica, 1:TYP, 2:LPOM, 3:AD_MAX, 4:AD_MIN, 5:AD_POL, 6:Z, 7:L, 8:V, 9:FILTR, 10:DANE,
    except:
        print("nie mozna utworzyc listy danych")
def plot_theme(motyw):                    # Motyw rysowania 
    mpl.rcParams['figure.figsize'] = 6.5, 4
    match motyw:
        case 'jasny':
            Kolory['linia'] = 'black'
            try:
                ax.set_facecolor('white')
                fig.set_facecolor('white')
            except:
                print('')
            #mpl.rcParams['figure.dpi'] = '1'
            mpl.rcParams['xtick.direction'] = 'in'
            mpl.rcParams['ytick.direction'] = 'in'
            #mpl.rcParams['axes.xmargin'] = 0.25
            mpl.rcParams['axes.ymargin'] = 0.2
            mpl.rcParams['xtick.minor.pad'] = 5 #-15   
            mpl.rcParams['ytick.minor.pad'] = 5 #-30
            mpl.rcParams['xtick.major.pad'] = 5 #-15
            mpl.rcParams['ytick.major.pad'] = 5 #-30
            mpl.rcParams['axes.facecolor'] = 'white'
            mpl.rcParams['axes.labelcolor'] = 'black'
            mpl.rcParams['axes.edgecolor'] = 'black'
            mpl.rcParams['figure.facecolor'] = 'white' #'#232e3d'
            mpl.rcParams['xtick.color'] = 'black'
            mpl.rcParams['xtick.labelcolor'] = 'black'
            mpl.rcParams['ytick.color'] = 'black'
            mpl.rcParams['ytick.labelcolor'] = 'black'
            mpl.rcParams['axes.titlecolor'] = 'black'
            mpl.rcParams['grid.color'] = 'black'
        case 'ciemny':
            Kolory['linia'] = 'yellow'
            try:
                ax.set_facecolor('black')
                fig.set_facecolor('black')
            except:
                print('')
            #mpl.rcParams['figure.dpi'] = '1'
            mpl.rcParams['xtick.direction'] = 'in'
            mpl.rcParams['ytick.direction'] = 'in'
            #mpl.rcParams['axes.xmargin'] = 0.25
            mpl.rcParams['axes.ymargin'] = 0.2
            mpl.rcParams['xtick.minor.pad'] = 5 #-15   
            mpl.rcParams['ytick.minor.pad'] = 5 #-30
            mpl.rcParams['xtick.major.pad'] = 5 #-15
            mpl.rcParams['ytick.major.pad'] = 5 #-30
            mpl.rcParams['axes.facecolor'] = 'black'
            mpl.rcParams['axes.labelcolor'] = '#424242'
            mpl.rcParams['axes.edgecolor'] = '#424242'
            mpl.rcParams['figure.facecolor'] = 'black' #'#232e3d'
            mpl.rcParams['xtick.color'] = '#424242'
            mpl.rcParams['xtick.labelcolor'] = 'yellow'
            mpl.rcParams['ytick.color'] = '#424242'
            mpl.rcParams['ytick.labelcolor'] = 'yellow'
            mpl.rcParams['axes.titlecolor'] = 'white'
            mpl.rcParams['grid.color'] = '#424242'
def create_plot(ax, xdata, ydata, color): # Funkcja rysująca wykres 
    ax.clear()
    ax.plot(xdata, ydata, color=color) #rysowanie lini
    minimum = min(ydata)
    ax.fill_between(xdata, ydata, minimum, color=color, alpha=0.15)
    ax.set_title('profil zmierzony')
    ax.set_xlabel('Odcinek pomiarowy [mm]', fontsize = 10)
    ax.set_ylabel('Wysokość profilu [um]', fontsize = 10)
    ax.grid(True, linestyle='--')
    ax.minorticks_on()

    return plt.gcf()
def draw_figure(canvas,figure):           #
    Figure_Canvas_Agg = FigureCanvasTkAgg(figure, canvas)
    Figure_Canvas_Agg.draw()
    Figure_Canvas_Agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return Figure_Canvas_Agg
def update_figure(figure_canvas_agg):     #
    Figure_Canvas_Agg.draw()
    Figure_Canvas_Agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return Figure_Canvas_Agg
def plot_update(index):                   #
    keyParametry = f'Parametry_{index}'
    key_um = f'Dane_um__{index}'
    try:
        parametry= Dane.get(keyParametry,[0])# 0:głowica, 1:TYP, 2:LPOM, 3:AD_MAX, 4:AD_MIN, 5:AD_POL, 6:Z, 7:L, 8:V, 9:FILTR, 10:DANE,
        window['-FILTR-'].Update(value=parametry[9])
        window['-DANE_Z-'].Update(value=parametry[6])
        window['-DANE_L-'].Update(value=parametry[7])
        window['-LPOM-'].Update(value=parametry[2])
        window['-GLOWICA-'].Update(value=parametry[0])
        window['-TYP-'].Update(value=parametry[1])
        window['-AD_MAX-'].Update(value=parametry[3])
        window['-AD_POL-'].Update(value=parametry[5])
        window['-DANE_V-'].Update(value=parametry[8])
        create_plot(ax, np.linspace(0, parametry[7], len(Dane[key_um])), Dane[key_um], Kolory['linia'])
    except:
        print('no data')
    update_figure(figure_canvas_agg)
def Export_figure(path, transparency):    #
    plt.savefig(path, transparent=transparency,)
    print('zapisano')
def interpolate(data,x):                  #
    
    original_points = np.arange(len(data)) # Original number of points
    new_points = np.linspace(0, len(data) - 1, x * len(data)) # New number of points x times
    cs = CubicSpline(original_points, data) # Cubic spline interpolation
    interpolated_data = cs(new_points)
    return interpolated_data
def cutoff_filter(data,lambdaC):          #

    # Define the cutoff wavelength lambdaC (in the same units as the data points' spacing)
    #lambdaC = 0.8  # Adjust this value as needed
    #sigma = lambdaC / np.sqrt(2 * np.pi)  # Calculate sigma based on lambdaC
    wc=lambdaC/0.5 #cutofffrequency = (mm)/(mm/s)
    sigma = np.sqrt(2*np.log(2)) / 2*np.pi*wc
    filtered_data = gaussian_filter(data, sigma=sigma) # Apply Gaussian lowpass filter
    return (filtered_data)
def oblicz_dane(number):                  #
    key_um = f'Dane_um__{number}'
    key = f'Parametry_{number}'
    key2 = f'DaneADC_{number}'
    value = Dane.get(key, [0]) # 0:głowica, 1:TYP, 2:LPOM, 3:AD_MAX, 4:AD_MIN, 5:AD_POL, 6:Z, 7:L, 8:V, 9:FILTR, 10:DANE,
    print(value)
    zakres_ADC = value[3] - value[4]
    try:
        res = value[6]/zakres_ADC  #określ rozdzielczość ADC w um
        print('rozdzielczosc ',res)
    except:
        res = 1
    dane = Dane.get(key2,0) - value[5]         #ustalenie zera
    dane_um = dane * res           #wartośći razy rozdzielczość
    dane_um = np.round(dane_um, 3) #zaokrąglanie wyniku
    Dane[key_um] = dane_um
    return dane_um    
def oblicz_para(number):                  #
    key_um = f'Dane_um__{number}'
    keyParametry_prof = f'Parametry_Prof_{number}'
    dane_um = Dane[key_um]
    Ra1 = np.mean(np.abs(dane_um))
    print('Ra=',Ra1)

    num_extremes = 5
    sorted_data = np.sort(dane_um)
    highest_peaks = sorted_data[-num_extremes:]
    lowest_valleys = sorted_data[:num_extremes]
    Rz = (np.sum(np.abs(highest_peaks)) + np.sum(np.abs(lowest_valleys)))/num_extremes
    print('Rz=',Rz)

    props = dict(boxstyle='round', facecolor='yellow', alpha=0.3)
    textstr = 'Ra',Ra1,'Rz',Rz,'Rsm'
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=14,
        verticalalignment='top', bbox=props)
    update_figure(figure_canvas_agg)
    Dane[keyParametry_prof]=[Ra1,Rz,]
    print(Dane[keyParametry_prof])
    return(True)
def add_to_list(number):                  #
    Blok = Dane['Blok']
    match values['-NBLOK-']:
     case 'Nowy Blok':
         Dane['Blok'] = Blok + [f"[Blok {number}] Ra={1}"]
     case 'Wybrany Blok':
         Blok[number] = [f"[Blok {number}] Ra={1}"]
         Dane['Blok'] = Blok  
    window['-LIST-'].Update(Dane['Blok'])
def save_to_df(number):                   #
    keyADC = f'DaneADC_{number}'
    key_um = f'Dane_um__{number}'
    df[keyADC] = Dane[keyADC].tolist()
    df[key_um] = Dane[key_um].tolist()
    window['-ML-'].print(df)
     
#======================== Układ okna =========================#

sg.theme('Dark Amber')  # Motyw Okna
datatab1_layout = [     # Zakładka danych RS232
    [sg.Text("Wprowadzanie danych:")],
    [
    sg.Radio('PC',group_id='tryb',default=True),
    sg.Radio('Drukarka',group_id='tryb',disabled=True),
    ],
    [sg.Frame('Dane', font='Any 15', layout=[
        [sg.Multiline(key='-ML-', write_only=True, size=(48,15))]])
    ],
  #  [sg.Frame('Terminal', font='Any 15', layout=[
  #      [sg.Output(size=(40, 4), font='Courier 10')]])],
   
]
datatab2_layout = [     # Zakładka danych parametrów pomiaru
    [sg.Text("Parametry pomiaru:")],
    [sg.Checkbox(' interpolacja Cubic Spline', key='-ITERPOLATE-')],
    [sg.Checkbox(' Filtr falistosci [mm]', key='-CHKFILTR-', enable_events=True,),sg.Push(),sg.Combo([0.25,0.8,2.5], key='-FILTR-', size=(19,1), enable_events=True, )],
    [sg.Text("Zakres pomiarowy [um]"),sg.Push(),sg.Combo([250, 100, 50, 25],key='-DANE_Z-', size=(19,1))],
    [sg.Text("Odcinek pomiarowy [mm]"),sg.Push(),sg.Combo([0.4, 1.25, 4.0, 12.5],key='-DANE_L-', size=(19,1))],
    [sg.Text("predkosc przesuwu"),sg.Push(),sg.Combo(['0.5mm/s'],key='-DANE_V-', size=(19,1), readonly=True, disabled=True)],
    [sg.Text("GLOWICA"),sg.Push(),sg.Combo(['1d','2d'],key='-GLOWICA-', size=(19,1), readonly=True, disabled=True)],
    [sg.Text("Liczba punktów pomiarowych"),sg.Push(),sg.Combo([''],key='-LPOM-', size=(19,1), readonly=True, disabled=True)],
    [sg.Text("zakres ADC"),sg.Push(),sg.Combo(['1d','2d'],key='-AD_MAX-', size=(19,1), readonly=True, disabled=True)],
    [sg.Text("ZERO_ADC"),sg.Push(),sg.Combo(['1d','2d'],key='-AD_POL-', size=(19,1), readonly=True, disabled=True)],
    [sg.Text("TYP"),sg.Push(),sg.Combo(['1d','2d'],key='-TYP-', size=(19,1), readonly=True, disabled=True)],

]
datatab3_layout = [     # Zakładka danych liczbowych
    [sg.Text("pomiary")],
    [sg.Push(),sg.Table([["", "ABC", "DEF"], ["GHI", "JKL", "MNO"], ["PQRS", "TUV", "WXYZ"]], headings=["1, 4, 7", "2, 5, 8", "3, 6, 9","1","2"]
                        , auto_size_columns=False, size=(40,20),justification='center',)]
]
tab1_layout = [         # zakładka edycji rysunku
    [sg.Text('Tab 1')],
    
]
tab2_layout = [         # zakładka eksportowania rysunku
    [sg.Text('Ustawiena eksportowania rysunku:')],
    [sg.Checkbox('przezroczystosc',key='-CHKTRANSPARENT-'),
     #sg.Text('format pliku'),sg.Combo(['svg','pdf','png','jpg','webp'], key='-FORMAT-', tooltip='wybierz lub wpisz'),
     sg.Push(),sg.Text('sciezka'), sg.Input(key='-EXFIGPATH-', size=(30, 1)),
        sg.FileSaveAs(button_text=("wybierz"),file_types=(('PDF','.pdf'),('SVG','.svg'),('PNG',',png'),('JPG','.jpg'),('WEBP','.webp'),('ALL Files', '. *'))),
    sg.Button('Eksportuj',key='-EXPRYS-',size=(10,1))
    ],    
]
datatab_group_layout = [# Layout zakładek wprowadzania danych
    [
        sg.Tab('Parametry',datatab2_layout, key='DTAB2-'),
        sg.Tab('Serie', datatab3_layout, key='-DTAB3-'),
        sg.Tab('RS232', datatab1_layout, key='-DTAB1-'),
        
    ]
]
tab_group_layout = [    # Layout zakładek własciwośći rysunku
    [
    sg.Tab('parametry rysunku', tab1_layout, key='-TAB1-'),
    sg.Tab('export rysunku', tab2_layout, visible=True, key='-TAB2-'),
    ]
]
Input_column = [        # Kolumna wprowadzania danych
    [sg.TabGroup(datatab_group_layout, enable_events=True, key='-DTABGROUP-')],
     [sg.Text('Plik .CSV'), sg.Input(key='-FILE-', size=(30, 1)),
        sg.FileBrowse(button_text=("wybierz"),file_types=(("plik arkusza", "*.csv"),))],   
]
List_column = [         #
[sg.Text('Lista pomiarów')],
[sg.Listbox(Dane['Blok'], size=(16, 24),key='-LIST-')],
[sg.Text('motyw \nrysunku'),sg.Combo(['ciemny','jasny'],default_value='ciemny', key='-MOTYW_RYS-', enable_events=True)],
]
Data_column = [         # Kolumna analizy danych
    [sg.Canvas(background_color='Grey6', size=(460,360), key='-CANVAS-' )],
    [sg.TabGroup(tab_group_layout, enable_events=True, key='-TABGROUP-')],            
]
Button_column = [       # Layout kolumny przycisków
    [sg.Text("ODBIÓR DANYCH")],
    [sg.Combo(['Nowy Blok','Wybrany Blok'],default_value='Nowy Blok',key= '-NBLOK-',size=(12,1),enable_events=False)],
    [sg.Button('START', button_color=('black', 'olivedrab3'), key='-START-', size=(8,3))],
    [sg.Button('STOP', button_color=('white', 'firebrick2'), key='-STOP-', size=(8,3))],
    [sg.VPush()],
    [sg.HorizontalSeparator()],
    [sg.VPush()],
    [sg.Button('ZAPISZ', button_color=('black', 'springgreen'), key='-SAVE-', size=(8,3))],
    [sg.Button('OTWÓRZ', button_color=('black', 'Steelblue1'), key='-OPEN-', size=(8,3))],
    [sg.Button('RYSUJ', button_color=('black', 'CadetBlue2'), key='-PLOT-', size=(8,3))],
    [sg.Button('test', button_color=('white', 'firebrick2'), key='-RESET-', size=(8,3))],
]
layout = [              # Główny layout
   [
    sg.Column(Input_column),
    sg.VSeparator(),
    sg.Column(List_column),                
    sg.Column(Data_column),
    sg.VSeparator(),
    sg.Column(Button_column),
            
  ]
]
window = sg.Window("PM02C Analizator profilu", layout, finalize=True, resizable=False, margins=(15, 15,))
 
#=================== Parametry rysowania =====================#

plot_theme('ciemny')                    # globalna zmiana wyglądu rysunków
fig, ax = plt.subplots()                #
create_plot(ax,[0],[0],Kolory['linia']) # Dane początkowe
figure_canvas_agg = draw_figure(window['-CANVAS-'].TKCanvas, fig)

#=============== Ustawienie portu szeregowego ================#

try:
        x = serial.Serial("/dev/ttyUSB0", 4800, timeout=0.1)
        x.close()
except:
    print("Brak portu /dev/ttyUSB0")
    x = serial.Serial()

#======================= Główna pętla ========================#

number = 0
activity = False
while True :
    event,values = window.read(timeout=100) # Wywołanie okna i odczyt stanu (blokujące!!)
    match event:                            # Przypisanie funkcji do przycisków
        case sg.WIN_CLOSED:   #wyjdź z pętli aby zamknąć okno
            break
        case 'Exit':
            break 
        case '-START-':

            try:
                 x.open()
                 print("Port otwarty")
            except:
                print("Nie mozna otworzyc")  
        case '-STOP-':
            x.close()
            print("Port Zamkniety")
        case '-OPEN-':
            try:
                open_file()
            except:
                print('nie udało się otworzyć')     
        case '-SAVE-':
            df.to_csv("Pomiary.csv", index=False)
            print("Zapisano jako Pomiary.csv")
        case '-EXPRYS-':
            Export_figure(values['-EXFIGPATH-'],values['-CHKTRANSPARENT-'])
        case '-RESET-':
             Blok = Dane['Blok']
             match values['-NBLOK-']:
                case 'Nowy Blok':
                    Dane['Blok'] = Blok + [f"[Blok {number}] Ra={1}"]
                case 'Wybrany Blok':
                    Blok[number] = f"[Blok {number}] Ra={2}"
                    Dane['Blok'] = Blok  
             window['-LIST-'].Update(Dane['Blok'])
        case '-MOTYW_RYS-':
            plot_theme(values['-MOTYW_RYS-'])
            plot_update(number)                   
        case '-PLOT-':
            plot_update(number)       
        case '-CHKFILTR-':
            print('hello')
        case '-LICZ-':
            print('hello')
    if x.isOpen() == True:                  # Odczyt danych z portu szeregowego
        recived = ""
        array = []
        activity = False
        window['-ML-'].print("czekam na dane",text_color='olivedrab3') 
        while x.isOpen() == True : #odczyt danych z portu szeregowego
            if event == sg.WIN_CLOSED:  #sprawdz czy okno nie zostało zamknięte
                break  
            data = str(x.readline().decode('latin-1')).rstrip()
            if data != '':
                if activity == False: #wiadomiśc o odbiorze danych
                    window['-ML-'].print("Odbieram dane",text_color='cyan3')
                activity = True
                recived += " "
                recived += data
            if activity== True and data == '' :
                x.close()
                window['-ML-'].print("Dane odebrane", text_color='springgreen')
                print("Port zamkniety")
            else:
                event, values = window.read(timeout=300)
            if event == '-STOP-':
                x.close()
                print("Port zamkniety")      
    if activity == True:                    # Przetwarzanie odczytanych danych
        match values['-NBLOK-']: #zmina indeksu
            case 'Nowy Blok':
                number = len(Dane['Blok'])
                number = number + 1
                print(number)
            case 'Wybrany Blok':
                print(':3')
        data_from_com(recived,number)
        oblicz_dane(number)
        oblicz_para(number)
        plot_update(number)
        save_to_df(number)
        add_to_list(number)

        activity = False 
       
window.close()  # Poza główną pętlą = zamknij okno
'''
dodać informacje o poprawnosci przyjętych danych w oknie terminal: zgodnosc dlugosci
jeden przycisk zamiast start stop
opcja włączenia ciągłego odbierania danych
poprawic otwieranie danych

keys:
-CANVAS-
-ML-
-START-
-STOP-
-SAVE-
-OPEN-
-PLOT-
-RESET-
-LICZ-
-MOTYW_RYS-
-FORMAT-
-CHKFILTR-
-FILTR-
-DANE_Z-
-DANE_L-
-DANE_V-
-GLOWICA-
-LPOM-
-AD_MAX-
-AD_POL-
-TYP-
-DTAB1-
-DTAB2-
-DTAB3-
-FILE-
-EXPRYS-
-EXFIGPATH-
-CHKTRANSPARENT-
-INTERPOLATE-
-LIST-
-NBLOK-
'''
