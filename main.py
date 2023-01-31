import sys
from io import BytesIO

import requests
from PIL import Image, ImageQt
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import Qt
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QMainWindow, QLineEdit

SCREEN_SIZE = [600, 450]


class MainWindow(QMainWindow):
    coord_edit: QLineEdit
    result_coord_lbl: QLabel

    def __init__(self):
        super().__init__()
        uic.loadUi('main_window.ui', self)
        self.ll = [37.530887, 55.703118]
        self.z = 16
        self.points = []

        self.l = 'map'

        self.params = {'ll': '37.530887,55.703118', 'z': 1, 'l': 'map'}
        self.getImage()

        self.sheme_btn.clicked.connect(self.set_l('map'))
        self.sputnik_btn.clicked.connect(self.set_l('sat'))
        self.sputnik_btn.clicked.connect(self.set_l('sat,skl'))

        self.getImage()
        self.search_btn.clicked.connect(self.search)
        self.sbros_btn.clicked.connect(self.sbros)

        self.sheme_btn.clicked.connect(self.set_l('map'))
        self.sputnik_btn.clicked.connect(self.set_l('sat'))
        self.sputnik_btn.clicked.connect(self.set_l('sat,skl'))

    def set_l(self, l: str):
        def inner():
            self.l = l
            self.getImage()
        return inner

    def sbros(self):
        if len(self.points) >= 1:
            self.points.pop(-1)
        self.result_coord_lbl.setText('')
        self.getImage()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageDown:
            self.params['z'] = self.params['z'] - 2 if self.params['z'] - 2 >= 0 else 0
        if event.key() == Qt.Key_PageUp:
            self.params['z'] = self.params['z'] + 2 if self.params['z'] + 2 <= 17 else 17
        if event.key() == Qt.Key_Left:
            self.move_ll(x=-0.5)
        if event.key() == Qt.Key_Up:
            self.move_ll(y=0.5)
        if event.key() == Qt.Key_Down:
            self.move_ll(y=-0.5)
        if event.key() == Qt.Key_Right:
            self.move_ll(x=0.5)
        self.getImage()

    def move_ll(self, x=0.0, y=0.0):
        self.params['ll'] = f"{float(self.params['ll'].split(',')[0]) + x},{float(self.params['ll'].split(',')[1]) +y}"

    def set_l(self, l_: str):
        def inner():
            self.params['l'] = l_
            self.getImage()

        return inner

    def getImage(self):
        map_request = f"http://static-maps.yandex.ru/1.x/"
        response = requests.get(map_request, params=self.params)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.label.setPixmap(QPixmap.fromImage(self.img))

    def find(self, address: str, search_for: str = False, spn: str = False):
        cords = self.get_pos(address)
        map_params = {'l': 'sat', 'll': f"{cords[0]},{cords[1]}"}
                      # 'pt': '~'.join([el + ',pm2blm1' for el in [pharmacy, ','.join(map(str, cords))]])}
        if spn:
            map_params['spn'] = spn
        map_request = "http://static-maps.yandex.ru/1.x/"
        map_response = requests.get(map_request, params=map_params)
        if map_response:
            return map_response
        else:
            print("Ошибка выполнения запроса:")
            print("Http статус:", map_response.status_code, "(", map_response.reason, ")")
    def search(self):
        print(self.ll)
        address = self.coord_edit.text()
        try:
            self.ll = self.get_pos(address)
        except IndexError:  # нет такого
            return
        self.points.append(tuple(self.ll))
        self.getImage()
        self.result_coord_lbl.setText(self.get_normal_address(address))

        self.sheme_btn.clicked.connect(self.set_l('map'))
        self.sputnik_btn.clicked.connect(self.set_l('sat'))
        self.sputnik_btn.clicked.connect(self.set_l('sat,skl'))

    def set_l(self, l: str):
        def inner():
            self.l = l
            self.getImage()
        return inner

    def get_pos(self, address):
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
        geo_params = {'apikey': api_key, 'geocode': address, 'format': 'json'}
        geo_response = requests.get(geocoder_request, params=geo_params)
        json_response = geo_response.json()

        data = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        cords = list(map(float, data['Point']['pos'].split()))
        return cords

    def get_normal_address(self, address):
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
        geo_params = {'apikey': api_key, 'geocode': address, 'format': 'json'}
        geo_response = requests.get(geocoder_request, params=geo_params)
        json_response = geo_response.json()

        data = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        return data['metaDataProperty']['GeocoderMetaData']['text']

    def getImage(self):
        pt = '~'.join(','.join(map(str, point)) for point in self.points)
        map_request = f"http://static-maps.yandex.ru/1.x/?ll={','.join(map(str, self.ll))}&l={self.l}&z={self.z}&pt={pt}"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.map.setPixmap(QPixmap.fromImage(self.img))


if __name__ == '__main__':
    print(','.join(map(str, [37.530887, 55.703118])))
    api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
