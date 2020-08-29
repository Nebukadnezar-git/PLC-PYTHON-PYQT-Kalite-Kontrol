from PyQt5.QtWidgets import*
from proje import Ui_MainWindow
import cv2
from PyQt5 import QtCore
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi
import datetime
import sys
import snap7.client as c
from snap7.util import *
from snap7.snap7types import *
import numpy as np
import time

class PLC_PyQt5(QMainWindow):

    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.logic = 0
        self.liste = list()
        self.ui.SHOW.clicked.connect(self.goruntu)
        self.ui.Exit.clicked.connect(self.cikis)
        self.ui.CAPTURE.clicked.connect(self.CaptureClicked)
       
    def goruntu(self):
        cap = cv2.VideoCapture(0)
        while (cap.isOpened()):
            self.alan = 0
            ret, frame = cap.read()
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            mask_alan = np.ones(frame.shape[:2], np.uint8)
            mask_alan.fill(255)
            sub_alan = cv2.subtract(mask_alan, gray)
            (thresh, blackAndWhiteImage) = cv2.threshold(sub_alan, 165, 225, cv2.THRESH_BINARY)
            im_floodfill = blackAndWhiteImage.copy()
            h, w = blackAndWhiteImage.shape[:2]
            mask_parca_2 = np.zeros((h + 2, w + 2), np.uint8)
            cv2.floodFill(im_floodfill, mask_parca_2, (0, 0), 255)
            im_floodfill_inv = cv2.bitwise_not(im_floodfill)
            im_out = blackAndWhiteImage | im_floodfill_inv
            for a in range(0, 480):
                for b in range(0, 640):
                    if im_out[a, b] == 255:
                        self.alan += 1
            
            if ret == True:
                self.displayImage(im_out)
                def ReadMemory(plc,byte,bit,datatype):
                    result = plc.read_area(areas['MK'],0,byte,datatype)
                    if datatype==S7WLBit:
                        return get_bool(result,0,bit)
                    elif datatype==S7WLByte or datatype==S7WLWord:
                        return get_int(result,0)
                    elif datatype==S7WLReal:
                        return get_real(result,0)
                    elif datatype==S7WLDWord:
                        return get_dword(result,0)
                    else:
                        return None

                def WriteMemory(plc,byte,bit,datatype,value):
                    result = plc.read_area(areas['MK'],0,byte,datatype)
                    if datatype==S7WLBit:
                        set_bool(result,0,bit,value)
                    elif datatype==S7WLByte or datatype==S7WLWord:
                        set_int(result,0,value)
                    elif datatype==S7WLReal:
                        set_real(result,0,value)
                    elif datatype==S7WLDWord:
                        set_dword(result,0,value)
                    plc.write_area(areas["MK"],0,byte,result)            
                if self.alan<168950:
                    if __name__=="__main__":
                        plc = c.Client()
                        plc.connect('192.168.0.80',0,1) #Buradaki ip adresi PLC ip adresim
                        WriteMemory(plc,0,0,S7WLBit,1)
                        time.sleep(100000)
                else:
                    if __name__=="__main__":
                        plc = c.Client()
                        plc.connect('192.168.0.80',0,1) #Buradaki ip adresi PLC ip adresim
                        WriteMemory(plc,0,0,S7WLBit,0)
                        time.sleep(10000)                
                k = cv2.waitKey(30) & 0xff
                if k == 27: # press 'ESC' to quit
                    break
            
                if(self.logic==2):
                    date = datetime.datetime.now()
                    NAME ='C:/Users/Thor/Desktop/akademik/pydsml/python_egitim/arayuz/proje/Saved_Images/Image_%s%s%sT%s%s%s.png'%(date.year, date.month, date.day, date.hour, date.minute, date.second) 
                    print(NAME)
                    cv2.imwrite(NAME, frame)
            else:
                print("Kamera Acılamadı..")   

        cap.release()
        cv2.destroyAllWindows()

    def cikis(self):
        cap.close()
        window.close()
    
    def CaptureClicked(self):
        self.logic =2

    def displayImage(self, img):
        qformat = QImage.Format_Indexed8

        if len(img.shape) == 3:
            if (img.shape[2]) == 4:
                qformat = QImage.Format_RGBA8888

            else:
                qformat = QImage.Format_RGB888
        img = QImage(img, img.shape[1], img.shape[0], qformat)
        img = img.rgbSwapped()
        self.ui.imgLabel.setPixmap(QPixmap.fromImage(img))
        self.ui.imgLabel.setAlignment(QtCore.Qt.AlignHCenter | QtCore.Qt.AlignVCenter)


uygulama = QApplication([])
pencere = PLC_PyQt5()
pencere.show()
uygulama.exec_()
