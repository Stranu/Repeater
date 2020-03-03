import pickle
import pyautogui
import time
import random
import sys
import csv
import os

import PySimpleGUI as sg
from pynput import mouse, keyboard

"""from pynput.keyboard import Listener  as KeyboardListener
from pynput.mouse import Listener  as MouseListener"""
from pynput.keyboard import Key, Controller
import logging

EXPORTHEADER = ["TYPE", "VALUE", "BUTTON", "MOVE", "TIME"]

# logging.basicConfig(filename="log.txt", level=logging.DEBUG, format='%(message)s')
KEY_LIST = [str(Key.caps_lock), str(Key.caps_lock), str(Key.shift_l), str(Key.ctrl_l)]
KEY_STOP = [str(Key.caps_lock), str(Key.caps_lock), str(Key.caps_lock), str(Key.caps_lock)]
COMMANDLOG = []  # List of dictionary
RECMODE = False
PRECMODE = False
ENDREC = False
REPLAY = False
CICLI = 1
LOOP = False
key_count = 0
kController = keyboard.Controller()
mController = mouse.Controller()


def storeData(filename, entry, mode='a'):
    if not os.path.isfile(filename):
        mode = 'w'
    try:
        with open(filename, mode, newline='') as csvfile:
            content = csv.writer(csvfile, delimiter=';', quotechar='|')
            content.writerow(entry)
        return True
    except:
        return False


def retrieve(filename):
    if os.path.isfile(filename):
        temp_list = []
        with open(filename, newline='') as csvfile:
            content = csv.reader(csvfile, delimiter=';', quotechar='|')
            next(content)
            for row in content:
                temp_list.append(row)

            return temp_list
    else:
        print(f'\n!Il file -{filename}- non esiste!')
        return []


def on_release(key):
    global RECMODE
    global PRECMODE
    global ENDREC
    if PRECMODE:
        # Se la registrazione viene avviata da on_press, on_release registra l'ultimo rilascio
        RECMODE = True
        PRECMODE = False
    elif RECMODE:
        COMMANDLOG.append({"releasekey": key, "time": time.time()})
        print(f"Rilascio {key}")
        if ENDREC:
            RECMODE = False
            ENDREC = False
            del COMMANDLOG[-(len(KEY_STOP)) * 2::1]  # Rimuove gli ultimi valori della lista
            # repeater(CICLI, LOOP)


def on_press(key):
    global PRECMODE
    global ENDREC
    global REPLAY
    global key_count
    global KEY_LIST
    global COMMANDLOG

    if RECMODE:  # if recmode is active, it start registering keys and mouse movements
        # logging.info(str(key))
        COMMANDLOG.append({"key": key, "time": time.time()})
        print(f"Premo {key}")
        if str(key) == KEY_STOP[key_count]:  # if the user enter the right sequence of keys, it will stop the recording
            key_count -= 1
            if key_count < (-len(KEY_STOP)):
                key_count = 0
                ENDREC = True
                print("Registrazione terminata...")
                windowMain["fase"].update("REC Terminato")
        else:
            key_count = -1
    elif str(key) == KEY_LIST[key_count] and not REPLAY:
        # if the user press the right keys in the right sequence, the program start recording mouse and keys usage
        # print(f"YUP {key} {key_count}")
        key_count += 1
        if key_count >= len(KEY_LIST):
            key_count = -1
            COMMANDLOG = []
            PRECMODE = True
            print("Inizio a registrare...")
            windowMain["fase"].update("REC Attivo")
    elif str(key) == KEY_STOP[key_count] and not REPLAY:
        # if the user press the right keys in the right sequence, the program replay the cycle
        # print(f"YUP {key} {key_count}")
        key_count += 1
        if key_count >= len(KEY_LIST):
            key_count = 0
            REPLAY = True
            repeater(CICLI, LOOP)
    else:
        key_count = 0
    if REPLAY:
        if key == Key.esc:
            REPLAY = False


def on_move(x, y):  # Not in use.
    if RECMODE:
        # logging.info("Mouse moved to : {0}, {1}".format(x, y))
        if COMMANDLOG:
            x1 = COMMANDLOG[-1]["move"][0]
            y1 = COMMANDLOG[-1]["move"][1]
            if "move" in COMMANDLOG[-1]:
                if x1 == x:
                    COMMANDLOG[-1]["move"][1] = y
                elif y1 == y:
                    COMMANDLOG[-1]["move"][0] = x
                else:
                    COMMANDLOG.append({"move": [x, y]})
        else:
            COMMANDLOG.append({"move": [x, y]})
        print(f"List: {COMMANDLOG}")


def on_click(x, y, button, pressed):
    if RECMODE:
        # logging.info('Mouse clicked at : {0}, {1} : {2}'.format(x, y, button))
        COMMANDLOG.append({"click": True if pressed else False, "button": button, "move": [x, y], "time": time.time()})
        print(f"Command {COMMANDLOG[-1]}")


def on_scroll(x, y, dx, dy):
    if RECMODE:
        # logging.info('Mouse scrolled at : {0}, {1} : {2}, {3}'.format(x, y, dx, dy))
        if COMMANDLOG and "scroll" in COMMANDLOG[-1]:
            COMMANDLOG[-1]["scroll"][0] = dx + COMMANDLOG[-1]["scroll"][0]
            COMMANDLOG[-1]["scroll"][1] = dy + COMMANDLOG[-1]["scroll"][1]
        else:
            COMMANDLOG.append({"scroll": [dx, dy], "move": [x, y], "time": time.time()})
        print(f"Scrollo {dx}, {dy}")
        print(COMMANDLOG[-1])


def repeater(cicli=1, loop=False):
    """with open("answers.csv") as f:
        lineList = f.readlines()
    commandList = [line.strip() for line in lineList]
    for command in commandList:"""

    windowMain["fase"].update("REPLAY Attivo")
    try:
        windowWidget["cicliText"].update("RIPETO")
    except:
        print("non in widget mode")
    mListenerR = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
    klistenerR = keyboard.Listener(on_press=on_press, on_release=on_release)
    mListenerR.start()
    klistenerR.start()
    # Faccio ripartire i listener all'interno del loop. Qui non legge ilistener creati nel main
    global REPLAY
    print("___________________________RIPETO I COMANDI__________________________________")
    REPLAY = True

    while cicli > 0 and REPLAY:
        oldCommand = {}
        for command in COMMANDLOG:
            print(command)
            currTime = command["time"]
            if oldCommand:
                prevTime = oldCommand["time"]
            else:
                prevTime = currTime
            # print(f"currTime: {currTime}, prevTime: {prevTime}, PAUSA: {currTime-prevTime}")
            time.sleep(currTime - prevTime)
            if "move" in command:
                pyautogui.moveTo(command["move"][0], command["move"][1], duration=0.2, tween=pyautogui.easeInOutQuad)
            if "click" in command:
                # time.sleep(0.1)
                if command["click"]:
                    # pyautogui.click()
                    mController.press(command["button"])
                else:
                    mController.release(command["button"])
            elif "scroll" in command:
                # time.sleep(0.1)
                pyautogui.moveTo(command["move"][0], command["move"][1])
                pyautogui.scroll(command["scroll"][1] * 100)
            elif "key" in command:
                # time.sleep(0.1)
                kController.press(command["key"])
            elif "releasekey" in command:
                # time.sleep(0.1)
                kController.release(command["releasekey"])
            oldCommand = command
        print(f"Giro {cicli} concluso")
        if loop:
            cicli += 1
        else:
            cicli -= 1
    print("_________________________OPERAZIONE TERMINATA________________________")
    mListenerR.stop()
    klistenerR.stop()
    REPLAY = False
    windowMain["fase"].update("")
    try:
        windowWidget["cicliText"].update("N cicli: ")
    except:
        print("non in widget mode")


mListener = mouse.Listener(on_click=on_click, on_scroll=on_scroll)
klistener = keyboard.Listener(on_press=on_press, on_release=on_release)
mListener.start()
klistener.start()

layoutMain = [[sg.Text("Comandi manuali per controllare Automator\n"
                       "(premere i seguenti tasti in quest'ordine)\n"
                       "Avvio REC: capsLock+capsLock+shift+ctrl\n"
                       "Stop REC e avvio REPLAY: capsLockx4\n"
                       "Interruzione: ESC (completa l'ultimo ciclo e termina)")],
              [sg.Text('Imposta il numero di ripetizioni: '), sg.InputText("1", key='cicli', size=(10, 1)),
               sg.Button('Imposta', key='impostaCicli')],
              [sg.Text('Oppure: '), sg.Button('Loop Continuo', key='loop',
                                              tooltip="Terminata la registrazione, ripeterà i comandi all'infinito")],
              [sg.Text('Cicli: '), sg.Text('1', key="mostraCicli", size=(5, 1)), sg.Text('', key="fase", size=(20, 1))],
              [sg.Button('Ripeti', key="ricicla", tooltip="Ripeti l'ultimo ciclo registrato o importato.\n"
                                                          "Il ciclo si avvierà dopo 5 secondi")],
              [sg.Text('')],
              [sg.Button('Esporta ciclo', key='esporta'),
               sg.Button('Importa ciclo', key='importa')],
              [sg.Exit(button_color=('white', 'firebrick4'), key='Exit'),
               sg.Button("Widget", key='widget',
                         tooltip='Minimizza la finestra, mantenendola sempre in prima pagina')]]
windowMain = sg.Window('Automator', layoutMain, auto_size_buttons=True, keep_on_top=False, grab_anywhere=False,
                       no_titlebar=False)
while True:
    event, values = windowMain.read()
    if event is None or event == 'Exit':  # ALWAYS give a way out of program
        mListener.stop()
        klistener.stop()
        windowMain.Close()
        quit()
        break
    if event == 'impostaCicli':
        try:
            CICLI = int(values['cicli'])
            windowMain["mostraCicli"].update(CICLI)
        except:
            sg.PopupOK("Non hai inserito un numero!")
    elif event == "loop":
        LOOP = True
        windowMain["mostraCicli"].update("LOOP")
    elif event == "ricicla":
        if COMMANDLOG:
            sg.PopupOK("Il ciclo si avvierà dopo 5 secondi da quando avrai chiuso questo popup")
            time.sleep(5)
            repeater(CICLI, LOOP)
        else:
            sg.PopupOK("Non ci sono comandi da eseguire")
    elif event == 'esporta':
        freeToGo = True
        filename = False
        while freeToGo:
            filename = sg.PopupGetFile(f'Scegli dove esportare il file (Scegliere come estensione il .pkl)',
                                       default_extension=".pkl", save_as=True, file_types=(('PKL', '.pkl'),))
            if not filename:
                break
            elif ".pkl" in filename:
                break
            else:
                filename = filename.split(".")
                filename = filename[0] + ".pkl"
                break
        if filename:
            if COMMANDLOG:
                try:
                    afile = open(filename, 'wb')

                    pickle.dump(COMMANDLOG, afile)

                    afile.close()
                    sg.PopupOK('File esportato con successo')
                except:
                    sg.PopupOK("Salvataggio non avvenuto. Controllare che il file non sia aperto")
            else:
                sg.PopupOK("Non c'è nulla da esportare. Registra prima qualcosa")
    elif event == 'importa':
        freeToGo = True
        filename = False
        while freeToGo:
            filename = sg.PopupGetFile(f'Scegli il file .pkl con la lista di comandi da importare',
                                       default_extension=".csv", file_types=(('PKL', '.pkl'),))
            if not filename:
                break
            elif ".pkl" in filename:
                break
            else:
                sg.PopupOK("Il file selezionato non è un .pkl")
        if filename:
            file2 = open(filename, 'rb')
            COMMANDLOG = pickle.load(file2)
            file2.close()
            print(COMMANDLOG)
            sg.PopupOK("Comandi importati correttamente")
    elif event == "widget":
        layoutWidget = [[sg.Text('N cicli: ', key="cicliText"), sg.InputText("1", key='cicli', size=(5, 1)),
                         sg.Button('Imposta', key='impostaCicli'),
                         sg.Button('Loop', key='loop',
                                   tooltip="Terminata la registrazione, ripeterà i comandi all'infinito")],
                        [sg.Button('Ripeti', key="ricicla", tooltip="Ripeti l'ultimo ciclo registrato o importato.\n"
                                                                    "Il ciclo si avvierà dopo 5 secondi"),
                         sg.Button('Esporta', key='esporta'),
                         sg.Button('Importa', key='importa'),
                         sg.Exit(button_color=('white', 'firebrick4'), key='Exit')]]
        windowWidget = sg.Window('Automator', layoutWidget, grab_anywhere=True, auto_size_buttons=True,
                                 keep_on_top=True,
                                 no_titlebar=True)

        windowMain.Hide()
        while True:
            eventWidget, valuesWidget = windowWidget.read()
            if eventWidget is None or eventWidget == 'Exit':  # ALWAYS give a way out of program
                windowWidget.Close()
                windowMain.UnHide()
                break
            if eventWidget == 'impostaCicli':
                try:
                    CICLI = int(valuesWidget['cicli'])
                    windowWidget["cicli"].update(CICLI)
                except:
                    sg.PopupOK("Non hai inserito un numero!")
            elif eventWidget == "loop":
                LOOP = True
                windowWidget["cicli"].update("LOOP")
            elif eventWidget == "ricicla":
                if COMMANDLOG:
                    sg.PopupOK("Il ciclo si avvierà dopo 5 secondi da quando avrai chiuso questo popup")
                    time.sleep(5)
                    repeater(CICLI, LOOP)
                else:
                    sg.PopupOK("Non ci sono comandi da eseguire")
            elif eventWidget == 'esporta':
                freeToGo = True
                filename = False
                while freeToGo:
                    filename = sg.PopupGetFile(f'Scegli dove esportare il file (Scegliere come estensione il .pkl)',
                                               default_extension=".pkl", save_as=True, file_types=(('PKL', '.pkl'),))
                    if not filename:
                        break
                    elif ".pkl" in filename:
                        break
                    else:
                        filename = filename.split(".")
                        filename = filename[0] + ".pkl"
                        break
                if filename:
                    if COMMANDLOG:
                        control = storeData(filename, EXPORTHEADER, "w")
                        if control:
                            for command in COMMANDLOG:
                                if "click" in command:
                                    type = "click"
                                elif "key" in command:
                                    type = "key"
                                elif "releasekey" in command:
                                    type = "releasekey"
                                elif "scroll" in command:
                                    type = "scroll"
                                value = command[type]
                                if "button" in command:
                                    button = command["button"]
                                else:
                                    button = ""
                                if "move" in command:
                                    move = command["move"]
                                else:
                                    move = ""
                                atime = command["time"]
                                # storeData(filename, [type, value, button, move, atime])
                                afile = open(filename, 'wb')
                                pickle.dump(COMMANDLOG, afile)
                                afile.close()
                            sg.PopupOK('File esportato con successo')
                        else:
                            sg.PopupOK("Salvataggio non avvenuto. Controllare che il file non sia aperto")
                    else:
                        sg.PopupOK("Non c'è nulla da esportare. Registra prima qualcosa")
            elif eventWidget == 'importa':
                freeToGo = True
                filename = False
                while freeToGo:
                    filename = sg.PopupGetFile(f'Scegli il file .pkl con la lista di comandi da importare',
                                               default_extension=".csv", file_types=(('PKL', '.pkl'),))
                    if not filename:
                        break
                    elif ".pkl" in filename:
                        break
                    else:
                        sg.PopupOK("Il file selezionato non è un .pkl")
                if filename:
                    file2 = open(filename, 'rb')
                    COMMANDLOG = pickle.load(file2)
                    file2.close()
                    print(COMMANDLOG)
                    sg.PopupOK("Comandi importati correttamente")
