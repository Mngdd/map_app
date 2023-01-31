import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow

SCREEN_SIZE = [600, 450]


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)

        self.l = 'map'

        self.getImage()

        self.sheme_btn.clicked.connect(self.set_l('map'))
        self.sputnik_btn.clicked.connect(self.set_l('sat'))
        self.sputnik_btn.clicked.connect(self.set_l('sat,skl'))

    def set_l(self, l: str):
        def inner():
            self.l = l
            self.getImage()
        return inner

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/?ll=37.530887,55.703118&spn=0.002,0.002&l={self.l}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.label.setPixmap(QPixmap.fromImage(self.img))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
