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




sys.path.append('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/widgets/tools')

from rasterize import Rasterize


class Rasterize_ui(QWidget):

    def __init__(self):
        super().__init__()

        self.shapefile_path_group = QGroupBox()
        shapefile_path_group_layout = QVBoxLayout()
        self.shapefile_path_group.setTitle('Shapefile path')
        self.shapefile_path_group.setLayout(shapefile_path_group_layout)
        self.shapefile_path_line = lineedit()
        self.shapefile_path_line.setText('/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/thematic.shp')
        shapefile_path_group_layout.addWidget(self.shapefile_path_line)

        self.out_raster_path_group = QGroupBox()
        out_raster_path_group_layout = QVBoxLayout()
        self.out_raster_path_group.setTitle('Output Raster path')
        self.out_raster_path_group.setLayout(out_raster_path_group_layout)
        self.out_raster_path_line = lineedit()
        self.out_raster_path_line.setText('/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/')
        out_raster_path_group_layout.addWidget(self.out_raster_path_line)

        self.reference_raster_group = QGroupBox()
        reference_raster_group_layout = QVBoxLayout()
        self.reference_raster_group.setTitle('Reference raster')
        self.reference_raster_group.setLayout(reference_raster_group_layout)
        self.reference_raster_line = lineedit()
        self.reference_raster_line.setText('/home/inbal/inbal/gdal/outputs/rasterize/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_5.0_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif')
        reference_raster_group_layout.addWidget(self.reference_raster_line)

        self.out_raster_name_group = QGroupBox()
        out_raster_name_group_layout = QVBoxLayout()
        self.out_raster_name_group.setTitle('Output raster name')
        self.out_raster_name_group.setLayout(out_raster_name_group_layout)
        self.out_raster_name_line = lineedit()
        self.out_raster_name_line.setText('predicted_raster.tif')
        out_raster_name_group_layout.addWidget(self.out_raster_name_line)

        self.field_name_group = QGroupBox()
        field_name_group_layout = QVBoxLayout()
        self.field_name_group.setTitle('Field name')
        self.field_name_group.setLayout(field_name_group_layout)
        self.field_name_line = QLineEdit()
        self.field_name_line.setText('id')
        field_name_group_layout.addWidget(self.field_name_line)

        self.lables_file_group = QGroupBox()
        lables_file_group_layout = QVBoxLayout()
        self.lables_file_group.setTitle('Labels file')
        self.lables_file_group.setLayout(lables_file_group_layout)
        self.lables_file_line = QLineEdit()
        self.lables_file_group.setCheckable(True)
        self.lables_file_group.setChecked(False)
        lables_file_group_layout.addWidget(self.lables_file_line)


        self.button_box = QDialogButtonBox()
        self.rasterizebottun = self.button_box.addButton('Rasterize', QDialogButtonBox.NoRole)


        self.newraster = None




        layout = QVBoxLayout()
        layout.addWidget(self.shapefile_path_group)
        layout.addWidget(self.out_raster_path_group)
        layout.addWidget(self.reference_raster_group)
        layout.addWidget(self.out_raster_name_group)
        layout.addWidget(self.field_name_group)
        layout.addWidget(self.lables_file_group)
        layout.addWidget(self.button_box)

        self.setLayout(layout)

        self.poly = None
        self.legendwidget = None

        self.rasterizebottun.clicked.connect(self.run)

    def collect_users_input(self):
        shapefile_path_line = self.shapefile_path_line.text()
        out_raster_path = self.out_raster_path_line.text()
        reference_raster = self.reference_raster_line.text()
        out_raster_name = self.out_raster_name_line.text()
        field_name = self.field_name_line.text()
        lables_file = self.lables_file_line.text()
        self.newraster = out_raster_path + out_raster_name

        self.ras = Rasterize(shapefile_path_line, out_raster_path, reference_raster, out_raster_name=out_raster_name,
                             field_name = field_name, lables_file = None)


    def clear(self):
        self.shapefile_path_line.clear()
        self.out_raster_path_line.clear()
        self.reference_raster_line.clear()
        self.out_raster_name_line.clear()
        self.field_name_line.clear()
        self.lables_file_line.clear()

    def load_results_to_canvas(self):

        self.legendwidget.add_to_canvas([self.newraster])



    def run(self):
        shapefile_path_line = self.shapefile_path_line.text()
        out_raster_path = self.out_raster_path_line.text()
        reference_raster = self.reference_raster_line.text()
        out_raster_name = self.out_raster_name_line.text()
        field_name = self.field_name_line.text()
        lables_file = self.lables_file_line.text()
        self.newraster = out_raster_path + out_raster_name

        ras = Rasterize(shapefile_path_line, out_raster_path, reference_raster, out_raster_name= out_raster_name,
                        field_name=field_name, lables_file=None)
        self.clear()
