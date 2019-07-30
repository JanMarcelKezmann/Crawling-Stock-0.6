import sys
import requests
import math
import re
#import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from bs4 import BeautifulSoup
from qtpy import QtWidgets
from PyQt5.QtCore import Qt

from ui.mainwindow import Ui_MainWindow

app = QtWidgets.QApplication(sys.argv)

url = "https://www.ariva.de"

number = 6

class Canvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=200):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)

        FigureCanvas.__init__(self, fig)
        self.setParent(parent)

        self.plotter()

    def plotter(self):
        x = [50, 30, 40]
        labels = ["Apples", "Bananas", "Melons"]
        ax = self.figure.add_subplot(111)
        ax.pie(x, labels=labels)


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, parent=None, list_of_companies=[], the_company=[], sorted_matrice=[], input_urls=[], row=0,
                 modnumber=0, chosen="", financials="", value="", complete_financials=[]):
        super().__init__(parent)
        self.list_of_companies = list_of_companies
        self.the_company = the_company
        self.sorted_matrice = sorted_matrice
        self.row = row
        self.chosen = chosen
        self.input_urls = input_urls
        self.financials = financials
        self.value = value
        self.modnumber = modnumber
        self.complete_financials = complete_financials

        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.MYUI()

        self.ui.pushButton.clicked.connect(self.disp_input)
        self.ui.pushButton2.clicked.connect(self.clickedStock)

        self.ui.error_info.hide()
        self.ui.error_info_2.hide()
        self.ui.error_info_3.hide()

        self.ui.tableWidget.hide()
        self.ui.pushButton2.hide()
        self.ui.restart.hide()

    def disp_input(self):
        if self.ui.lineEdit.text() == "":
            pass
        else:
            self.returnInputResults()

            self.ui.tableWidget.show()
            self.ui.pushButton2.show()
            self.ui.pushButton.hide()
            self.ui.restart.hide()

            self.newRow()
        return

    def MYUI(self):

        canvas = Canvas(self, width=8, height=4)
        canvas.move(0, 0)

       # button = QPushButton("click me", self)
       # button.move(100, 450)

       # button2 = QPushButton("click me next", self)
       # button2.move(250, 450)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Enter or event.key() == Qt.Key_Return:
            self.disp_input

    def clickedStock(self):
        if self.ui.tableWidget.currentItem() == None:
            self.ui.error_info_2.show()
            return
        else:
            if not self.ui.error_info_2.isHidden():
                self.ui.error_info_2.hide()
            # get the clicked company
            self.chosen = self.ui.tableWidget.currentItem().text()
            self.row = self.ui.tableWidget.currentItem().row()

            # erase the TableWidget and set a new title
            while self.ui.tableWidget.rowCount() > 0:
                self.ui.tableWidget.removeRow(0)
            self.ui.tableWidget.setHorizontalHeaderItem(0, QtWidgets.QTableWidgetItem("Indicators"))

            self.goToStockPage()

            #self.getSortedMatrice(url)
            return

    def newRow(self):
        for i in range(0, len(self.list_of_companies)):
            rows = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(rows)
            self.ui.tableWidget.setItem(rows, 0, QtWidgets.QTableWidgetItem(self.list_of_companies[i]))
        return

    def returnInputResults(self):
        newurl = url + "/search/search.m?searchname=" + self.ui.lineEdit.text()
        print(newurl)
        # build self.ui.error_info.show() into the return input result function

        r = requests.get(newurl)
        doc = BeautifulSoup(r.text, "html.parser")

        for i in doc.select("tbody a"):
            self.list_of_companies.append(i.text)
            self.input_urls.append(i.attrs["href"])

        #print(self.list_of_companies)
        return

    def goToStockPage(self):
        self.ui.pushButton2.hide()

        newurl = url + self.input_urls[self.row]
        print(newurl)

        r = requests.get(newurl)
        doc = BeautifulSoup(r.text, "html.parser")

        for i in doc.select("#pageSnapshotHeader #reiter_Profilseite li a"):
            if i.text == "Kennzahlen":
                print("Es gibt Kennzahlen zu diesem Unternehmen")
                self.financials = i.attrs["href"]

                self.goToFinancials()
                return
        if self.financial == "":
            self.ui.error_info_3.show()
            return

    def goToFinancials(self):
        newurl2 = url + self.financials
        print(newurl2)

        r = requests.get(newurl2)
        doc = BeautifulSoup(r.text, "html.parser")

        tempmax = 0
        for i in doc.select("#pageFundamental select option"):
            if int(i.attrs["value"]) > tempmax:
                tempmax = int(i.attrs["value"])
                self.value = i.attrs["value"]

        self.modnumber = math.floor(tempmax / number)

        # crawle alle Werte der letzten self.value Jahre

        for i in range(0, self.modnumber + 2):
            if i == 0:
                store_temp1 = self.crawl(doc, i)
            elif i == self.modnumber + 1:
                store_temp4 = self.crawl(doc, i)
            elif i == 1:
                store_temp2 = self.crawl(doc, i)
            elif i == 2:
                store_temp3 = self.crawl(doc, i)

        self.complete_financials = store_temp4

        for i in range(0, len(self.complete_financials)):
            if self.modnumber == 2:
                for j in range(0, 6):
                    self.complete_financials[i].append(store_temp3[i][j])
                    self.complete_financials[i].append(store_temp2[i][j])
                    if j != 5:
                        self.complete_financials[i].append(store_temp1[i][j])
            elif self.modnumber == 1:
                for j in range(0, 6):
                    self.complete_financials[i].append(store_temp2[i][j])
                    if j != 5:
                        self.complete_financials[i].append(store_temp1[i][j])
            else:
                for j in range(0, 5):
                    self.complete_financials[i].append(store_temp1[i][j])
        print(self.complete_financials)
        return

    def crawl(self, doc, i):
        div1 = ".tabelleUndDiagramm.guv.new.abstand tbody tr td.right"
        div2 = ".tabelleUndDiagramm.aktie.new.abstand tbody tr td.right"
        div3 = ".tabelleUndDiagramm.personal.new.abstand tbody tr td.right"
        div4 = ".tabelleUndDiagramm.bewertung.new.abstand tbody tr td.right"

        div = [div1, div2, div3, div4]

        if i == 0:
            store_temp1 = []
            # crawl the first page
            # therefor crawl everything except the current year's column
            for j in div:
                fixer = 6
                counter = 1
                tempnumber = []
                for i in doc.select(j):
                    if i.attrs["class"] == ["right", "year"]:
                        continue
                    else:
                        if counter % fixer == 0:
                            counter += 1
                            store_temp1.append(tempnumber)
                            tempnumber = []
                            continue
                        elif (i.text == "-   " and counter % fixer != 0) or (i.text == " " and counter % fixer != 0):
                            tempnumber.append(0)
                        elif re.findall("[M]", i.text):
                            temp = i.text.replace(",", "")
                            temp = temp.replace("M", "")
                            temp = temp.replace(" ", "")
                            temp = temp + "0000"
                            temp = temp.replace(" ", "")
                            tempnumber.append(float(temp))
                        else:
                            temp = i.text.replace(".", "")
                            temp = temp.replace(",", ".")
                            tempnumber.append(float(temp))

                    counter += 1

            return store_temp1
        elif i == self.modnumber + 1:
            temp_mod = int(self.value) % 6
            newurl3 = url + self.financials + "?page=" + str((i - 1) * number + (temp_mod))
            print(newurl3)
            r = requests.get(newurl3)
            temp_doc = BeautifulSoup(r.text, "html.parser")

            store_temp2 = []
            # crawl the first page
            # therefor crawl everything except the current year's column
            for j in div:
                fixer = 6
                counter = 1
                tempnumber = []
                for i in temp_doc.select(j):
                    if i.attrs["class"] == ["right", "year"]:
                        continue
                    elif counter > temp_mod:
                        pass
                    else:
                        if i.text == "-   " or i.text == " ":
                            tempnumber.append(0)
                        elif re.findall("[M]", i.text):
                            temp = i.text.replace(",", "")
                            temp = temp.replace("M", "")
                            temp = temp.replace(" ", "")
                            temp = temp + "0000"
                            temp = temp.replace(" ", "")
                            tempnumber.append(float(temp))
                        else:
                            temp = i.text.replace(".", "")
                            temp = temp.replace(",", ".")
                            tempnumber.append(float(temp))

                    if counter % fixer == temp_mod:
                        store_temp2.append(tempnumber)
                        tempnumber = []
                    if counter == 6:
                        counter = 0

                    counter += 1

            return store_temp2

        elif i == 1 or i == 2:
            newurl3 = url + self.financials + "?page=" + str(i * number)
            print(newurl3)
            r = requests.get(newurl3)
            temp_doc = BeautifulSoup(r.text, "html.parser")

            store_temp2 = []
            # crawl the first page
            # therefor crawl everything except the current year's column
            for j in div:
                fixer = 6
                counter = 1
                tempnumber = []
                for i in temp_doc.select(j):
                    if i.attrs["class"] == ["right", "year"]:
                        continue
                    else:
                        if i.text == "-   " or i.text == " ":
                            tempnumber.append(0)
                        elif re.findall("[M]", i.text):
                            temp = i.text.replace(",", "")
                            temp = temp.replace("M", "")
                            temp = temp.replace(" ", "")
                            temp = temp + "0000"
                            temp = temp.replace(" ", "")
                            tempnumber.append(float(temp))
                        else:
                            temp = i.text.replace(".", "")
                            temp = temp.replace(",", ".")
                            tempnumber.append(float(temp))

                    if counter % fixer == 0:
                        store_temp2.append(tempnumber)
                        tempnumber = []
                    counter += 1

            return store_temp2



window = MainWindow()
window.show()

sys.exit(app.exec_())
