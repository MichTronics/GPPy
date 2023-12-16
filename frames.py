from PyQt5.QtGui import QTextCursor
from ax253 import Frame, FrameType, Control
import configparser

CONNECTED = False

serverFormat = '<span style="color:#29F500;">{}</span>'
allFormat = '<span style="color:gray;">{}</span>'
uiFormat = '<span style="color:yellow;">{}</span>'
discFormat = '<span style="color:red;">{}</span>'
messageFormat = '<span style="color:white;">{}</span>'

config = configparser.ConfigParser()


''' Frames Handler for AX25 '''
class FramesHandler:
    def __init__(self) -> None:
        # super(FramesHandler, self).__init__()
        # print("FramesHandler_init")
        
        pass
    
    def received_frame(self, frame, ui, ki):
        config.read('./config.ini')
        rframes = self.replace_charcters_html(frame)
        frame = rframes
        self.check_ftype_messages(frame, ui, ki)
        # print(self)
        # print(ki)
        # print(frame)
        
    
    def replace_charcters_html(self, frame):
        if b'<' in frame or b'>' in frame:
            a = frame.replace(b'<', b'&lt;')
            b = a.replace(b'>', b'&gt;')
            frame = b
        frame_lt_gt_br = frame.replace(b'\r', b'<br>')
        return frame_lt_gt_br
    
    def disc(ui, ki):
        frame_disc = Frame.ui(
            destination=frameAX25Source,
            source=config['gp3']['mycall'],
            path=[],
            info="",
            control=FrameType.U_DISC.value,
        )
        ui.tEMonitor.append(discFormat.format(str(frame_disc) +  ' ' + str(frame_disc.control.ftype)))
        ki.write(frame_disc)
        CONNECTED = False
        ui.tECh1.append(discFormat.format("Disconnected from " + str(frameAX25Source)))
        ui.pBChan1.setText("1: ------")
        ui.pBDiscCh1.lower()
        
        
    def check_ftype_messages(self, frame, ui, ki):
        global CONNECTED
        global frameAX25Source
        frameAX25 = Frame.from_bytes(frame)
        frameAX25Source = frameAX25.source.callsign.decode()
        frameAX25Destination = frameAX25.destination
        frameAX25Control = frameAX25.control.ftype
        frameAX25Info = frameAX25.info
        frameAX25Split = [str(frameAX25).split(':', 1)[0] + ':'] + str(frameAX25).split(':', 1)[1:]
        
        if frameAX25Control is FrameType.I:
            ui.tEMonitor.append(allFormat.format(frameAX25Split[0] + " " + str(frameAX25Control)))
            ui.tEMonitor.append(uiFormat.format(frameAX25Split[1]))
            if CONNECTED is True:
                ui.tECh1.append(messageFormat.format(frameAX25Split[1]))
                frame_rr = Frame.ui(
                    destination=frameAX25Source,
                    source=config['gp3']['mycall'],
                    path=[],
                    info="",
                    control=FrameType.S_RR.value | (1 << 4) | (1 << 5), 
                )
                ui.tEMonitor.append(discFormat.format(str(frame_rr) +  ' ' + str(frame_rr.control.ftype)))
                ki.write(frame_rr)
        elif frameAX25Control is FrameType.U_UI:
            ui.tEMonitor.append(allFormat.format(frameAX25Split[0] + " " + str(frameAX25Control)))
            ui.tEMonitor.append(uiFormat.format(frameAX25Split[1]))
        elif frameAX25Control is FrameType.U_UA:
            ui.tEMonitor.append(serverFormat.format(frameAX25Split[0] + " " + str(frameAX25Control)))
            if config['gp3']['mycall'] in str(frameAX25Destination) and CONNECTED is False:
                CONNECTED = True
                ui.tECh1.append(serverFormat.format("Connected to " + str(frameAX25Source)))
            else:
                CONNECTED = False
        elif frameAX25Control is FrameType.S_RR:
            ui.tEMonitor.append(allFormat.format(frameAX25Split[0] + " " + str(frameAX25Control)))
            if CONNECTED is False:
                frame_disc = Frame.ui(
                    destination=frameAX25Source,
                    source=config['gp3']['mycall'],
                    path=[],
                    info="",
                    control=FrameType.U_DISC.value,
                )
                ui.tEMonitor.append(discFormat.format(str(frame_disc) +  ' ' + str(frame_disc.control.ftype)))
                ki.write(frame_disc)
                # CONNECTED = False
            else:
                frame_rr = Frame.ui(
                    destination=frameAX25Source,
                    source=config['gp3']['mycall'],
                    path=[],
                    info="",
                    control=FrameType.S_RR.value | (1 << 4) | (1 << 5), 
                )
                ui.tEMonitor.append(discFormat.format(str(frame_rr) +  ' ' + str(frame_rr.control.ftype)))
                ki.write(frame_rr)
                
        elif frameAX25Control is FrameType.U_DISC:
            if CONNECTED is True:
                ui.tEMonitor.append(discFormat.format(frameAX25Split[0] + " " + str(frameAX25Control)))
                frame_disc = Frame.ui(
                    destination=frameAX25Source,
                    source=config['gp3']['mycall'],
                    path=[],
                    info="",
                    control=FrameType.U_UA.value,
                )
                ui.tEMonitor.append(discFormat.format(str(frame_disc) +  ' ' + str(frame_disc.control.ftype)))
                ki.write(frame_disc)
                CONNECTED = False
                ui.tECh1.append(discFormat.format("Disconnected from " + str(frameAX25Source)))
            else:
                ui.tEMonitor.append(allFormat.format(frameAX25Split[0] + " " + str(frameAX25Control)))

        else:
            ui.tEMonitor.append(allFormat.format(str(frameAX25) + " " + str(frameAX25Control)))
        ui.tEMonitor.moveCursor(QTextCursor.End)

    