import sys
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
# Импортируем всё из библиотек

import random
import time


size = 20
mines = 50  # Размер поля(кведратное), кол-во бомб

IMG_SMILE = QImage('smile.png')
IMG_MINA = QImage('mina.png')
IMG_FLAG = QImage('flag.png')  # Картинки для мин, флажков и смайлик

NUM_COLORS = {1: QColor('#1959d1'), # Цвета для циферков
              2: QColor('#19ff19'),
              3: QColor('#ff0000'),
              4: QColor('#001d18'),
              5: QColor('#321414'),
              6: QColor('#fc6f6f'),
              7: QColor('#ffff00'),
              8: QColor('#000000')}


class Pos(QWidget): # Класс для позиций в поле, каждая из котрых один маленький виджет

    def __init__(self, x, y, *args, **kwargs):
        super(Pos, self).__init__(*args, **kwargs)

        self.setFixedSize(QSize(20, 20)) # Размер позиции
        self.x = x # И её координаты
        self.y = y
        self.is_mine = False  # Мина 
        self.mines_around = 0 # Кол-во бомб вокруг
        self.have_click = False # Нажата или нет
        self.is_flag = False # Флаг

    def reset(self): # При новой игре все парамерты обновляются
        self.is_mine = False 
        self.mines_around = 0
        self.have_click = False
        self.is_flag = False
        self.update()

    def paintEvent(self, event): # Рисуем саму клеточку
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        r = event.rect()

        # Сначала выбираем цвет
        if self.have_click: # Ежели клеточка нажата, то просто делаем её такого же цвета как и само поле
            color = self.palette().color(QPalette.Background)
            out, inn = color, color
        else:
            out, inn = Qt.gray, Qt.lightGray # А иначе сернькую клетку, и тоненькую рамочку чуть темнее

        # Рисуем (только цвет)
        p.fillRect(r, QBrush(inn))  
        pen = QPen(out)
        pen.setWidth(4)
        p.setPen(pen)
        p.drawRect(r)

        # А теперь, если нужно, вставляем картинку (или число)
        if self.have_click:
            if self.is_mine:
                p.drawPixmap(r, QPixmap(IMG_MINA))
                ex.open_map()
            elif self.mines_around > 0:
                pen = QPen(NUM_COLORS[self.mines_around])
                p.setPen(pen)
                f = p.font()
                f.setBold(True)
                p.setFont(f)
                p.drawText(r, Qt.AlignHCenter | Qt.AlignVCenter, str(self.mines_around))
        elif self.is_flag:
            p.drawPixmap(r, QPixmap(IMG_FLAG))

    def flag(self): # Если поставили флажок
        if self.is_flag:
            self.is_flag = False
            ex.change_mines_add()
        else:
            self.is_flag = True
            ex.change_mines()
        self.update()
        ex.start_timer()


    def click(self):  # При клике
        if not self.have_click:
            if ex.button_is_m: # Если открываем клетки
                self.openn()
                if self.mines_around == 0: 
                    ex.open_empty(self.x, self.y)
            else: # если отмечаем мины
                self.flag()
        ex.start_timer()


    def openn(self): # Переключаем что клеточка открыта
        if not self.have_click:
            self.have_click = True
            self.update()
        

    def mouseReleaseEvent(self, e): # Ловим нажатия мышки
        if e.button() == Qt.RightButton and not self.have_click:
            self.flag()

        elif e.button() == Qt.LeftButton:
            if ex.button_is_m:
                if  not self.is_flag and not self.have_click:
                    self.click()
            else:
                if not self.have_click:
                    self.click()
         
        

class Window(QMainWindow):   
    def __init__(self, *args, **kwargs):
        super(QMainWindow, self).__init__(*args, **kwargs)
        
        w = QWidget()
        vb = QVBoxLayout()
        w.setLayout(vb)
        hb4 = QHBoxLayout()
        vb.addLayout(hb4)
        hb2 = QHBoxLayout()
        vb.addLayout(hb2)
        hb3 = QHBoxLayout()
        vb.addLayout(hb3)
        hb1 = QHBoxLayout()
        vb.addLayout(hb1)
        
        self.setWindowTitle('Settings')
        self.setFixedSize(QSize(340, 190))
        
        self.button = QPushButton()
        self.button.setGeometry(QRect(120, 140, 111, 31))
        self.button.setFixedSize(QSize(110, 30))
        self.button.setText('Сохранить')
        self.button.clicked.connect(self.save)

        self.line_1 = QLabel()
        self.line_1.setGeometry(QRect(20, 10, 140, 40))
        font = QFont()
        font.setPointSize(10)
        self.line_1.setFont(font)
        self.line_1.setText('Размеры поля')
        
        self.line_2 = QLabel()
        self.line_2.setGeometry(QRect(180, 10, 140, 40))
        font = QFont()
        font.setPointSize(10)
        self.line_2.setFont(font)
        self.line_2.setText('Количество мин')

        self.spinBox = QSpinBox()
        self.spinBox.setGeometry(QRect(190, 70, 121, 41))
        font = QFont()
        font.setPointSize(14)
        self.spinBox.setFont(font)
        self.spinBox.setCursor(QCursor(Qt.IBeamCursor))
        self.spinBox.setMaximum(30)
        self.spinBox.setMinimum(10)

        self.spinBox_2 = QSpinBox()
        self.spinBox_2.setGeometry(QRect(30, 70, 121, 41))
        font = QFont()
        font.setPointSize(14)
        self.spinBox_2.setFont(font)
        self.spinBox_2.setCursor(QCursor(Qt.IBeamCursor))
        self.spinBox_2.setMaximum(200)
        self.spinBox_2.setMinimum(20)

        self.line_3 = QLabel()
        self.line_3.setText('''Вводите так, что бы количество мин
не было меньше 10 % от количества клеток на поле,
но и не превышало количество клеток''')
        
        hb1.addWidget(self.button)
        hb2.addWidget(self.line_1)
        hb2.addWidget(self.line_2)
        hb3.addWidget(self.spinBox)
        hb3.addWidget(self.spinBox_2)
        hb4.addWidget(self.line_3)
        
        self.setCentralWidget(w)


    def save(self):
        global size
        global mines
        global ex
        size = int(self.spinBox.text())
        mines = int(self.spinBox_2.text())
        if size * size > mines and size * size - mines < size * size * 0.9:
            ex.close()
            ex = MainWindow()
            ex.show()

        

    
class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Строим окошко
        self.setWindowTitle('Sapper')
        self.size = size
        self.mines = mines
        self.setFixedSize(QSize())
        
        w = QWidget()
        hb = QHBoxLayout()
        vb = QVBoxLayout()
        vb.addLayout(hb)

        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.num_of_min = QLCDNumber()
        self.num_of_min.setGeometry(QRect(0, 0, 400, 40))
        self.num_of_min.setDigitCount(5)
        self.num_of_min.setProperty("intValue", self.mines)
        
        self.button_new_game = QPushButton()
        self.button_new_game.setFixedSize(QSize(40, 40))
        self.button_new_game.setIconSize(QSize(40, 40))
        self.button_new_game.setIcon(QIcon('smile.png'))
        self.button_new_game.clicked.connect(self.new_game)

        self.button_f_or_m = QPushButton()
        self.button_f_or_m.setFixedSize(QSize(40, 40))
        self.button_f_or_m.setIconSize(QSize(30, 30))
        self.button_f_or_m.setIcon(QIcon('mina.png'))
        self.button_is_m = True
        self.button_f_or_m.clicked.connect(self.change_icon)

        self.button_set = QPushButton()
        self.button_set.setFixedSize(QSize(40, 40))
        self.button_set.setIconSize(QSize(30, 30))
        self.button_set.setIcon(QIcon('set.png'))
        self.button_set.clicked.connect(self.open_set)

        self.times = QLCDNumber()
        self.times.setGeometry(QRect(0, 0, 500, 40))
        self.times.setDigitCount(5)
        self.times.setProperty("intValue", 0)
        self.start = False

        
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_timer)
        self.timer.start(1000)
        self.times.display("0:00")


        hb.addWidget(self.times)
        hb.addWidget(self.button_set)
        hb.addWidget(self.button_new_game)
        hb.addWidget(self.button_f_or_m)
        hb.addWidget(self.num_of_min)
        hb.setGeometry(QRect(0, 0, 100, 40))

        self.init_map()
        self.reset_map()
        self.show()


    def init_map(self):
        # Просто создаем поле
        for x in range(self.size):
            for y in range(self.size):
                w = Pos(x, y)
                self.grid.addWidget(w, y, x)

    def reset_map(self):
        # Тут обновляем
        for x in range(self.size):
            for y in range(self.size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reset()

        self.start = False
        self.times.display('0:00')
        self.mines = mines # Обновляем окошко с минами
        self.num_of_min.display(self.mines)
        
        # А тут впёхиваем мины 
        positions = []
        while len(positions) < self.mines:
            x, y = random.randint(0, self.size - 1), random.randint(0, self.size - 1)
            if (x, y) not in positions:
                w = self.grid.itemAtPosition(y, x).widget()
                w.is_mine = True
                positions.append((x, y))

        for x in range(self.size): # Узнаём кол-во мин вокруг каждой клетки
            for y in range(self.size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.mines_around = self.find_mines(x, y) 

    def find_mines(self, x, y):
        mines = 0
        positions = self.pos_around(x, y)  # Смотрим какие позиции вокруг
        for w in positions: # И запоминаем сколько мин
            if w.is_mine:
                mines += 1
        return mines                

    def pos_around(self, x, y):  # Запоминаем позици вокруг
        positions = []
        for i in range(max(0, x - 1), min(x + 2, self.size)):  # Вот это в скобочках, это для того, чтобы не заходить за поля
            for j in range(max(0, y - 1), min(y + 2, self.size)):
                if self.grid.itemAtPosition(j, i).widget() not in positions:
                    positions.append(self.grid.itemAtPosition(j, i).widget())
        return positions

    def open_map(self): # Открываем карту в конце
        self.start = False
        for x in range(self.size):
            for y in range(self.size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.openn()

    def open_empty(self, x, y):  # Открывааем пустые клетки
        for i in range(max(0, x - 1), min(x + 2, self.size)):
            for j in range(max(0, y - 1), min(y + 2, self.size)):
                w = self.grid.itemAtPosition(j, i).widget()
                if not w.is_mine:
                    w.click()
    
    def change_icon(self): # Меняем - открывем клетки или ставим флаг
        if self.button_is_m:
            self.button_f_or_m.setIcon(QIcon('flag.png'))
            self.button_is_m = False
        else:
            self.button_f_or_m.setIcon(QIcon('mina.png'))
            self.button_is_m = True

    def change_mines(self): # Этой и следующей функцией меняем кол-во мин
        self.mines -= 1
        self.num_of_min.display(self.mines)
        
    def change_mines_add(self):
        self.mines += 1
        self.num_of_min.display(self.mines)

    def new_game(self): # Новая игра
        self.reset_map()

    def start_timer(self):
        if not self.start:
            self.start = True
            self.start_time = int(time.time())
    
    def update_timer(self):
        if self.start:
            t = int(time.time()) - self.start_time
            m = t//60
            s = t%60
            self.times.display('{}:{}'.format(m, s))


    def open_set(self):
        sets.show()
                           
        
 
app = QApplication(sys.argv)
ex = MainWindow()
sets = Window()
ex.show()
sys.exit(app.exec_())
