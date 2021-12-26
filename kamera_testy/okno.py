from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *

import sys, toupcam
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from PyQt5.QtGui import QPixmap, QImage
from PyQt5.QtWidgets import QLabel, QApplication, QWidget, QDesktopWidget, QCheckBox, QMessageBox
import numpy as np
import matplotlib.pyplot as plt

class Camera(QLabel):
    eventImage = pyqtSignal()
    snap_image_event = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.hcam = None
        self.buf = None      # video buffer
        self.w = 0           # video width
        self.h = 0           # video height
        
        self.x = 10
        self.y = 152
        self.total = 0
      #  self.setFixedSize(800, 600)
      #  qtRectangle = self.frameGeometry()
      #  centerPoint = QDesktopWidget().availableGeometry().center()
       # qtRectangle.moveCenter(centerPoint)
      #  self.przemiesc(qtRectangle.topLeft())
        self.initUI()
        self.initCamera()
        
      #  self.h_cam.put_AutoExpoEnable(True)


    def initUI(self):
     #   self.cb = QCheckBox('Auto Exposure', self)
     #   self.cb.stateChanged.connect(self.changeAutoExposure)
     #   self.label = QLabel(self)
        self.setScaledContents(True)
     #   self.label.przemiesc(0, 30)
        self.resize(self.geometry().width(), self.geometry().height())

# the vast majority of callbacks come from toupcam.dll/so/dylib internal threads, so we use qt signal to post this event to the UI thread  
    @staticmethod
    def cameraCallback(nEvent, ctx):
        if nEvent == toupcam.TOUPCAM_EVENT_IMAGE:
            ctx.nowy_obraz_z_kamery.emit()
        elif nEvent == toupcam.TOUPCAM_EVENT_STILLIMAGE:
            ctx.nowy_wymuszony_obraz_z_kamery.emit()
            

                     
# run in the UI thread
    @pyqtSlot()
    def eventImageSignal(self):
        if self.hcam is not None:
            try:
                self.hcam.PullImageV2(self.buf, 24, None)
                self.total += 1
            except toupcam.HRESULTException:
                print('pull image failed')
                QMessageBox.warning(self, '', 'pull image failed', QMessageBox.Ok)
            else:
             #   self.setWindowTitle('{}: {}'.format(self.nazwa_kamery, self.total))
                img = QImage(self.buf, self.w, self.h, (self.w * 24 + 31) // 32 * 4, QImage.Format_RGB888)
                self.setPixmap(QPixmap.fromImage(img))
                
 #   @pyqtSlot()                
    def snap_image_event_signal(self):
        if self.hcam is not None:
            w, h = self.hcam.get_Size()
           # w= 2048
           # h= 1536 
            bufsize = ((w * 24 + 31) // 32 * 4) * h
            still_img_buf = bytes(bufsize)
            self.hcam.PullStillImageV2(still_img_buf, 24, None)
            print('saving image')
        #    print(self.h_cam.get_ExpoTime())
            print(w, h)
            print()
            img = self.bytes_to_array(still_img_buf)
            plt.imsave('img_frame_{}.png'.format(self.total), img)

                        
    def bytes_to_array(self, still_img_buf, dtype=np.uint8):
        arr_1d = np.frombuffer(still_img_buf, dtype=dtype)
        return arr_1d.reshape(self.h, self.w, 3)
        #return arr_1d.reshape(1536, 2048, 3)

    def initCamera(self):
        a = toupcam.Toupcam.EnumV2()
        if len(a) <= 0:
            pass
   #        self.setWindowTitle('No camera found')
    #        self.cb.setEnabled(False)
        else:
            self.camname = a[0].displayname
       #     self.setWindowTitle(self.nazwa_kamery)
            self.eventImage.connect(self.eventImageSignal)
            self.snap_image_event.connect(self.snap_image_event_signal)

            try:
                self.hcam = toupcam.Toupcam.Open(a[0].id)
            except toupcam.HRESULTException:
                QMessageBox.warning(self, '', 'failed to open camera', QMessageBox.Ok)
            else:
                self.w, self.h = self.hcam.get_Size()
                bufsize = ((self.w * 24 + 31) // 32 * 4) * self.h
                self.buf = bytes(bufsize)
         #       self.cb.setChecked(self.h_cam.get_AutoExpoEnable())
                try:
                    if sys.platform == 'win32':
                        self.hcam.put_Option(toupcam.TOUPCAM_OPTION_BYTEORDER, 0) # QImage.Format_RGB888
                    self.hcam.StartPullModeWithCallback(self.cameraCallback, self)
                except toupcam.HRESULTException:
                    QMessageBox.warning(self, '', 'failed to start camera', QMessageBox.Ok)

    def changeAutoExposure(self, state):
        if self.hcam is not None:
            self.hcam.put_AutoExpoEnable(state)
            
    def pause(self, x):
        self.hcam.Pause(x)
        
    def snap_img(self):
        self.hcam.Snap(1)
        
    def restart(self):
        pass
      #  print(se;f)
       # self.h_cam.StartPullModeWithCallback(self.cameraCallback, self)

    def close(self):
        print('closing')
        if self.hcam is not None:
            self.hcam.Close()
            self.hcam = None



class Obraz(QLabel):
    # Klaza Obraz_z_kamery dziedziczy z QLabel, pozwala na lepszą obsługę eventu mouseMoveEvent

    def __init__(self, main_window, *args, **kwargs):
        super(Obraz, self).__init__(*args, **kwargs)

        # obiekt Klasy MainWindow podany jako argument przy tworzeniu obiektu klasy Obraz_z_kamery - pozwala na komunikację z oknem głównym
        self.main_window = main_window

        #Tworzy białe tło
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor('white'))
        self.setPalette(palette)

        # Wczytywanie obrazu do wyświetlenia:
        self.setPixmap(QPixmap('1.jpg'))
        self.setScaledContents(False)

      #  self.setMouseTracking(True)  # Domyślnie ustawione na False - gdy False mouseMoveEvent wywoływany jest tylko gdy któryś z przycisków myszki jest wciśnięty

        # pozycja myszki nad widgetem
        self.x = 0
        self.y = 0


    def mouseMoveEvent(self, e):
        # event występuje tylko jeśli myszka znajduje się nad tym widgetem, 
        # jeżeli metoda zostałaby umieszczona w MainWindow to byłaby wywoływana w każdym miejscu programu, a naszym celem jest żeby zczytywać pozycje nad wyświetlanym obrazem
        # Oczywiście jeżeli zczytywanie rozpoczniemy nad obrazem to trzymając przycisk cały czas da się wyjść poza jego obszar i dalej zczytywać pozycję myszki, ale to raczej nie będzie problemem

        self.x = e.x()
        self.y = e.y()

        text = f'x: {self.x},  y: {self.y}'

        # Wysyłanie pozycji do okna głównego, do atrybutu pozycje[0] gdzie znajduje się widget QLabel wyświetlający pozycję myszki
        self.main_window.pozycje[0].setText(text)




class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):

        super(MainWindow, self).__init__(*args, **kwargs) #konstruktor

        self.setWindowTitle("Mapowanie prubek") #nazwa
        self.resize(800, 600)

        
######################################################################################
################################# Toolbar & Menu #####################################
######################################################################################
        

        toolbar = QToolBar("Funkcje") #stworzenie toolbara
        self.addToolBar(toolbar) #dodanie toolbara

        # Tworzenie 3 akcji w ramach demonstracji działania
        # wciśnięcię któregokolwiek z przycisków akcji wyświetli w konsoli ostatnią zapisaną pozycję myszki uzyskaną przez wywołanie eventu mouseMoveEvent nad widgetem obraz
        action_1 = self.qactiontoolbar("Action_1",  self.onMyToolBarButtonClick)
        action_2 = self.qactiontoolbar("AutoExposure_ON",  lambda x: self.obraz.changeAutoExposure(True))
        action_3 = self.qactiontoolbar("AutoExposure_OFF",  lambda x: self.obraz.changeAutoExposure(False))
        action_4 = self.qactiontoolbar("Pause",  lambda x: self.obraz.pause(1))
        action_5 = self.qactiontoolbar("Unpause",  lambda x: self.obraz.pause(0))
        action_6 = self.qactiontoolbar("Snap obraz",  lambda x: self.obraz.snap_img())
       # action_6 = self.qactiontoolbar("Restart",  lambda x: self.obraz.restart())



        
        toolbar.addAction(action_1) #dodanie przycisku do toolbara
        toolbar.addAction(action_2)
        toolbar.addAction(action_3)
        toolbar.addAction(action_4)
        toolbar.addAction(action_5)
        toolbar.addAction(action_6)





        #  Tworzenie menuBar: 
        menu = self.menuBar()
    
        # Dodanie menu Plik i dwóch akcji do niego
        file_menu = menu.addMenu("Plik")
        file_menu.addAction(action_1)
        file_menu.addAction(action_2)

        # Dodanie menu Edycja i dwóch akcji do niego
        file_menu = menu.addMenu("Edycja")
        file_menu.addAction(action_1)
        file_menu.addAction(action_3)

        # Dodanie menu Pomoc, to menu jest puste, dadane tylko demonstracyjnie
        file_menu = menu.addMenu("Pomoc")
        
     

######################################################################################
##################################Przyciski###########################################
######################################################################################
      
        # Musi być dodane self przed zmienną pozycję żeby zostały dodane jako atrybut obiektu MainWindow i można było aktualizować 
        # QLabel znajdujący się na pierwszej pozycji listy w innych funkcjach lub obiekcie klasy Obraz_z_kamery.
        # Patrz definicja klasy Obraz_z_kamery, metoda mouseMoveEvent, zczytywanie pozycji przez następujący sposób: self.main_window.pozycje[0].setText(text),
        # gdzie main_window to przekazany przy inicjalizowaniu obiekt MainWindow
        self.pozycje = [ #4
            QLabel('x: 0,  y: 0', self),
            QDoubleSpinBox(),
            QDoubleSpinBox(),
            QDoubleSpinBox()]
            
        
        kierunkowe = [ #4
            QPushButton(),
            QPushButton(),
            QPushButton(),
            QPushButton()]
           
        przyciski = [ #6
            QPushButton(),
            QPushButton(),
            QPushButton(),
            QPushButton(),
            QPushButton(),
            QPushButton()]
         
######################################################################################
##################################Leyout##############################################
######################################################################################        
        
        mainlayout = QHBoxLayout()
        secendarylayout = QVBoxLayout()
        
        pozycjelayout = QGridLayout()
        kierunkowelayout = QGridLayout()
        przyciskilayout = QGridLayout()
        
        
        i = 2
        j = 0
        for w in self.pozycje:
        
            pozycjelayout.addWidget(w,j,i)
            
            i  += 2
            
            if i > 4:
                i = 2
                j +=1
                
        opisy = ["Pozycja:", "Y1", "X2", "Y2"]
        jt = [0,0,1,1]
        it =  [1,3,1,3]
        for t in range(4):
            label = QLabel()
            label.setText(opisy[t])
            label.setAlignment(Qt.AlignRight|Qt.AlignVCenter)
            j = jt[t] #1 3 5 7
            i = it[t]
            pozycjelayout.addWidget(label,  j,int(i),)
           
           
        i = [3,2,4,3]
        j = [2,3,3,4]
        k = 0
        for w in kierunkowe:
        
            kierunkowelayout.addWidget(w,j[k],i[k])
            k  += 1
        
        
        i = 2
        j = 5
        for w in przyciski:
            przyciskilayout.addWidget(w,j,i)
            i += 1
            if i > 4:
                i = 2
                j += 1
        
        
        # Tworzenie instancji klasy Obraz_z_kamery
        self.obraz = Camera()
        mainlayout.addWidget(self.obraz)
        
        secendarylayout.addLayout(pozycjelayout)
        secendarylayout.addLayout(kierunkowelayout)
        secendarylayout.addLayout(przyciskilayout)
                
        mainlayout.addLayout(secendarylayout)
        
        widget = QWidget()
        widget.setLayout(mainlayout)

        self.setCentralWidget(widget)





######################################################################################
##################################Fukcje##############################################
######################################################################################

#toolbar


    def onMyToolBarButtonClick(self, s):
        print("click", s)
        # Odczytywanie pozycji z obiektu obraz i jej wyświetlanie w konsoli:
        print('Ostatnia pozycja: x: {}, y: {}'.format(self.obraz.x, self.obraz.y))
        print()


    def qactiontoolbar(self,nazwa, funkcja): #stworzenie czegos na kształt przycisku ale nie koniecznie muszacego posiadac jeden triger

        Button = QAction(nazwa, self) #stworzenie czegos na kształt przycisku ale nie koniecznie muszacego posiadac jeden triger
        Button.triggered.connect(funkcja) #dodanie trigera

        return Button
    
        
    def closeEvent(self, event):
        self.obraz.close()

        
