from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QGroupBox,\
    QLineEdit, QWidget, QApplication, QMessageBox
from PyQt5.QtCore import QProcess,QThread,QThreadPool,QRunnable,pyqtSignal, QObject

import sys
from qgis.core import *
from qgis.gui import *
from costum_widgets import  map_canvas, LayersPanel, datatreeview, inputlistwidget, lineedit, massagewidget, MyQProcess
import ast

sys.path.append('./widgets/tools')

class Polygonize_ui(QWidget):
    running = pyqtSignal(name='running')
    def __init__(self):
        super().__init__()
        """this is a widget for poligonizing a raster"""

        # qline for adding the raster path
        self.raster_path_group = QGroupBox()
        raster_path_group_layout = QVBoxLayout()
        self.raster_path_group.setTitle('Raster path')
        self.raster_path_group.setLayout(raster_path_group_layout)
        self.raster_path_line = lineedit()
        self.raster_path_line.setText('/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif')
        raster_path_group_layout.addWidget(self.raster_path_line)

        # qline for adding labels
        self.costumelabels_group = QGroupBox()
        self.costumelabels_group.setCheckable(True)
        self.costumelabels_group.setChecked(False)
        costumelabels_group_layout = QVBoxLayout()
        self.costumelabels_group.setTitle('Set costume labels')
        self.costumelabels_group.setLayout(costumelabels_group_layout)
        self.costumelabels = QLineEdit()
        costumelabels_group_layout.addWidget(self.costumelabels)

        # qline for adding the path for the labels files
        self.labels_path_group = QGroupBox()
        labels_path_group_layout = QVBoxLayout()
        self.labels_path_group.setTitle('Labels file')
        self.labels_path_group.setLayout(labels_path_group_layout)
        self.labels_path = lineedit()
        self.labels_path.setText('/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm.lbl')
        labels_path_group_layout.addWidget(self.labels_path)

        # qline for adding the path for the output shapefile
        self.shapefile_path_group = QGroupBox()
        shapefile_path_group_layout = QVBoxLayout()
        self.shapefile_path_group.setTitle('Output path')
        self.shapefile_path_group.setLayout(shapefile_path_group_layout)
        self.shapefile_path = lineedit()
        self.shapefile_path.setText('/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/')
        shapefile_path_group_layout.addWidget(self.shapefile_path)

        # qline for adding the output layer name
        self.layer_name_group = QGroupBox()
        layer_name_group_layout = QVBoxLayout()
        self.layer_name_group.setTitle('Layer name')
        self.layer_name_group.setLayout(layer_name_group_layout)
        self.layer_name = QLineEdit()
        self.layer_name.setText('thematic')
        layer_name_group_layout.addWidget(self.layer_name)

        # qline for adding the field name where the lables will be added
        self.class_name_group = QGroupBox()
        class_name_group_layout = QVBoxLayout()
        self.class_name_group.setTitle('Class name')
        self.class_name_group.setLayout(class_name_group_layout)
        self.class_name = QLineEdit()
        self.class_name.setText('class')
        class_name_group_layout.addWidget(self.class_name)

        # qline for adding the field name where the pixel values will be added
        self.idfield_group = QGroupBox()
        idfield_group_layout = QVBoxLayout()
        self.idfield_group.setTitle('Field')
        self.idfield_group.setLayout(idfield_group_layout)
        self.idfield = QLineEdit()
        self.idfield.setText('id')
        idfield_group_layout.addWidget(self.idfield)

        # push button for starting the polygonization
        self.button_box = QDialogButtonBox()
        self.poligonizebottun = self.button_box.addButton('Poligonize', QDialogButtonBox.NoRole)
        self.poligonizebottun.clicked.connect(self.run)

        # add all widgets to the layout
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

        # this will be the polyginize class object
        self.poly = None

        # this is the layerspanel widget to wich the result will be added at the end
        self.legendwidget = None

        # massage when done running:
        self.process = MyQProcess('Polygonizing...pleas wait', 'Polygonize')

    def collect_users_input(self):

        """collect the input from all widgets and init the poliginize object with costume labels
        or with the selected labels file"""
        #self.show_massage()
        rasterpath = self.raster_path_line.text()+' '
        labels = self.labels_path.text()+' '
        shapefile_path = self.shapefile_path.text()+' '
        layer_name = self.layer_name.text()+' '
        class_name = self.class_name.text()+' '
        idfield = self.idfield.text() +' '
        lstcostumelabels = 'None '

        if self.costumelabels_group.isChecked():
            costumelabels = '[' + self.costumelabels.text() + ']'
            lstcostumelabels = ast.literal_eval(costumelabels)
            labels = 'None '

        argsdict = {'rasterpath' :rasterpath,'labels': labels, 'shapefile_path': shapefile_path, 'layer_name':layer_name,
                    'class_name':class_name,'idfield':idfield,'lstcostumelabels':lstcostumelabels,'layerfullpath': self.shapefile_path.text()+self.layer_name.text()+'.shp'}

        return argsdict

    def clear(self):
        """clear the text from all widgets"""
        self.raster_path_line.clear()
        self.labels_path.clear()
        self.shapefile_path.clear()
        self.costumelabels.clear()
        self.layer_name.clear()
        self.class_name.clear()
        self.idfield.clear()

    def run(self):
        """start polygonizing when 'polygonize' button is clicked"""

        argsdict = self.collect_users_input()
        cmd = 'python3 ./widgets/tools/polygonize.py ' + argsdict['rasterpath']+  argsdict['labels']+  argsdict['shapefile_path']+ argsdict['layer_name'] + argsdict['class_name'] + argsdict['idfield'] +argsdict['lstcostumelabels']
        self.process.cmd = cmd
        self.process.start_process2()
        newlayer= argsdict['layerfullpath']
        #self.process.process.finished.connect(lambda: self.legendwidget.add_to_canvas([newlayer]))
        self.process.process.finished.connect(lambda: self.load_results(newlayer))


    def load_results(self,layer):
        if self.process.process.exitStatus() == QProcess.NormalExit:
            if self.process.process.exitCode() == 0:
                self.process.label.setText('Done')
                print('normal')
                self.legendwidget.add_to_canvas([layer])
                self.clear()
            elif self.process.process.exitCode() == 1:
                print('error ocurred')
                self.process.label.setText('An error occured:\n'
                                           '1.Check if the file name you chose alredy exist in the folder\n'
                                           '2.Check if some input is missing\n'
                                           '3. Check that all the input paths are valid')

















