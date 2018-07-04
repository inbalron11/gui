from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QVBoxLayout, QMainWindow, QApplication,\
     QMenuBar, QStackedWidget, QDockWidget, QAction,\
    QGraphicsView, QFrame

from qgis.core import *
from qgis.gui import *
import sys


# Import our GUI
sys.path.append('/home/inbal/inbal/qgis_programing/standaloneapp/clssification_app_gui/widgets')

from costum_widgets import map_canvas, LayersPanel,tree
from supervised_ui import supervised_classification_ui
from polygonize_ui import Polygonize_ui
from rasterize_ui import Rasterize_ui

# Environment variable qgis_prefix must be set to the install directory
# before running the application
qgis_prefix = '/opt/qgis/QGIS/build/output/'


class object_classifier_app (QMainWindow):
    def __init__(self):
        super().__init__()

        # initialize the main window
        self.title = 'Epif Object Classifier'
        self.setWindowTitle(self.title)
        self.left = 10
        self.top = 10
        self.width = 1500
        self.height = 750
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)


        self.canvasframe = QFrame()
        self.canvasframe.setFrameShape(QFrame.StyledPanel)
        self.canvasframe.setFrameShadow(QFrame.Raised)

        self.treewidget = tree()

        self.menuebar = QMenuBar()
        filemenue = self.menuebar.addMenu('File')
        classificationmenue = self.menuebar.addMenu('Classification')
        toolsmenue = self.menuebar.addMenu('Tools')
        self.supervised = QAction('supervised')
        self.unsupervised = QAction('unsupernised')
        self.poligonize = QAction('Polygonize')
        self.rasterize = QAction('Rasterize')
        self.confusiomatrix = QAction('Confusionmatrix')
        self.loadproject = QAction('Load project')
        classificationmenue.addAction(self.supervised)
        classificationmenue.addAction(self.unsupervised)
        toolsmenue.addAction(self.poligonize)
        toolsmenue.addAction(self.rasterize)
        toolsmenue.addAction(self.confusiomatrix)
        filemenue.addAction(self.loadproject)



        #set the canvas to be the main widget
        self.setCentralWidget(self.canvasframe)


        # Create the map canvas
        self.canvas = map_canvas()
        self.canvas.show()
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





        # Lay the canvas out in the main window using a vertical box layout
        self.framelayout = QVBoxLayout(self.canvasframe)
        self.framelayout.addWidget(self.canvas)

        # createlayerpanel
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
        self.StackedWidget.setCurrentWidget(self.supervised_classification.step1)
        self.StackedWidget_dock = QDockWidget('classification',self)
        self.StackedWidget_dock.setWidget(self.StackedWidget)
        self.addDockWidget(Qt.RightDockWidgetArea, self.StackedWidget_dock)

        # set the unsupervised classification window widget

        #set polygonize widget
        polygonizewidget = Polygonize_ui()
        polygonizewidget.legendwidget = self.layerpanel
        self.StackedWidget.addWidget(polygonizewidget)

        rastrizewidget = Rasterize_ui()
        rastrizewidget.legendwidget = self.layerpanel
        rastrizewidget.legendwidget = self.layerpanel
        self.StackedWidget.addWidget(rastrizewidget)



        # set the tree dockwidget
        self.tree = QDockWidget("Select Data", self)
        self.tree.setWidget(self.treewidget)
        self.tree.setFloating(False)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.tree)

        # set a menue bar
        self.setMenuBar(self.menuebar)


        self.threadpool = QThreadPool()



        self.poligonize.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(polygonizewidget))
        self.poligonize.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Polygonize'))
        self.rasterize.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(rastrizewidget))
        self.rasterize.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Rasterize'))
        self.supervised.triggered.connect(lambda: self.StackedWidget_dock.setWindowTitle('Supervised classification'))
        self.supervised.triggered.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step1))
        self.supervised_classification.step1next.clicked.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step2))
        self.supervised_classification.step2back.clicked.connect(lambda: self.StackedWidget.setCurrentWidget(self.supervised_classification.step1))


    def zoomIn(self):
        self.canvas.setDragMode(QGraphicsView.ScrollHandDrag)

    def zoomOut(self):
        self.canvas.setMapTool(self.toolZoomOut)

    def pan(self):
        self.canvas.setMapTool(self.toolPan)


    def main(argv):
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
