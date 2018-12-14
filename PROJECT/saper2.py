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

    expandable = pyqtSignal(int, int)
    clickedd = pyqtSignal()
    ohno = pyqtSignal()    

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
        self.clickedd.emit()


    def click(self):  # При клике
        if not self.have_click:
            if ex.button_is_m: # Если открываем клетки
                self.openn()
                if self.mines_around == 0: 
                    self.expandable.emit(self.x, self.y)
            else: # если отмечаем мины
                self.flag()
        self.clickedd.emit()


    def openn(self): # Переключаем что клеточка открыта
        if not self.have_click:
            self.have_click = True
            self.update()
        

    def mouseReleaseEvent(self, b): # Ловим нажатия мышки
        if ex.button_is_m:
            if  not self.is_flag and not self.have_click:
                self.click()
        else:
            if not self.have_click:
                self.click()


class MainWindow(QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        # Строим окошко
        self.size = size
        self.mines = mines
        self.setFixedSize(QSize())
        
        w = QWidget()
        hb = QHBoxLayout()
        l = QLabel()
        hb.addWidget(l)
        
        vb = QVBoxLayout()
        vb.addLayout(hb)

        self.grid = QGridLayout()
        self.grid.setSpacing(1)
        vb.addLayout(self.grid)
        w.setLayout(vb)
        self.setCentralWidget(w)

        self.num_of_min = QLCDNumber()
        self.num_of_min.setGeometry(QRect(0, 0, 400, 40))
        self.num_of_min.setDigitCount(4)
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

        
        hb.addWidget(self.button_new_game)
        hb.addWidget(self.num_of_min)
        hb.addWidget(self.button_f_or_m)
        hb.setGeometry(QRect(0, 0, 200, 40))

        
        self.init_map()
        self.reset_map()
        self.show()


    def init_map(self):
        # Просто создаем поле
        for x in range(self.size):
            for y in range(self.size):
                w = Pos(x, y)
                self.grid.addWidget(w, y, x)
                w.expandable.connect(self.open_empty)

    def reset_map(self):
        # Тут обновляем
        for x in range(self.size):
            for y in range(self.size):
                w = self.grid.itemAtPosition(y, x).widget()
                w.reset()
                
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
        

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    sys.exit(app.exec_())
