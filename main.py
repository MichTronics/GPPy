import os, sys, time
from collections.abc import Callable, Iterable, Mapping
from typing import Any
from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, Qt, QEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
import configparser
from threading import Thread
from ax253 import Frame, FrameType, Control
import kiss

config = configparser.ConfigParser()
# config.read('./config.ini')

# MYCALL = config['gp3']['mycall']
KISS_HOST = os.environ.get("KISS_HOST", "192.168.6.115")
KISS_PORT = os.environ.get("KISS_PORT", "8102")
CONNECTED = False
CHATMONITOR = False

ki = kiss.TCPKISS(host=KISS_HOST, port=int(KISS_PORT), strip_df_start=True)

serverFormat = '<span style="color:#29F500;">{}</span>'
allFormat = '<span style="color:gray;">{}</span>'
uiFormat = '<span style="color:yellow;">{}</span>'

''' GP3 Settings Window '''
class Gp3SetGUI(QMainWindow):
    def __init__(self):
        super(Gp3SetGUI, self).__init__()
        uic.loadUi("./settings.ui", self)
        self.setWindowTitle("GP3 Settings")
        
        config.read('./config.ini')

        self.pBSetCancel.clicked.connect(self.cancel)
        self.pBSetSave.clicked.connect(self.save)
        self.lEMycall.setText(config['gp3']['mycall'])
        
    
    def save(self):
        # MYCALL = self.lEMycall.text()
        config["gp3"]["mycall"] = self.lEMycall.text()
        with open('./config.ini', 'w') as configfile:
            config.write(configfile)
        self.hide()
    
    def cancel(self):
        self.hide()

gp3ConUi = uic.loadUiType("./connect.ui")[0]

''' GP3 Connect Window '''
class Gp3ConGUI(QDialog, gp3ConUi):
    def __init__(self, parent=None) -> None:
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # super(Gp3ConGUI, self).__init__()
        global conclose
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.move(500, 824)
        self.conclose = False
        self.show()
        self.lEConCallsign.returnPressed.connect(self.conCh1)
        ui.installEventFilter(self)
        
    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        # if (a1.type() == a1.Type.KeyPress and a0 is self.lEConCallsign):
        #     if a1.key() == Qt.Key.Key_Enter:
        #         print('Enter') 
        if (a1.type() == a1.Type.MouseButtonPress and a0 is ui and self.conclose == False):
            if a1.button() == Qt.MouseButton.RightButton:
                self.conclose = True
                self.close()
        
        return super().eventFilter(a0, a1)
    
    def cancel(self):
        self.hide
        
    def conCh1(self):
        print("Try to connect..")
        print(self.lEConCallsign.text())
        frame = Frame.sabm(
            destination=self.lEConCallsign.text(),
            source=config['gp3']['mycall'],
        )
        # ui.tEMonitor.append(serverFormat.format("Connected to Direwolf"))
        ui.tEMonitor.append(serverFormat.format(str(frame) + " " + str(frame.control.ftype)))

        print()
        ki.write(frame)
        

''' GP3 Main Gui '''        
class Gp3GUI(QMainWindow):
    
    def __init__(self):
        super(Gp3GUI, self).__init__()
        global ui
        ui = uic.loadUi("./gp3.ui")
        # ui.setWindowFlag(Qt.FramelessWindowHint) 
        ui.show()
        ui.pBMheard.clicked.connect(self.mheard)
        ui.pBSettings.clicked.connect(self.settings)
        ui.pBMonitor.setEnabled(False)
        ui.pBMonitor.clicked.connect(self.monitor)
        ui.pBMonitorCh1.clicked.connect(self.monitor)
        ui.pBChan1.clicked.connect(self.chan1)
        ui.lWTitle.setText("Monitor")
        ui.pBConnectCh1.clicked.connect(self.connect)
        ui.widChan1.installEventFilter(self)
        
    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        global CHATMONITOR
        if (a1.type() == a1.Type.MouseButtonPress and a0 is ui):
            if a1.button() == Qt.MouseButton.RightButton:
                print("Test")
            
        if a1.type() == a1.Type.MouseButtonPress and a0 is ui.widChan1:
            if a1.button() == Qt.MouseButton.RightButton:
                if CHATMONITOR == False:
                    CHATMONITOR = True
                    ui.widChan1.resize(1031, 500) #551
                    ui.widStatusBot.move(0, 649) #700
                    ui.widMonitor.resize(1031, 51) #571
                    ui.widMonitor.move(0,670) #150
                    ui.widMheard.lower()
                    ui.tEMonitor
                    ui.tEMonitor.resize(1031, 51)
                    # ui.tEMonitor.move(0, 649)
                elif CHATMONITOR == True:
                    CHATMONITOR = False
                    ui.widChan1.resize(1031, 551) #551
                    ui.widStatusBot.move(0, 700) #700
                    ui.widMonitor.resize(1031, 551) #571
                    ui.widMonitor.move(0,150) #150
                    ui.widMonitor.lower()
                    ui.tEMonitor.resize(1031, 551)
                    # ui.tEMonitor.move(0, 150)
        return super().eventFilter(a0, a1)
        
    def chan1(self):
        ui.widMonitor.lower()
        ui.widMheard.lower()
        ui.widButtons.lower()
        ui.pBMonitor.setEnabled(True)
           
    def settings(self):    
        self.w = Gp3SetGUI()
        self.w.show()
        
    def connect(self):
        self.w = Gp3ConGUI()
        self.w.show()
             
    def mheard(self):
        ui.lWTitle.setText("MHeard")
        ui.pBMonitor.setEnabled(True)
        ui.pBMheard.setEnabled(False)
        ui.widMonitor.lower()
        ui.widChan1.lower()
        ui.widStatusBot.lower()
        # ui.widStatusBot.setEnabled(False)
        ui.widMonitor.setEnabled(False)
        # ui.widget_4.lower()
        # ui.textEdit.append('Test') 
        
    def monitor(self):        
        ui.lWTitle.setText("Monitor")
        ui.pBMonitor.setEnabled(False)
        ui.pBMheard.setEnabled(True)
        # ui.widMonitor.lower()
        ui.widMonitor.resize(1031, 551) #571
        ui.widMonitor.move(0,150)
        ui.tEMonitor.resize(1031, 551)
        ui.widMheard.lower()
        ui.widChan1.lower()
        ui.widButtonsCh1.lower()
        # ui.widMheard.setEnabled(False)
                     
class kissAx25(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window=window
        
        # print("Try to connect to Direwolf server.")
        ki.start()
        ui.tEMonitor.append(serverFormat.format("Connected to Direwolf"))
        
    def run(self): 
        # print("Read Frames")   
        # TCP_IP = '192.168.6.115'
        # TCP_PORT = 8102
        # BUFFER_SIZE = 255
        while True:
            ki.read(callback=self.print_frame, min_frames=None)
            
    def scroll_to_bottom(self):
        # Scroll to the bottom whenever the scrollbar value changes
        ui.tEMonitor.verticalScrollBar().setValue(self.tEMonitor.verticalScrollBar().maximum())
        
    def print_frame(self, frame):
        global CONNECTED
        # config.read('./config.ini')
        if b'<' in frame or b'>' in frame:
            a = frame.replace(b'<', b'&lt;')
            b = a.replace(b'>', b'&gt;')
            frame = b
            # print(b)
        t = frame.replace(b'\r', b'<br>')
        frame = t
        test = Frame.from_bytes(frame)
        print(frame)
        print(str(frame))
        print(test)
        print(test.control.ftype)
        dest = str(test.destination)
        if test.control.ftype is FrameType.U_UI:
            a = [str(test).split(':', 1)[0] + ':'] + str(test).split(':', 1)[1:]
            print(a)            
            ui.tEMonitor.append(allFormat.format(a[0] + " " + str(test.control.ftype)))
            ui.tEMonitor.append(uiFormat.format(a[1]))
        else:
            ui.tEMonitor.append(allFormat.format(str(test) + " " + str(test.control.ftype)))
        ui.tEMonitor.moveCursor(QTextCursor.End)
        
        # if config['gp3']['mycall'] in dest and CONNECTED is False:
        #     print("test")
        #     if test.control.ftype is FrameType.U_UA:
        #         CONNECTED = True
        #         pass
        #     pass
        # elif config['gp3']['mycall']in dest and CONNECTED is True:
        #     if test.control.ftype is FrameType.I:
        #         # print(test.info)
        #         for line in test.info.split(b"\r"):
        #             print(line.decode("utf-8"))
        #             # decode_string = test.info.decode("utf-8")
        #             # print(decode_string)
        #             pass
        #     pass
        
def main():
    app = QApplication([])
    window = Gp3GUI()
    kissThread = kissAx25(window)
    kissThread.start()
    app.exec_()
    
if __name__ == '__main__':
    main()