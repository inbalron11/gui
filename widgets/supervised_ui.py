from PyQt5.QtGui import QFont, QStandardItemModel, QDropEvent, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo,QProcess, QStringListModel, QThread, QObject, QRunnable, QThreadPool
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QGroupBox,\
    QPushButton, QLineEdit, QWidget, QFrame, QLabel, QListWidget, QApplication, QFileSystemModel,QTreeView,\
    QListView, QListWidgetItem, QAbstractItemView, QMenuBar, QAction, QMenu, QCheckBox, QListWidgetItem, QMessageBox,\
    QCheckBox, QTreeWidget, QTreeWidgetItem, QGraphicsView, QFileDialog,QTextEdit, QProgressBar
import sys
from qgis.core import *
from qgis.gui import *
import gdal
import os
import ast
import subprocess
import threading as thr

from costum_widgets import map_canvas, LayersPanel, datatreeview, bands_pairing, inputlistwidget, lineedit, MyQProcess
import fileinput


class supervised_classification_ui(QWidget):
    running = pyqtSignal(name='running')

    def __init__(self):
        super().__init__()
        """init a widget for supervised classification"""

        #step1- chosing dataset and bands, step 2- chosing trainingset,roi,classname,params,outpath
        self.step1 = QGroupBox()
        self.step2 = QGroupBox()
        self.lstwidget_dataset = datatreeview()
        self.featurebandwidget = bands_pairing(self.lstwidget_dataset)
        self.lstwidget_trainingset = inputlistwidget()
        self.lstwidget_roi = inputlistwidget()
        self.lineEdit_out = lineedit()
        self.lineEdit_classname = QLineEdit()
        self.cellsizelabel = QLabel('Cell Size')
        self.mincelllabel = QLabel('Min')
        self.maxcellalbel = QLabel('Max')
        self.mincellsizelineedit = QLineEdit()
        self.maxcellsizelineedit = QLineEdit()
        self.occcurencelabel = QLabel('Occurence\ndistance')
        self.minoccurencelabel = QLabel('Min')
        self.maxoccurencelabel = QLabel('Max')
        self.minoccurencelineedit = QLineEdit()
        self.maxoccurencelineedit = QLineEdit()
        self.overlapratiolabel = QLabel('Overlap ratio')
        self.objectresolutionlabel = QLabel('Object resolution')
        self.overlapratiolineedit = QLineEdit()
        self.objectresolutionlineedit = QLineEdit()

        self.dataset = QGroupBox()
        self.dataset.setTitle("Data set")
        datasetlayout = QVBoxLayout()
        datasetlayout.addWidget(self.lstwidget_dataset)
        self.dataset.setLayout(datasetlayout)

        # group2
        self.trainingset = QGroupBox()
        self.trainingset.setTitle("Training set")
        trainingsetlayout = QVBoxLayout()
        trainingsetlayout.addWidget(self.lstwidget_trainingset)
        self.trainingset.setLayout(trainingsetlayout)

        # group3
        self.roi = QGroupBox()
        self.roi.setTitle("Region of interest")
        roilayout = QVBoxLayout()
        roilayout.addWidget(self.lstwidget_roi)
        self.roi.setLayout(roilayout)

        # group4
        self.outputpath = QGroupBox()
        self.outputpath.setTitle("Output path")
        outputpathlayout = QVBoxLayout()
        outputpathlayout.addWidget(self.lineEdit_out)
        self.outputpath.setLayout(outputpathlayout)

        # group5
        self.classfield = QGroupBox()
        self.classfield.setTitle("Class field")
        self.lineEdit_classname.setText('CLASS')
        classfieldlayout = QHBoxLayout()
        classfieldlayout.addWidget(self.lineEdit_classname)
        self.classfield.setLayout(classfieldlayout)

        # group 6
        self.featurebands = QGroupBox()
        self.featurebands.setCheckable(True)
        self.featurebands.setChecked(False)
        self.featurebands.toggled.connect(self.set_fixed_bands)
        self.featurebands.setTitle("Feature bands")

        featurebandslayout = QVBoxLayout()
        featurebandslayout.addWidget(self.featurebandwidget.maingroup)
        self.featurebands.setLayout(featurebandslayout)

        # group 10
        myfont = QFont()
        myfont.setBold(True)
        self.cellsizelabel.setFont(myfont)
        self.occcurencelabel.setFont(myfont)
        self.overlapratiolabel.setFont(myfont)
        self.objectresolutionlabel.setFont(myfont)
        self.params = QGroupBox()
        paramslayout = QGridLayout()
        paramslayout.setHorizontalSpacing(35)
        self.params.setLayout(paramslayout)
        paramslayout.addWidget(self.cellsizelabel, 0, 0)
        paramslayout.addWidget(self.mincelllabel, 1, 0)
        paramslayout.addWidget(self.mincellsizelineedit, 1, 1)
        paramslayout.addWidget(self.maxcellalbel, 2, 0)
        paramslayout.addWidget(self.maxcellsizelineedit, 2, 1)
        paramslayout.addWidget(self.occcurencelabel, 0, 2)
        paramslayout.addWidget(self.minoccurencelabel, 1, 2)
        paramslayout.addWidget(self.minoccurencelineedit, 1, 3)
        paramslayout.addWidget(self.maxoccurencelabel, 2, 2)
        paramslayout.addWidget(self.maxoccurencelineedit, 2, 3)
        paramslayout.addWidget(self.overlapratiolabel, 1, 4)
        paramslayout.addWidget(self.overlapratiolineedit, 1, 5)
        paramslayout.addWidget(self.objectresolutionlabel, 2, 4)
        paramslayout.addWidget(self.objectresolutionlineedit, 2, 5)

        # Qprocess to run the classification
        self.process = MyQProcess()
        # creates step1 and step2 ui
        self.createstep1()
        self.createstep2()

        #connect signals and slots
        self.step2saveroject.clicked.connect(self.create_project)
        self.step1open.clicked.connect(self.load_supervised_project)
        self.step2classify.clicked.connect(self.run_supervised_classification)

    def runclass(self):
        """emits a signal when the classification is runing"""
        self.running.emit()

    def createstep1(self):
        """create the ui for step 1- selecting datasets and bands"""
        step1grouplayout = QVBoxLayout()
        self.step1.setLayout(step1grouplayout)
        self.button_box_nextback = QDialogButtonBox()
        self.step1next = self.button_box_nextback.addButton('Next', QDialogButtonBox.NoRole)
        self.step1open = self.button_box_nextback.addButton('Open project', QDialogButtonBox.NoRole)
        step1grouplayout.addWidget(self.dataset)
        step1grouplayout.addWidget(self.featurebands)
        step1grouplayout.addWidget(self.button_box_nextback)
        return

    def createstep2(self):
        """create the ui for step 1- selecting training,roi,params.outpath"""
        step2grouplayout = QVBoxLayout()
        self.step2.setLayout(step2grouplayout)
        self.button_box_nextback = QDialogButtonBox()
        self.step2classify = self.button_box_nextback.addButton('Classify', QDialogButtonBox.NoRole)
        self.step2saveroject = self.button_box_nextback.addButton('Save project', QDialogButtonBox.NoRole)
        self.step2back = self.button_box_nextback.addButton('Back', QDialogButtonBox.NoRole)
        step2grouplayout.addWidget(self.trainingset)
        step2grouplayout.addWidget(self.roi)
        step2grouplayout.addWidget(self.classfield)
        step2grouplayout.addWidget(self.outputpath)
        step2grouplayout.addWidget(self.params)
        step2grouplayout.addWidget(self.button_box_nextback)
        return

    def set_fixed_bands(self):
        """get the selcted bands from the datasetsselection widget and set them in the feature bands widget"""
        if self.featurebands.isChecked():
            self.featurebandwidget.firstband.clear()
            self.featurebandwidget.secondband.clear()
            self.featurebandwidget.additems()
        else:
            self.featurebandwidget.firstband.clear()
            self.featurebandwidget.secondband.clear()
            self.featurebandwidget.pairs.clear()

    def clear_all_data(self):
        """clear the data from all the widgets"""
        self.lstwidget_dataset.clear()
        self.featurebandwidget.firstband.clear()
        self.featurebandwidget.secondband.clear()
        self.featurebandwidget.pairs.clear()
        self.lstwidget_trainingset.clear()
        self.lstwidget_roi.clear()
        self.lineEdit_out.clear()
        self.lineEdit_classname.clear()
        self.mincellsizelineedit.clear()
        self.maxcellsizelineedit.clear()
        self.minoccurencelineedit.clear()
        self.maxoccurencelineedit.clear()
        self.overlapratiolineedit.clear()
        self.objectresolutionlineedit.clear()

    def create_project(self):
        """create a project in a textfile when the user press save project"""
        folderename = QFileDialog.getExistingDirectory(None, "Select Folder")
        selectedpath = str(folderename) + '/'
        input = self.supervised_classification_input()
        strinput = str(input)

        # create and save project:
        os.system("touch" + " " + selectedpath + "supervisedclassificationproject.txt")
        file = open(input['outpath'] + 'supervisedclassificationproject.txt', 'w')
        file.write(strinput)
        file.close()

    def supervised_classification_input(self):
        """get the users input fron all the widgets"""
        dataset = self.lstwidget_dataset.collect_user_input()['datasets']
        bands = self.featurebandwidget.get_pairs()[0]
        featurebands = self.featurebandwidget.get_pairs()[1]
        trainingset = self.lstwidget_trainingset.collect_input()
        roi = self.lstwidget_roi.collect_input()
        outpath = self.lineEdit_out.text()
        classname = self.lineEdit_classname.text()
        mincellsize = self.mincellsizelineedit.text()
        maxcellsize = self.maxcellsizelineedit.text()
        minocurencedistance = self.minoccurencelineedit.text()
        maxocurencedistance = self.maxoccurencelineedit.text()
        ovelrlapratio = self.overlapratiolineedit.text()
        objectresolution = self.objectresolutionlineedit.text()
        datasetwidget = self.lstwidget_dataset.collect_user_input()['bandsdict']
        feturebandspairs = self.featurebandwidget.get_pairs()[2]

        inputdict = {'dataset': dataset, 'bands': bands, 'featurebands': featurebands, 'trainingset': trainingset,
                      'roi': roi, 'outpath': outpath, 'classname': classname, 'mincellsize': float(mincellsize),
                      'maxcellsize': float(maxcellsize), 'minocurencedistance': float(minocurencedistance),
                      'maxocurencedistance': float(maxocurencedistance),
                      'ovelrlapratio': float(ovelrlapratio), 'objectresolution': float(objectresolution),
                      'datasetwidget': datasetwidget, 'feturebandspairs': feturebandspairs}

        return inputdict


    def load_supervised_project(self):
        """load a project and set its data into the widgets"""
        self.clear_all_data()
        file = QFileDialog.getOpenFileName(self, "Open project", ".", "(*.txt)")[0]
        fileinfo = QFileInfo(file)
        file = open(fileinfo, 'r')
        lines = []
        for line in file:
            lines += [str(line)]

        data = ast.literal_eval(lines[0])

        dataset = data["dataset"]
        bands = data["bands"]
        featurebands = data["featurebands"]
        trainingset = data["trainingset"]
        roi = data["roi"]
        outpath = data["outpath"]
        classname = data["classname"]
        mincellsize = data["mincellsize"]
        maxcellsize = data["maxcellsize"]
        minocurencedistance = data["minocurencedistance"]
        maxocurencedistance = data["maxocurencedistance"]
        ovelrlapratio = data["ovelrlapratio"]
        objectresolution = data["objectresolution"]
        datasetwidget = data["datasetwidget"]
        featurebandspairs = data["feturebandspairs"]

        # set all data to the widgets
        # self.supervised_classification.lstwidget_dataset.model.clear()
        self.lstwidget_dataset.add_dataset(dataset)

        for pair in featurebandspairs:
            pairitem = QTreeWidgetItem()
            pairitem.setText(0, pair.split('|')[0])
            pairitem.setText(1, pair.split('|')[1])
            self.featurebandwidget.pairs.addTopLevelItem(pairitem)
        self.lstwidget_trainingset.load_data(trainingset)
        self.lstwidget_roi.load_data(roi)
        self.lineEdit_out.setText(outpath)
        self.lineEdit_classname.setText(classname)
        self.mincellsizelineedit.setText(str(mincellsize))
        self.maxcellsizelineedit.setText(str(maxcellsize))
        self.minoccurencelineedit.setText(str(minocurencedistance))
        self.maxoccurencelineedit.setText(str(maxocurencedistance))
        self.overlapratiolineedit.setText(str(ovelrlapratio))
        self.objectresolutionlineedit.setText(str(objectresolution))

    def run_supervised_classification(self):
        """run the classification when 'classify' bottun is pressed"""
        self.running.emit()
        input = self.supervised_classification_input()
        strinput = str(input)

        # create the classification script with the users input
        copyclassificationscript = "cp " + "'/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/supervised_classification.py' " \
                                   + "'" + input['outpath'] + "'"
        os.system(copyclassificationscript)
        openinput = "input_dict =" + strinput

        for line in fileinput.input(input['outpath'] + 'supervised_classification.py', inplace=True):
            print(line.rstrip().replace('#open input', openinput))

        cmd = 'python3 ' + input['outpath'] + 'supervised_classification.py'
        print (cmd)
        #self.process.cmd = 'python3 /home/inbal/inbal/qgis_programing/standaloneapp/apptrials/metula_supervised.py'
        self.process.cmd = cmd
        self.process.start_process()


