from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout,QGroupBox,QLineEdit,QWidget, QMessageBox, QFrame, QLabel
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
import sys
from qgis.core import *
from qgis.gui import *
from costum_widgets import map_canvas, LayersPanel, datatreeview, inputlistwidget, lineedit

sys.path.append('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/widgets/tools')
from confusion_matrix import Confusion_matrix


class Confusion_matrix_ui(QWidget):
    done = pyqtSignal(name = 'done')

    def __init__(self):
        super().__init__()

        self.trueraster_path_group = QGroupBox()
        trueraster_path_group_layout = QVBoxLayout()
        self.trueraster_path_group.setTitle('True raster path')
        self.trueraster_path_group.setLayout(trueraster_path_group_layout)
        self.trueraster_path_line = lineedit()
        self.trueraster_path_line.setText('/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif')
        trueraster_path_group_layout.addWidget(self.trueraster_path_line)

        self.predicted_raster_path_group = QGroupBox()
        predicted_raster_path_group_layout = QVBoxLayout()
        self.predicted_raster_path_group.setTitle('Predicted raster path')
        self.predicted_raster_path_group.setLayout(predicted_raster_path_group_layout)
        self.predicted_raster_path_line = lineedit()
        self.predicted_raster_path_line.setText('/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/predicted_raster.tif')
        predicted_raster_path_group_layout.addWidget(self.predicted_raster_path_line)

        self.outpath_group = QGroupBox()
        outpath_group_layout = QVBoxLayout()
        self.outpath_group.setTitle('Output path')
        self.outpath_group.setLayout(outpath_group_layout)
        self.outpath_line = lineedit()
        self.outpath_line.setText('/home/inbal/inbal/qgis_programing/standaloneapp/apptrials')
        outpath_group_layout.addWidget(self.outpath_line)

        self.button_box = QDialogButtonBox()
        self.confusionbottun = self.button_box.addButton('Get confusion matrix', QDialogButtonBox.NoRole)

        layout = QVBoxLayout()
        layout.addWidget(self.trueraster_path_group)
        layout.addWidget(self.predicted_raster_path_group)
        layout.addWidget(self.outpath_group)
        layout.addWidget(self.button_box)

        self.resultsgroup = QGroupBox()
        self.resultslayout = QVBoxLayout()
        self.resultsgroup.setLayout(self.resultslayout)

        self.frame1 = QFrame()
        self.frame1layout = QVBoxLayout()
        self.frame1.setLayout(self.frame1layout)
        self.frame1.setFrameShape(QFrame.StyledPanel)
        self.frame1.setFrameShadow(QFrame.Raised)
        self.label1 = QLabel()
        self.frame1layout.addWidget(self.label1)


        self.frame2 = QFrame()
        self.frame2layout = QVBoxLayout()
        self.frame2.setLayout(self.frame2layout)
        self.frame2.setFrameShape(QFrame.StyledPanel)
        self.frame2.setFrameShadow(QFrame.Raised)
        self.label2 = QLabel()
        self.frame2layout.addWidget(self.label2)


        self.resultslayout.addWidget(self.frame1)
        self.resultslayout.addWidget(self.frame2)

        self.setLayout(layout)

        self.confusionbottun.clicked.connect(self.run)

        self.massage = QMessageBox()

    def clear(self):
        self.trueraster_path_line.clear()
        self.predicted_raster_path_line.clear()
        self.outpath_line.clear()

    def run(self):
        trueraster_path_line = self.trueraster_path_line.text()
        predicted_raster_path_line = self.predicted_raster_path_line.text()
        outpath_line = self.outpath_line.text()
        self.con = Confusion_matrix(trueraster_path_line, predicted_raster_path_line, 10, outpath_line, False)
        self.done.emit()

        pixmap = QPixmap(outpath_line + '/' + 'normalized_confusion_matrix')
        self.label1.setPixmap(pixmap)


        pixmap = QPixmap(outpath_line + '/'+ 'confusion_matrix')
        self.label2.setPixmap(pixmap)


        self.massage.setText('Done')
        self.massage.show()
        self.clear()
