from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMessageBox, QDialog
from PyQt5.QtWidgets import QTableWidgetItem

from requests import get, put, post

from desktop import URL, UI_PATH

 
class Material(QDialog):
    def __init__(self, mode='a', m_id=1):
        super().__init__()
        uic.loadUi(UI_PATH + '/material.ui', self)

        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.ok.clicked.connect(self.adding)
        self.closing.clicked.connect(self.close)

        self.mode = mode
        self.id = m_id

        if self.mode == 'p':
            self.load() 

    def adding(self):
        title = self.title.text()
        price = self.price.value()
        waste = self.waste.value()

        if title == '' or price == 0.0 or waste == 0.0:
            QMessageBox.warning(self, 'Ошибка', 'Заполнены не все поля')
        else:
            if self.mode == 'p':
                put(URL + f'/api/material/{self.id}?title={title}&waste_coef={waste}&price={price}')
                self.close()
            elif self.mode == 'a':
                post(URL + f'/api/material/0?title={title}&waste_coef={waste}&price={price}')
                self.close()

    def load(self):
        material = get(URL + f'/api/material/{self.id}').json()['result']['material']

        self.title.setText(material['title'])
        self.price.setValue(material['price'])
        self.waste.setValue(material['waste_coef'])


class Materials(QDialog):
    def __init__(self):
        super().__init__()
        uic.loadUi(UI_PATH + 'materials.ui', self)
        
        self.setWindowFlag(Qt.WindowContextHelpButtonHint, False)

        self.table.cellClicked.connect(self.row_focus)
        self.table.cellDoubleClicked.connect(self.edit_material)

        self.fields = 0
        self.load()

    def row_focus(self):  # select all column of chosen film
        for i in range(self.fields):
            self.table.item(self.table.currentRow(), i).setSelected(True)

    def edit_material(self):
        self.row_focus()

        m_id = self.table.currentItem().data(Qt.UserRole)

        window = Material(mode='p', m_id=m_id)
        window.exec()

        self.load()

    def load(self):
        materials = get(URL + f'/api/materials?ids=all').json()['result']['materials']

        if not materials:
            QMessageBox.warning(self, 'Внимание', 'Материалов нет')
            return

        self.fields = len(materials[0].keys()) - 1

        self.table.setColumnCount(self.fields)
        self.table.setHorizontalHeaderLabels(('Название', 'Цена', 'Отходы, %'))

        self.table.setRowCount(0)
        for i, material in enumerate(materials):
            self.table.setRowCount(self.table.rowCount() + 1)

            item = QTableWidgetItem(material['title'])
            item.setData(Qt.UserRole, material['id'])
            self.table.setItem(i, 0, item)

            item = QTableWidgetItem(str(material['price']))
            item.setData(Qt.UserRole, material['id'])
            self.table.setItem(i, 1, item)

            item = QTableWidgetItem(str(material['waste_coef']))
            item.setData(Qt.UserRole, material['id'])
            self.table.setItem(i, 2, item)

        self.table.resizeColumnsToContents()
