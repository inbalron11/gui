from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout,QLabel,QGroupBox,QWidget,QMessageBox,QLineEdit,QPushButton,\
    QInputDialog,QListWidget, QComboBox,QListWidgetItem

from qgis.core import *
from qgis.gui import *
import sys
from costum_widgets import lineedit
import os



class PolyMapTool(QgsMapToolEmitPoint):
    def __init__(self,canvas):
        self.canvas = canvas
        QgsMapToolEmitPoint.__init__(self, self.canvas)
        self.rubberband = QgsRubberBand(self.canvas, True)
        self.rubberband.setColor(Qt.red)
        self.rubberband.setWidth(1)
        self.point = None
        self.points = []
        self.m_list = []

    def canvasPressEvent(self, e):
        if e.button() == Qt.RightButton:
            print(type(self.point))
            return self.points

        else:
            self.point = self.toMapCoordinates(e.pos())
            m = QgsVertexMarker(self.canvas)
            m.setCenter(self.point)
            m.setColor(QColor(0, 255, 0))
            m.setIconSize(5)
            m.setIconType(QgsVertexMarker.ICON_BOX)
            m.setPenWidth(3)

            self.m_list += [m]
            self.points.append(self.point)
            self.isEmittingPoint = True
            self.showPoly()

    def showPoly(self):

        self.rubberband.reset(geometryType= QgsWkbTypes.PolygonGeometry)
        for point in self.points[:-1]:
            self.rubberband.addPoint(point, False)
        self.rubberband.addPoint(self.points[-1], True)

    def keyPressEvent(self, event):
        """delet the current polygon"""
        if event.key() == Qt.Key_Delete:
            self.rubberband.reset(geometryType=QgsWkbTypes.PolygonGeometry)
            for i in self.m_list:
                self.canvas.scene().removeItem(i)

    def reset(self):

        self.rubberband.reset(geometryType=QgsWkbTypes.PolygonGeometry)
        for i in self.m_list:
            self.canvas.scene().removeItem(i)
        self.rubberband.setColor(Qt.red)
        self.rubberband.setWidth(1)
        self.point = None
        self.points = []
        self.m_list = []


class listwidgetitem(QListWidgetItem):
    def __init__(self, text):
        super().__init__()
        self.setFlags(Qt.ItemIsSelectable | Qt.ItemIsEditable | Qt.ItemIsEnabled)
        self.setText(text)


class listwidget(QListWidget):
    def __init__(self):
        super().__init__()

    def keyPressEvent(self, event):
        """delet the current polygon"""
        if event.key() == Qt.Key_Delete:
            self.takeItem(self.currentRow())

    def addclass(self,item):
        self.addItem(item)


class create_training_set(QWidget):
    def __init__(self,canvas):
        super().__init__()

        #self.path = layer_path
        self.canvas = canvas
        self.label = QLabel('class')
        self.num_of_classes_line = QLineEdit()
        self.classes = listwidget()
        self.create = QPushButton('Create layer')
        self.feature_class = QComboBox()
        self.buttoncreatefeature = QPushButton('Draw new feature')
        self.buttonadd = QPushButton('Add feature')
        self.buttonsave = QPushButton('Save')
        self.pluscalssbottun = QPushButton('+')
        self.outputline = lineedit()
        self.layer = None
        self.layername = None
        self.layout = QVBoxLayout()
        self.sizeHint()
        self.toolpoly = PolyMapTool(self.canvas)

        self.group_classes = QGroupBox()
        self.group_classes.setTitle('Create classes')
        self.group_classes_layout = QVBoxLayout()
        self.group_classes.setLayout(self.group_classes_layout)
        self.group_classes_layout.addWidget(self.classes)
        self.group_classes_layout.addWidget(self.pluscalssbottun)

        self.group_select_featureclass = QGroupBox()
        self.group_select_featureclass.setTitle('Select feature class')
        self.group_select_featureclass_layout = QVBoxLayout()
        self.group_select_featureclass.setLayout(self.group_select_featureclass_layout)
        self.group_select_featureclass_layout.addWidget(self.feature_class)

        self.group_drawfeature = QGroupBox()
        self.group_drawfeature_layout = QHBoxLayout()
        self.group_drawfeature.setLayout(self.group_drawfeature_layout)
        self.group_drawfeature_layout.addWidget(self.buttoncreatefeature)
        self.group_drawfeature_layout.addWidget(self.buttonadd)

        self.group_addfeature = QGroupBox()
        self.group_addfeature.setTitle('Add features')
        self.group_addfeature_layout = QVBoxLayout()
        self.group_addfeature.setLayout(self.group_addfeature_layout)
        self.group_addfeature_layout.addWidget(self.group_select_featureclass)
        self.group_addfeature_layout.addWidget(self.group_drawfeature)

        self.group_savelayer = QGroupBox()
        self.group_savelayer.setTitle('Save Training set')
        self.group_savelayer_layout = QHBoxLayout()
        self.group_savelayer.setLayout(self.group_savelayer_layout)
        self.group_savelayer_layout.addWidget(self.outputline)
        self.group_savelayer_layout.addWidget(self.buttonsave)

        self.layout.addWidget(self.group_classes)
        self.layout.addWidget(self.group_addfeature)
        self.layout.addWidget(self.group_savelayer)

        self.setLayout(self.layout)

        self.canvas = canvas

        self.buttoncreatefeature.clicked.connect(self.poly)
        self.buttonadd.clicked.connect(self.add_features)
        self.buttonsave.clicked.connect(self.save_layer)
        self.create.clicked.connect(self.create_layer)
        self.pluscalssbottun.clicked.connect(lambda: self.classes.addclass(listwidgetitem('class')))
        self.classes.currentItemChanged.connect(self.classes_names)
        self.classes.currentRowChanged.connect(self.classes_names)
        self.classes.currentTextChanged.connect(self.classes_names)
        self.classes.itemSelectionChanged.connect(self.classes_names)

    def create_layer(self):
        self.show()
        layernameinput = QInputDialog()
        text = layernameinput.getText(self, 'Training set name', 'Training set name')
        if text[1] is False:
            self.close()
        else:
            self.layername = text[0]
            self.layer = QgsVectorLayer('Polygon?crs=wgs:1984&field=CLASS', text[0], 'memory')
            self.layer.addAttribute(QgsField('CLASS', 10))
            self.dataprovider = self.layer.dataProvider()
            QgsProject.instance().addMapLayer(self.layer)

    def add_features(self):
        points = []
        for i in self.toolpoly.points:
            points.append(QgsPointXY(i[0],i[1]))
        print(points)
        polygon = QgsGeometry.fromPolygonXY([points])

        fields = self.dataprovider.fields()
        print(fields.names())
        feature = QgsFeature(fields)
        feature.setGeometry(polygon)

        feature['CLASS'] = self.feature_class.currentText()
        self.dataprovider.addFeature(feature)
        self.layer.updateExtents()
        self.canvas.refreshAllLayers()
        self.canvas.unsetMapTool(self.toolpoly)
        self.toolpoly.reset()

    def classes_names(self):
        itemsnames = []
        for i in range(self.classes.count()):
            itemsnames+=[self.classes.item(i).text()]
        self.feature_class.clear()
        self.feature_class.addItems(itemsnames)

    def poly(self):

        self.canvas.setMapTool(self.toolpoly)

    def save_layer(self):
        if not os.path.isdir(self.outputline.text()):
            print(self.outputline.text() +' is an invalid path')
            massage = QMessageBox()
            massage.setText('"Path of the file is Invalid"')
            massage.setWindowTitle('Invalid outpath')
            massage.exec()

        else:
            print('valid path')
            crs = QgsCoordinateReferenceSystem("WGS84")

            error = QgsVectorFileWriter.writeAsVectorFormat(self.layer,self.outputline.text()+'/'+self.layername+'.shp',
                                                            "UTF-8", crs, 'ESRI Shapefile')

            if error == QgsVectorFileWriter.NoError:
                print('success! writing new memory layer')
            else:
                print('failed at saving layer')




















