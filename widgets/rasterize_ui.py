from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout,QGroupBox,QLineEdit,QWidget
from PyQt5.QtCore import QProcess
import sys
from qgis.core import *
from qgis.gui import *
from costum_widgets import map_canvas, LayersPanel, datatreeview, inputlistwidget, lineedit

sys.path.append('./tools')
from rasterize import Rasterize
from costum_widgets import MyQProcess


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

        self.process = MyQProcess('Rasterizing...', 'Rasterize')

    def collect_users_input(self):
        if self.lables_file_group.isChecked():
            lables_file = self.lables_file_line.text()
        else:
            lables_file = None
        shapefile_path_line = self.shapefile_path_line.text()
        out_raster_path = self.out_raster_path_line.text()
        reference_raster = self.reference_raster_line.text()
        out_raster_name = self.out_raster_name_line.text()
        field_name = self.field_name_line.text()

        self.newraster = out_raster_path + out_raster_name

        self.ras = Rasterize(shapefile_path_line, out_raster_path, reference_raster, out_raster_name=out_raster_name,
                             field_name=field_name, lables_file=lables_file)

    def clear(self):
        self.shapefile_path_line.clear()
        self.out_raster_path_line.clear()
        self.reference_raster_line.clear()
        self.out_raster_name_line.clear()
        self.field_name_line.clear()
        self.lables_file_line.clear()

    def load_results_to_canvas(self,raster):
        if self.process.process.exitStatus() == QProcess.NormalExit:
            if self.process.process.exitCode() == 0:
                self.process.label.setText('Done')
                print('normal')
                self.legendwidget.add_to_canvas([raster])
                self.clear()
            elif self.process.process.exitCode() == 1:
                print('error ocurred')
                self.process.label.setText('An error occured:\n'
                                           '1.Check if some input is missing\n'
                                           '2. Check that all the input paths are valid')

    def run(self):
        shapefile_path_line = self.shapefile_path_line.text() + ' '
        out_raster_path = self.out_raster_path_line.text() + ' '
        reference_raster = self.reference_raster_line.text() + ' '
        out_raster_name = self.out_raster_name_line.text() + ' '
        field_name = self.field_name_line.text() + ' '
        lables_file = 'None '
        self.newraster = out_raster_path + out_raster_name
        if self.lables_file_group.isChecked():
            lables_file = self.lables_file_line.text() + ' '

        cmd = 'python3 ./widgets/tools/rasterize.py ' + shapefile_path_line + out_raster_path + reference_raster + out_raster_name + field_name + lables_file
        self.process.cmd = cmd
        self.process.start_process2()
        newraster = self.out_raster_path_line.text() + self.out_raster_name_line.text()
        self.process.process.finished.connect(lambda: self.load_results_to_canvas(newraster))

