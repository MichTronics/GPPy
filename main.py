import os, sys, time
from collections.abc import Callable, Iterable, Mapping
from typing import Any
from PyQt5.QtGui import *
from PyQt5.QtCore import QObject, Qt, QEvent, pyqtSignal, pyqtSlot, QPoint
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget
import configparser
from threading import Thread
from ax253 import Frame, FrameType, Control
import kiss
from frames import FramesHandler

# CONNECTED = False
CHATMONITOR = False

config = configparser.ConfigParser()
config.read('./config.ini')

ki = kiss.TCPKISS(host=config['interface1']['host'], port=int(config['interface1']['port']), strip_df_start=True)

serverFormat = '<span style="color:#29F500;">{}</span>'
allFormat = '<span style="color:gray;">{}</span>'
uiFormat = '<span style="color:yellow;">{}</span>'
discFormat = '<span style="color:red;">{}</span>'

''' GPPy Main Gui '''        
class GppyGUI(QMainWindow):
    customSignal = pyqtSignal(QTextCursor)
    def __init__(self):
        super(GppyGUI, self).__init__()
        global ui
        global config
        config.read('./config.ini')
        ui = uic.loadUi("./gppy.ui")
        # ui.setWindowFlag(Qt.FramelessWindowHint) 
        ui.move(200,100)
        
        ui.widConnect.hide()
        ui.widSettings.raise_()
        ui.widSettings.hide()
        
        ui.widChan1.installEventFilter(self)
        ui.tEInput.installEventFilter(self)
        
        ui.pBChan1.clicked.connect(self.chan1)
        ui.lWTitle.setText("Monitor")
        ui.pBConnectCh1.clicked.connect(self.pBConnectCh1)
        ui.pBMonitorCh1.clicked.connect(self.monitor)
        ui.lEConCallsign.returnPressed.connect(self.connectCh1)
        
        ui.pBSetSave.clicked.connect(self.pBSetSave)
        ui.pBSetCancel.clicked.connect(self.pBSetCancel)
        
        ui.pBMheard.clicked.connect(self.mheard)
        ui.pBSettings.clicked.connect(self.settings)
        ui.pBMonitor.setEnabled(False)
        ui.pBMonitor.clicked.connect(self.monitor)
        ui.pBDiscCh1.clicked.connect(GppyGUI.disconnectCh1)
        ui.tEMonitor.document().setMaximumBlockCount(5000)
        # ui.tEInput.returnPressed.connect(self.send_input)
        ui.show()
        
    def eventFilter(self, a0: QObject, a1: QEvent) -> bool:
        global CHATMONITOR
        if (a1.type() == a1.Type.KeyPress and a0 is ui.tEInput):
            if a1.key() == Qt.Key.Key_Return and ui.tEInput.hasFocus():
                print('Enter Pressed.')
        
        if (a1.type() == a1.Type.MouseButtonPress and a0 is ui):
            if a1.button() == Qt.MouseButton.RightButton:
                print("Test")
            
        if a1.type() == a1.Type.MouseButtonPress and a0 is ui.widChan1:
            if a1.button() == Qt.MouseButton.RightButton:
                if CHATMONITOR == False:
                    CHATMONITOR = True
                    ui.widConnect.hide()
                    ui.widChan1.resize(1024, 500) #551
                    ui.tECh1.resize(1024, 500)
                    ui.widStatusBot.move(0, 649) #700
                    ui.widMonitor.resize(1024, 51) #571
                    ui.widMonitor.move(0,670) #150
                    ui.widMheard.lower()
                    ui.tEMonitor
                    ui.tEMonitor.resize(1024, 51)
                    # ui.tEMonitor.move(0, 649)
                elif CHATMONITOR == True:
                    CHATMONITOR = False
                    ui.widConnect.hide()
                    ui.widChan1.resize(1024, 551) #551
                    ui.tECh1.resize(1024, 551)
                    ui.widStatusBot.move(0, 700) #700
                    ui.widMonitor.resize(1024, 551) #571
                    ui.widMonitor.move(0,150) #150
                    ui.widMonitor.lower()
                    ui.tEMonitor.resize(1024, 551)
                    # ui.tEMonitor.move(0, 150)
        return super().eventFilter(a0, a1)
        
    def connectCh1(self):
        print("Try to connect..")
        config.read('./config.ini')
        print(ui.lEConCallsign.text())
        frame_sabm = Frame.ui(
            destination=ui.lEConCallsign.text(),
            source=config['gp3']['mycall'],
            path=[],
            info="",
            control=FrameType.U_SABM.value,
            # control=Control(b"\x2f" | FrameType.S_RR.value | (1 << 4))
        )
        # ui.tEMonitor.append(serverFormat.format("Connected to Direwolf"))
        ui.tEMonitor.append(serverFormat.format(str(frame_sabm) + " " + str(frame_sabm.control.ftype)))
        ui.pBConnectCh1.lower()
        ui.pBChan1.setText("1: " + ui.lEConCallsign.text())
        ui.tEMonitor.moveCursor(QTextCursor.End)

        # print()
        ki.write(frame_sabm)
        # self.close()
        ui.widConnect.hide()
        
    def chan1(self):
        ui.widMonitor.lower()
        ui.widMheard.lower()
        ui.widButtons.lower()
        ui.pBMonitor.setEnabled(True)
           
    def settings(self):   
        ui.widSettings.show()
        ui.lESetMycall.setText(config['gp3']['mycall'])
        # self.w = Gp3SetGUI()
        # self.w.show()
        
    def pBSetCancel(self):
        ui.widSettings.hide()
        
    def pBSetSave(self):
        # MYCALL = self.lEMycall.text()
        config["gp3"]["mycall"] = ui.lESetMycall.text()
        with open('./config.ini', 'w') as configfile:
            config.write(configfile)
        ui.widSettings.hide()
        
    def pBConnectCh1(self):
        ui.widConnect.show()
        ui.lEConCallsign.setFocus()
        ui.lEConCallsign.selectAll()
        # effect = QGraphicsDropShadowEffect(
        # offset=QPoint(3, 3), blurRadius=25, color=QColor("#111"))
        # ui.widConnect.setGraphicsEffect(effect)
        # ui.lEConCallsign.setCursorPosition(2)
        # self.w = Gp3ConGUI()
        # self.w.show()

    def disconnectCh1():
        FramesHandler.disc(ui, ki)
        ui.pBDiscCh1.lower()
             
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
        ui.widMonitor.resize(1024, 551) #571
        ui.widMonitor.move(0,150)
        ui.tEMonitor.resize(1024, 551)
        ui.widMheard.lower()
        ui.widChan1.lower()
        ui.widButtonsCh1.lower()
        # ui.widMheard.setEnabled(False)
        
    def monitor_message(message):
        print(message)
        # ui.tEMonitor.append(message)
        # ui.tEMonitor.moveCursor(QTextCursor.End)
        

''' Ax25 Class '''           
class kissAx25(Thread):
    def __init__(self, window):
        Thread.__init__(self)
        self.window=window
        ki.start()
        ui.tEMonitor.append(serverFormat.format("Connected to Direwolf"))
        
    def run(self): 
        while True:
            ki.read(callback=self.receive_frame, min_frames=None)
            
    def receive_frame(self, frame):
        self.fh = FramesHandler()
        self.fh.received_frame(frame, ui, ki)
        # global CONNECTED
        
        # config.read('./config.ini')
        # if b'<' in frame or b'>' in frame:
        #     a = frame.replace(b'<', b'&lt;')
        #     b = a.replace(b'>', b'&gt;')
        #     frame = b
        # t = frame.replace(b'\r', b'<br>')
        # frame = t
        # test = Frame.from_bytes(frame)
        # print(frame)
        # print(str(frame))
        # print(test)
        # print(test.control.ftype)
        # dest = str(test.destination)
        # 
        # if test.control.ftype is FrameType.U_UI or test.control.ftype is FrameType.I:
        #     ui.tEMonitor.append(allFormat.format(a[0] + " " + str(test.control.ftype)))
        #     ui.tEMonitor.append(uiFormat.format(a[1]))
        #     print(a)            
        # else:
        #     ui.tEMonitor.append(allFormat.format(str(test) + " " + str(test.control.ftype)))
        # ui.tEMonitor.moveCursor(QTextCursor.End)
        
        
        # if config['gp3']['mycall'] in str(test.destination) and CONNECTED is False:
        #     print("test")
        #     if test.control.ftype is FrameType.U_UA:
        #         CONNECTED = True
        # elif config['gp3']['mycall']in str(test.destination) and CONNECTED is True:
        #     if test.control.ftype is FrameType.I:
        #         print(test.info)
        #         # for line in test.info.split(b"\r"):
        #         #     print(line.decode("utf-8"))
        #             # decode_string = test.info.decode("utf-8")
        #             # print(decode_string)
        
def main():
    app = QApplication([])
    window = GppyGUI()
    kissThread = kissAx25(window)
    kissThread.start()
    app.exec_()
    
if __name__ == '__main__':
    main()