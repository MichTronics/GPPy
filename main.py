import os, sys, time
from collections.abc import Callable, Iterable, Mapping
from typing import Any
from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, Qt, QEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
import settings 
from threading import Thread
from ax253 import Frame, FrameType, Control
import kiss

MYCALL = os.environ.get("MYCALL", "NL2TST")
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
        uic.loadUi("./gp3/settings.ui", self)
        self.setWindowTitle("GP3 Settings")

        self.pBSetCancel.clicked.connect(self.cancel)
        self.pBSetSave.clicked.connect(self.save)
        self.lEMycall.setText(settings.MYCALL)
    
    def save(self):
        settings.MYCALL = self.lEMycall.text()
        self.hide()
    
    def cancel(self):
        self.hide()

Test = uic.loadUiType("./gp3/connect.ui")[0]

''' GP3 Connect Window '''
class Gp3ConGUI(QDialog, Test):
    def __init__(self, parent=None) -> None:
        QDialog.__init__(self, parent)
        self.setupUi(self)
        # super(Gp3ConGUI, self).__init__()
        global conclose
        global conui
        # conui = 
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # conui.resize(300,100)
        self.move(500, 824)
        self.conclose = False
        self.show()
        # self.lEConCallsign.installEventFilter(self)
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
            source=MYCALL,
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
        ui = uic.loadUi("./gp3/gp3.ui")
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
         

        
   
# class MouseObserver(QObject):
#     def __init__(self, widget):
#         super(MouseObserver, self).__init__(widget)
#         self._widget = widget
#         self.widget.eventFilter(self)
    
#     @property
#     def widget(self):
#         return self._widget
    
#     def eventFilter(self, o: QObject, e: QEvent):
#         if o is self.widget:
#             if e.type() == QEvent.Type.MouseButtonPress:
#                 print("Test")
            
class kissAx25(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window=window
        
        print("Try to connect to Direwolf server.")
        ki.start()
        ui.tEMonitor.append(serverFormat.format("Connected to Direwolf"))
        
    def run(self): 
        print("Read Frames")   
        TCP_IP = '192.168.6.115'
        TCP_PORT = 8102
        BUFFER_SIZE = 255
        while True:
            ki.read(callback=self.print_frame, min_frames=None)
            
    def print_frame(self, frame):
        global CONNECTED
        test = Frame.from_bytes(frame)
        print(test.control.ftype)
        dest = str(test.destination)
        if test.control.ftype is FrameType.U_UI:
            # ui.textEdit.setStyleSheet("color: #FF00FF")
            ui.tEMonitor.append(uiFormat.format(str(Frame.from_bytes(frame)) + " " + str(test.control.ftype)))
        else:
            # ui.textEdit.setStyleSheet("color: #00FF00")        
            ui.tEMonitor.append(allFormat.format(str(Frame.from_bytes(frame)) + " " + str(test.control.ftype)))
        
        if MYCALL in dest and CONNECTED is False:
            print("Ontvangen")
            if test.control.ftype is FrameType.U_UA:
                print(test.info)               
            
                              
        # Gp3 = Gp3GUI()
        # Gp3.sFtE("Test")
       
        
def main():
    app = QApplication([])
    window = Gp3GUI()
    kissThread = kissAx25(window)
    kissThread.start()
    app.exec_()
    
if __name__ == '__main__':
    main()