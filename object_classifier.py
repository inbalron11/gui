from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QFileDialog, QApplication, QHBoxLayout,QLabel,\
    QDialogButtonBox,QGroupBox, QToolButton, QMenuBar, QWidget, QStackedWidget, QDockWidget, QAction,\
    QGraphicsView, QTreeWidgetItem, QFrame, QTextEdit,QMessageBox

from qgis.core import *
from qgis.gui import *
import sys


# Import costume widgets
sys.path.append('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/widgets')

from costum_widgets import map_canvas, LayersPanel,filetree
from supervised_ui import supervised_classification_ui
from polygonize_ui import Polygonize_ui
from rasterize_ui import Rasterize_ui
from confusinmatrix_ui import Confusion_matrix_ui
#from canvastools import PolyMapTool, PointMapTool, SelectMapTool


# Environment variable qgis_prefix must be set to the install directory
# before running the application
qgis_prefix = '/opt/qgis/QGIS/build/output/'


class object_classifier_app (QMainWindow):
    def __init__(self):
        super().__init__()
        
        # init the main window
        self.title = 'Epif Object Classifier'
        self.setWindowTitle(self.title)
        self.left = 10
        self.top = 10
        self.width = 1500
        self.height = 750
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        # Create the map canvas and set the canvas to be the main widget
        self.canvasframe = QFrame()
        self.canvasframe.setFrameShape(QFrame.StyledPanel)
        self.canvasframe.setFrameShadow(QFrame.Raised)
        self.setCentralWidget(self.canvasframe)
        self.canvas = map_canvas()
        self.canvas.show()
        self.framelayout = QVBoxLayout(self.canvasframe)
        self.framelayout.addWidget(self.canvas)
        
        # create map canvas actions and set icons
        actionZoomIn = QAction("Zoom in", self)
        actionZoomOut = QAction("Zoom out", self)
        actionPan = QAction("Pan", self)
        actionZoomIn.setCheckable(True)
        actionZoomOut.setCheckable(True)
        actionPan.setCheckable(True)

        actionPanPixmap = QPixmap('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/icons/Hands-Hand-icon.png')
        actionZoomInPixmap = QPixmap('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/icons/Zoom-In-icon.png')
        actionZoomOutPixmap = QPixmap('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/icons/Zoom-Out-icon.png')

        actionZoomIn.setIcon(QIcon(actionZoomInPixmap))
        actionZoomOut.setIcon(QIcon(actionZoomOutPixmap))
        actionPan.setIcon(QIcon(actionPanPixmap))
        
        actionZoomIn.triggered.connect(self.zoomIn)
        actionZoomOut.triggered.connect(self.zoomOut)
        actionPan.triggered.connect(self.pan)
        
          # create map canvas tool bar
        self.toolbar = self.addToolBar("Canvas actions")
        self.toolbar.addAction(actionZoomIn)
        self.toolbar.addAction(actionZoomOut)
        self.toolbar.addAction(actionPan)

        # create the map tools
        self.toolPan = QgsMapToolPan(self.canvas)
        self.toolPan.setAction(actionPan)
        self.toolZoomIn = QgsMapToolZoom(self.canvas, False)  # false = in
        self.toolZoomIn.setAction(actionZoomIn)
        self.toolZoomOut = QgsMapToolZoom(self.canvas, True)  # true = out
        self.toolZoomOut.setAction(actionZoomOut)

        #init the file tree widget and set as a dock widget
        self.treewidget = filetree()
        self.tree = QDockWidget("Select Data", self)
        self.tree.setWidget(self.treewidget)
        self.tree.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree)
        
        # init a menue bar and its actions
        self.menuebar = QMenuBar()
        self.setMenuBar(self.menuebar)
        filemenue = self.menuebar.addMenu('File')
        classificationmenue = self.menuebar.addMenu('Classification')
        toolsmenue = self.menuebar.addMenu('Tools')
        self.supervised = QAction('supervised')
        self.unsupervised = QAction('unsupernised')
        self.poligonize = QAction('Polygonize')
        self.rasterize = QAction('Rasterize')
        self.confusiomatrix = QAction('Confusionmatrix')
        self.loadprojectaction = QAction('Load project')
        self.saveprojectaction = QAction('Save project')
        classificationmenue.addAction(self.supervised)
        classificationmenue.addAction(self.unsupervised)
        toolsmenue.addAction(self.poligonize)
        toolsmenue.addAction(self.rasterize)
        toolsmenue.addAction(self.confusiomatrix)
        filemenue.addAction(self.loadprojectaction)
        filemenue.addAction(self.saveprojectaction)
       
        # create a layerpanel
        self.layerpanel = LayersPanel(self.canvas)
        self.layerpanelDock = QDockWidget("Layers", self)
        self.layerpanelDock.setObjectName("layers")
        self.layerpanelDock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)
        self.layerpanelDock.setWidget(self.layerpanel)
        self.layerpanelDock.setContentsMargins(9, 9, 9, 9)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.layerpanelDock)

        #set the supervised classification window widget
        self.supervised_classification = supervised_classification_ui()
        self.StackedWidget = QStackedWidget()
        self.StackedWidget.addWidget(self.supervised_classification.step1)
        self.StackedWidget.addWidget(self.supervised_classification.step2)
        self.StackedWidget.addWidget(self.supervised_classification.step3)
        self.StackedWidget.setCurrentWidget(self.supervised_classification.step1)
        self.StackedWidget_dock = QDockWidget('classification',self)
        self.StackedWidget_dock.setWidget(self.StackedWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.StackedWidget_dock)

        # set the unsupervised classification window widget

        #set polygonize widget
        polygonizewidget = Polygonize_ui()
        polygonizewidget.legendwidget = self.layerpanel
        self.StackedWidget.addWidget(polygonizewidget)
        
        # set rasterize widget
        rastrizewidget = Rasterize_ui()
        rastrizewidget.legendwidget = self.layerpanel
        rastrizewidget.legendwidget = self.layerpanel
        self.StackedWidget.addWidget(rastrizewidget)

        # set confusion matrix widget
        confusionmatrixwidget = Confusion_matrix_ui()
        self.StackedWidget.addWidget(confusionmatrixwidget)
        self.StackedWidget.addWidget(confusionmatrixwidget.resultsgroup)

        self.threadpool = QThreadPool()
        self.massage = QMessageBox(text='Running')

        # connect signals and slots
        self.poligonize.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(polygonizewidget))
        self.poligonize.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Polygonize'))
        self.rasterize.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(rastrizewidget))
        self.rasterize.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Rasterize'))
        self.confusiomatrix.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(confusionmatrixwidget))
        self.confusiomatrix.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Confusion Matrix'))
        confusionmatrixwidget.done.connect(lambda: self.StackedWidget.setCurrentWidget(confusionmatrixwidget.resultsgroup))
        self.supervised.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Supervised classification'))
        self.supervised.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step1))
        self.supervised_classification.step1next.clicked.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step2))
        self.supervised_classification.step2back.clicked.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step1))
        self.supervised_classification.step2next.clicked.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step3))
        self.supervised_classification.step3back.clicked.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step2))
        self.loadprojectaction.triggered.connect(self.openproject)
        self.saveprojectaction.triggered.connect(self.saveproject)


    def zoomIn(self):
        """canvas zoom in tool"""
        self.canvas.setMapTool(self.toolZoomIn)

    def zoomOut(self):
        """canvas zoom out tool"""
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        """canvas pan tool"""
        self.canvas.setMapTool(self.toolPan)

    def saveproject(self):
        savedfile = QFileDialog.getSaveFileName(self, "Save project", ".", "(*.qgs)")[0] +'.qgs'
        try:
            self.layerpanel.project.setFileName(savedfile)
            self.layerpanel.project.write()
        except:
            pass


    def openproject(self):
        file = QFileDialog.getOpenFileName(self, "Open project", ".", "(*.qgs)")[0]
        fileinfo = QFileInfo(file)
        projectfile = fileinfo.filePath()
        print(projectfile)
        try:
            self.layerpanel.project.read(projectfile)
        except:
            pass




    def main(argv):
        """runing thr appplication"""
        # create Qt application
        app = QApplication(argv)

        # Initialize qgis libraries
        QgsApplication.setPrefixPath(qgis_prefix, True)
        QgsApplication.initQgis()

        # create main window
        wnd = object_classifier_app()
        # Move the app window to upper left
        wnd.move(100, 100)
        wnd.show()

        # run!
        retval = app.exec_()

        # exit
        QgsApplication.exitQgis()
        sys.exit(retval)


if __name__ == "__main__":
    object_classifier_app.main(sys.argv)
