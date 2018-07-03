from PyQt5.QtGui import QFont, QStandardItemModel, QDropEvent, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QGroupBox,\
    QPushButton, QLineEdit, QWidget, QFrame, QLabel, QListWidget, QApplication, QFileSystemModel,QTreeView,\
    QListView, QListWidgetItem, QAbstractItemView, QMenuBar, QAction, QMenu, QCheckBox, QListWidgetItem, QMessageBox,\
    QCheckBox, QTreeWidget, QTreeWidgetItem, QGraphicsView, QFileDialog
import sys
from qgis.core import *
from qgis.gui import *
import gdal
import os
import ast
import subprocess
import threading as thr

from costum_widgets import  map_canvas, LayersPanel, datatreeview, bands_pairing, listview, lineedit
import fileinput



sys.path.append('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/widgets/tools')

from polygonize import Polygonize


class Polygonize_ui(QWidget):
    def __init__(self):
        super().__init__()

        self.raster_path_group = QGroupBox()
        raster_path_group_layout = QVBoxLayout()
        self.raster_path_group.setTitle('Raster path')
        self.raster_path_group.setLayout(raster_path_group_layout)
        self.raster_path_line = lineedit()
        self.raster_path_line.setText('/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif')
        raster_path_group_layout.addWidget(self.raster_path_line)

        self.costumelabels_group = QGroupBox()
        self.costumelabels_group.setCheckable(True)
        costumelabels_group_layout = QVBoxLayout()
        self.costumelabels_group.setTitle('Set costume labels')
        self.costumelabels_group.setLayout(costumelabels_group_layout)
        self.costumelabels = QListWidget()
        costumelabels_group_layout.addWidget(self.costumelabels)

        self.labels_path_group = QGroupBox()
        labels_path_group_layout = QVBoxLayout()
        self.labels_path_group.setTitle('Labels file')
        self.labels_path_group.setLayout(labels_path_group_layout)
        self.labels_path = lineedit()
        self.labels_path.setText('/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm.lbl')
        labels_path_group_layout.addWidget(self.labels_path)

        self.shapefile_path_group = QGroupBox()
        shapefile_path_group_layout = QVBoxLayout()
        self.shapefile_path_group.setTitle('Output path')
        self.shapefile_path_group.setLayout(shapefile_path_group_layout)
        self.shapefile_path = lineedit()
        self.shapefile_path.setText('/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/')
        shapefile_path_group_layout.addWidget(self.shapefile_path)

        self.layer_name_group = QGroupBox()
        layer_name_group_layout = QVBoxLayout()
        self.layer_name_group.setTitle('Layer name')
        self.layer_name_group.setLayout(layer_name_group_layout)
        self.layer_name = QLineEdit()
        self.layer_name.setText('thematic')
        layer_name_group_layout.addWidget(self.layer_name)

        self.class_name_group = QGroupBox()
        class_name_group_layout = QVBoxLayout()
        self.class_name_group.setTitle('Class name')
        self.class_name_group.setLayout(class_name_group_layout)
        self.class_name = QLineEdit()
        self.class_name.setText('class')
        class_name_group_layout.addWidget(self.class_name)

        self.idfield_group = QGroupBox()
        idfield_group_layout = QVBoxLayout()
        self.idfield_group.setTitle('Field')
        self.idfield_group.setLayout(idfield_group_layout)
        self.idfield = QLineEdit()
        self.idfield.setText('id')
        idfield_group_layout.addWidget(self.idfield)


        self.button_box = QDialogButtonBox()
        self.poligonizebottun = self.button_box.addButton('Poligonize', QDialogButtonBox.NoRole)

        #self.message = QMessageBox()
        #self.message.setWindowTitle('Polygonize')
        #self.message.setText('Running,pleas wait')
        #self.message.setStyleSheet("background-color: white")


        layout = QVBoxLayout()
        layout.addWidget(self.raster_path_group)
        layout.addWidget(self.costumelabels_group)
        layout.addWidget(self.labels_path_group)
        layout.addWidget(self.shapefile_path_group)
        layout.addWidget(self.layer_name_group)
        layout.addWidget(self.class_name_group)
        layout.addWidget(self.idfield_group)
        layout.addWidget(self.idfield_group)
        layout.addWidget(self.button_box)


        self.setLayout(layout)

        self.poly = None
        self.legendwidget = None

        self.poligonizebottun.clicked.connect(self.run)




    def collect_users_input(self):

        rasterpath = self.raster_path_line.text()
        labels = self.labels_path.text()
        shapefile_path = self.shapefile_path.text()
        layer_name = self.layer_name.text()
        class_name = self.class_name.text()
        idfield = self.idfield.text()

        self.poly = Polygonize(raster_path=rasterpath, labels_path=labels, shapefile_path=shapefile_path,
                           layer_name=layer_name, class_name=class_name, idfield = idfield)

    def clear(self):
        self.raster_path_line.clear()
        self.labels_path.clear()
        self.shapefile_path.clear()
        self.costumelabels.clear()
        self.layer_name.clear()
        self.class_name.clear()
        self.idfield.clear()

    def run(self):
        self.collect_users_input()
        self.poly.polygonize()
        newlayer = self.poly.output_shp + self.poly.layer_name + '.shp'
        print (newlayer)
        self.legendwidget.add_to_canvas([newlayer])
        self.clear()









