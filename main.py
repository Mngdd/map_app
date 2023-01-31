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

        self.getImage()

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

    def get_pos(self, address):
        geocoder_request = "http://geocode-maps.yandex.ru/1.x/"
        geo_params = {'apikey': api_key, 'geocode': address, 'format': 'json'}
        geo_response = requests.get(geocoder_request, params=geo_params)
        json_response = geo_response.json()

        data = json_response["response"]["GeoObjectCollection"]["featureMember"][0]["GeoObject"]
        cords = list(map(float, data['Point']['pos'].split()))
        return cords

    def getImage(self):
        map_request = "http://static-maps.yandex.ru/1.x/?ll=37.530887,55.703118&spn=0.002,0.002&l=map"
        response = requests.get(map_request)

        if not response:
            print("Ошибка выполнения запроса:")
            print(map_request)
            print("Http статус:", response.status_code, "(", response.reason, ")")
            sys.exit(1)

        self.img = ImageQt.ImageQt(Image.open(BytesIO(response.content)))
        self.label.setPixmap(QPixmap.fromImage(self.img))


if __name__ == '__main__':
    api_key = '40d1649f-0493-4b70-98ba-98533de7710b'
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
