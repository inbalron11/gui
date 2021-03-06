from PyQt5.QtGui import QFont
from PyQt5.QtCore import  pyqtSignal, QFileInfo
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout, QGroupBox,\
     QLineEdit, QWidget, QLabel,QMessageBox,QTreeWidgetItem, QFileDialog

from qgis.core import *
from qgis.gui import *
import os
import ast


from costum_widgets import map_canvas, LayersPanel, datatreeview, inputlistwidget, lineedit, MyQProcess, bands_pairing2



class supervised_classification_ui(QWidget):
    running = pyqtSignal(name='running')

    def __init__(self):
        super().__init__()
        """init a widget for supervised classification"""

        #step1- chosing datasets, step 2- selecting featurebands, step 3- chosing trainingset,roi,classname,params,outpath
        self.step1 = QGroupBox()
        self.step2 = QGroupBox()
        self.step3 = QGroupBox()
        self.lstwidget_dataset = datatreeview()
        self.featurebandwidget = bands_pairing2(self.lstwidget_dataset)
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
        self.process = MyQProcess('Start classification...','Running classification...')
        # creates step1 and step2 ui
        self.createstep1()
        self.createstep3()
        self.createstep2()

        #connect signals and slots
        self.step3saveroject.clicked.connect(self.create_project)
        self.step1open.clicked.connect(self.load_supervised_project)
        self.step3classify.clicked.connect(self.run_supervised_classification)
        self.step1clear.clicked.connect(self.clear_all_data)
        self.step3clear.clicked.connect(self.clear_all_data)
        self.step2clear.clicked.connect(self.clear_all_data)


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
        self.step1clear = self.button_box_nextback.addButton('Clear', QDialogButtonBox.NoRole)
        step1grouplayout.addWidget(self.dataset)
        #step1grouplayout.addWidget(self.featurebands)
        step1grouplayout.addWidget(self.button_box_nextback)
        return

    def createstep3(self):
        """create the ui for step 1- selecting training,roi,params.outpath"""
        step3grouplayout = QVBoxLayout()
        self.step3.setLayout(step3grouplayout)
        self.button_box_nextback = QDialogButtonBox()
        self.step3classify = self.button_box_nextback.addButton('Classify', QDialogButtonBox.NoRole)
        self.step3clear = self.button_box_nextback.addButton('Clear', QDialogButtonBox.NoRole)
        self.step3saveroject = self.button_box_nextback.addButton('Save project', QDialogButtonBox.NoRole)
        self.step3back = self.button_box_nextback.addButton('Back', QDialogButtonBox.NoRole)
        step3grouplayout.addWidget(self.trainingset)
        step3grouplayout.addWidget(self.roi)
        step3grouplayout.addWidget(self.classfield)
        step3grouplayout.addWidget(self.outputpath)
        step3grouplayout.addWidget(self.params)
        step3grouplayout.addWidget(self.button_box_nextback)
        return

    def createstep2(self):
        step2grouplayout = QVBoxLayout()
        self.step2.setLayout(step2grouplayout)
        self.button_box_nextback = QDialogButtonBox()
        self.step2next= self.button_box_nextback.addButton('Next', QDialogButtonBox.NoRole)
        self.step2clear = self.button_box_nextback.addButton('Clear', QDialogButtonBox.NoRole)
        self.step2back = self.button_box_nextback.addButton('Back', QDialogButtonBox.NoRole)
        step2grouplayout.addWidget(self.featurebands)
        step2grouplayout.addWidget(self.button_box_nextback)

    def clear_all_data(self):
        """clear the data from all the widgets"""
        self.lstwidget_dataset.clear()
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

        # set the model for the band pairing widget
        self.featurebandwidget.firstband.setModel(self.featurebandwidget.dataview.model)
        self.featurebandwidget.secondband.setModel(self.featurebandwidget.dataview.model)

    def create_project(self):
        """create a project in a textfile when the user press save project"""
        folderename = QFileDialog.getExistingDirectory(None, "Select Folder")
        selectedpath = str(folderename) + '/'
        input = self.supervised_classification_input()[0]
        strinput = str(input)

        # create and save project:
        os.system("touch" + " " + selectedpath + "supervisedclassificationproject.txt")
        file = open(input['outpath'] + 'supervisedclassificationproject.txt', 'w')
        file.write(strinput)
        file.close()

    def supervised_classification_input(self):
        """get the users input fron all the widgets"""
        dataset = self.lstwidget_dataset.collectinput()[1]
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
        #datasetwidget = self.lstwidget_dataset.collectinput()[1]
        feturebandspairs = self.featurebandwidget.get_pairs()[2]

        inputlist = [dataset,bands,featurebands,trainingset,outpath,classname,mincellsize,maxcellsize,
                     minocurencedistance,maxocurencedistance,ovelrlapratio,objectresolution, feturebandspairs]

        inputdict = {'dataset': dataset, 'bands': bands, 'featurebands': featurebands, 'trainingset': trainingset,
                      'roi': roi, 'outpath': outpath, 'classname': classname, 'mincellsize': mincellsize,
                      'maxcellsize': maxcellsize, 'minocurencedistance': minocurencedistance,
                      'maxocurencedistance': maxocurencedistance,
                      'ovelrlapratio': ovelrlapratio, 'objectresolution': objectresolution,
                      'feturebandspairs': feturebandspairs}

        return [inputdict,inputlist]


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
        featurebandspairs = data["feturebandspairs"]

        # set all data to the widgets
        # self.supervised_classification.lstwidget_dataset.model.clear()
        self.lstwidget_dataset.add_dataset(dataset)


        for pair in featurebandspairs:
            pairitem = QTreeWidgetItem()
            pairitem.setText(0,pair[0])
            pairitem.setText(1, pair[1])
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

    def check_parameters(self):
        """checks if all the needed parameters were given by the user"""
        inputlist = self.supervised_classification_input()[1]

        for i in inputlist:
            if i == '' or i == [] or i == {}:
                print('missing')
                print(i)
                return False
        return True


    def run_supervised_classification(self):
        """run the classification when 'classify' bottun is pressed"""

        inputdict = self.supervised_classification_input()[0]
        self.running.emit()
        parameters = self.check_parameters()
        if parameters == True:
            strinput = str(inputdict)
            self.process.cmd = 'python3 ./widgets/tools/supervised_classification.py ' +'"' +strinput +'"'
            self.process.start_process()
        else:
            massage = QMessageBox(self)
            massage.setText('Some parameters are missing')
            massage.show()










