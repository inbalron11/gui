from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo,QProcess
from PyQt5.QtWidgets import QVBoxLayout, QHBoxLayout, QGroupBox,\
    QPushButton, QLineEdit, QWidget, QLabel, QListWidget, QApplication, QFileSystemModel,QTreeView,\
    QAbstractItemView, QMenu, QListWidgetItem,\
    QTreeWidget, QTreeWidgetItem,QTextEdit
import sys
from qgis.core import *
from qgis.gui import *
import gdal
import os


class MyMenuProvider(QgsLayerTreeViewMenuProvider):
    def __init__(self, view):
        super().__init__()
        """this class creates a menue for controling the layers in the layerspanel. 
            the menue initialized when right clicking on a layer in the layers panel."""

        self.view = view

    def createContextMenu(self):
        """create the menue when right clicking on a layer in the layers pannel"""
        if self.view.currentLayer():
            m = QMenu()
            m.addAction("Zoom to layer", self.zoomtolayer)
            m.addAction("Remove layer", self.removelayer)
        else:
            return None
        return m

    def removelayer(self):
        """when remove layer is clicked the layer is removed from the pannel"""
        r = self.view.currentLayer().id()
        self.view.removelayer(r)

    def zoomtolayer(self):
        """when zoom to layer is clicked the canvas will zoom to the current layer extent"""
        r = self.view.currentLayer().extent()
        self.view.linkedcanvas.setExtent(r)
        self.view.linkedcanvas.refreshAllLayers()


class LayersPanel(QgsLayerTreeView):

    layerdeletion = pyqtSignal(str, name='layerdeletion')
    dropped = pyqtSignal(list, name='dropped')
    
    def __init__(self, linkedcanvas):
        super().__init__()
        """This class creates a layers panel widget, connected to a map canvas (linked canvas)"""
        
        self.linkedcanvas = linkedcanvas
        self.project = QgsProject.instance()
        self.root = self.project.layerTreeRoot()
        self.model = QgsLayerTreeModel(self.root)
        self.setModel(self.model)
        self.bridge = QgsLayerTreeMapCanvasBridge(self.root, self.linkedcanvas)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeReorder)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeRename)
        self.model.setFlag(QgsLayerTreeModel.AllowNodeChangeVisibility)
        self.model.setFlag(QgsLayerTreeModel.ShowLegend)
        self.model.setFlag(QgsLayerTreeModel.ShowLegendAsTree)
        provider = MyMenuProvider(self)
        self.setMenuProvider(provider)
        self.setDragEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.DragDrop)
        
        # connect signals and slots
        self.dropped.connect(self.add_to_canvas)
        self.linkedcanvas.droppedtocanvas.connect(self.add_to_canvas)
        self.layerdeletion.connect(self.removelayer)
        self.currentLayerChanged.connect(lambda: self.linkedcanvas.refreshAllLayers())

    def keyPressEvent(self, event):
        """when 'delet' key is pressed a signal for deleting the current layer from the layers panel is emmited"""
        if event.key() == Qt.Key_Delete:
            if self.currentLayer():
                currentlayer = self.currentLayer()
                self.layerdeletion.emit(currentlayer.id())
            else:
                pass

    def removelayer(self, layerid):
        """"the current layer will be deleted when layerdeletion signal is emmited"""
        self.project.removeMapLayer(layerid)
        self.linkedcanvas.refreshAllLayers()

    def remove_groupnode(self, currentgroupnode):
        """the current groupnode will be deleted"""
        self.root.removeChildNode(currentgroupnode)
        self.linkedcanvas.refreshAllLayers()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(LayersPanel, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        else:
            super(LayersPanel, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.path()))
                self.dropped.emit(links)
            event.acceptProposedAction()
        else:
            super(LayersPanel, self).dropEvent(event)

    def add_to_canvas(self, item):
        """when dropped signal is emmited,if the layer is valid the layer will be added to the layers
        pannel and to the canvas"""
        for i in item:
            fileinfo = QFileInfo(i)
            raster = QgsRasterLayer(i, fileinfo.fileName())
            if not raster.isValid:
                print('raster is not valid')
            # Add layer to the qgsproject
            else:
                self.project.addMapLayer(raster)
                self.linkedcanvas.setExtent(raster.extent())

            shapefile = QgsVectorLayer(i, fileinfo.fileName(), "ogr")
            if not shapefile.isValid:
                print('shapefile is not valid')
            # Add layer to the qgsproject
            else:
                self.project.addMapLayer(shapefile)
                self.linkedcanvas.setExtent(shapefile.extent())
        self.linkedcanvas.refreshAllLayers()


class map_canvas(QgsMapCanvas):
    droppedtocanvas = pyqtSignal(list, name='droppedtocanvas')

    def __init__(self):
        super().__init__()
        """init the map canvas widget"""

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(map_canvas, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        else:
            super(map_canvas, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.path()))
                self.droppedtocanvas.emit(links)
        else:
            super(map_canvas, self).dropEvent(event)


class inputlistwidget(QListWidget):

    dropped = pyqtSignal(list, name='dropped')
    itemdeletion = pyqtSignal(name='itemdeletion')

    def __init__(self):
        super().__init__()
        """init a list widget, used to create a list of files with drag and drop (used for training sets and roi) """

        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.dropped.connect(self.add_to_list)
        self.dropIndicatorPosition()
        self.items = []

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(inputlistwidget, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        else:
            super(inputlistwidget, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.path()))
                self.dropped.emit(links)
            event.acceptProposedAction()
        else:
            super(inputlistwidget, self).dropEvent(event)

    def add_to_list(self, item):
        """add item to the list when dropped emited"""
        for i in item:
            self.addItem(i)
            self.items += [i]

    def keyPressEvent(self,event):
        """delete the current item when delete key is pressed"""
        if event.key() == Qt.Key_Delete:
            todelet = self.selectedItems()
            for i in todelet:
                self.takeItem(self.row(i))
                self.items.remove(i.text())

    def collect_input(self):
        """returns a list of all the data from the widget"""
        items = []
        for row in range(self.count()):
            item = self.item(row)
            items += [item.text()]
        if items == []:
            return ['']
        else:
            return items

    def load_data(self, lst):
        """add data to the widget when a project is loaded"""
        self.clear()
        for i in lst:
            self.addItem(i)


class lineedit(QLineEdit):
    dropped = pyqtSignal(str, name='dropped')

    def __init__(self):
        """lineedit widget that supports drug and drop"""
        super().__init__()

        self.setAcceptDrops(True)
        self.dropped.connect(self.change_text)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(lineedit, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        else:
            super(lineedit, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            for url in event.mimeData().urls():
                link = (str(url.path()))
            self.dropped.emit(link)
            event.acceptProposedAction()
        else:
            super(lineedit, self).dropEvent(event)

    def change_text(self, link):
        self.setText(link)


class datatreeview(QTreeView):
    dropped = pyqtSignal(name='dropped')

    def __init__(self):
        super().__init__()
        """a tree widget to create a list of datasets and select bands from each dataset"""

        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Dataset'])
        self.setModel(self.model)
        self.setSortingEnabled(True)
        self.root = self.model.invisibleRootItem()
        self.setAlternatingRowColors(True)
        self.bandsdict = None

        self.dataGroupBox = QGroupBox('')

        self.setEditTriggers(QAbstractItemView.SelectedClicked | QAbstractItemView.EditKeyPressed)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setDefaultDropAction(Qt.MoveAction)
        self.setDragDropMode(QAbstractItemView.InternalMove)

        self.setSortingEnabled(True)
        self.setAcceptDrops(True)
        self.setDropIndicatorShown(True)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDropIndicatorShown(True)
        self.root.setFlags(Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.dropped.connect(self.collectinput)

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(datatreeview, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        else:
            super(datatreeview, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.path()))
            self.add_dataset(links)
            event.acceptProposedAction()
            self.dropped.emit()
        else:
            super(datatreeview, self).dropEvent(event)

    def keyPressEvent(self, event):
        """delet the current dataset when delete key is pressed"""
        if event.key() == Qt.Key_Delete:
            todelet = self.selectedIndexes()
            for i in todelet:
                self.root.removeRow(i.row())
        self.collect_user_input()

    def add_dataset(self, raster_links):
        """if the dropped data set is a raster it will be added to the tree"""
        # this allows GDAL to throw Python Exceptions
        gdal.UseExceptions()
        for i in raster_links:
            treeitem = QStandardItem(str(i))
            try:
                src_ds = gdal.Open(i)
                bandscount = src_ds.RasterCount
                bandsindex = list(range(1, bandscount + 1))
                for index in reversed(bandsindex):
                    band = QStandardItem('band' + ' ' + str(index))
                    #band.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    band.setFlags(Qt.ItemIsEnabled | Qt.ItemIsSelectable)
                    #band.setCheckState(Qt.Checked)
                    treeitem.appendRow(band)
                treeitem.sortChildren(0, Qt.AscendingOrder)
                self.root.appendRows([treeitem])
            except:
                print('Unable to open INPUT tif')

    def clear(self):
        """clear the widget from data"""
        self.model.clear()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Dataset'])
        self.root = self.model.invisibleRootItem()
        self.root.setFlags(Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.setModel(self.model)

    def collectinput(self):
        datasets = []
        selectedbands = []
        # bandsdict example: {rastername-band1: [0,0], rastername-band2:[0,1]
        bandsdict = {}
        # add dataset to the dictionaty a key and it path and bands as value
        for i in range(self.model.rowCount(self.root.index())):
            dataset = self.model.item(i)
            datasets += [dataset.text()]
            datasetname = (os.path.basename(dataset.text()))
            bands = []
            # add every band to the dictionary- bands text as key and [datasetindex, bandindex] as value (example: band1 : [0,0]
            for j in range(self.model.rowCount(dataset.index())):
                band = dataset.child(j)
                bands += [j]
            for k in bands:
                bandtext = datasetname + ' - ' + 'band ' + str(k+1)
                bandsdict[bandtext] = [i, k]
                selectedbands += [[i,k]]
        self.bandsdict = bandsdict
        return [self.bandsdict, datasets, selectedbands]


class filetree(QTreeView):
    def __init__(self):
        super().__init__()
        """creates a file tree widget"""

        self.model = QFileSystemModel()
        self.model.setRootPath('/home/inbal')
        self.setDragEnabled(True)
        self.model.removeColumn(1)
        self.model.removeColumn(3)
        self.setModel(self.model)
        self.setRootIndex(self.model.index('/home/'))
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)


class MyQProcess(QWidget):
    """creates a q process for running the classification"""
    def __init__(self,text,title):
        super().__init__()

        # Add the UI components (here we use a QTextEdit to display the stdout from the process)
        self.layout = QVBoxLayout()
        self.stoppush = QPushButton('Stop')
        self.edit = QTextEdit()
        self.edit.setStyleSheet('font-size:12pt')
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.stoppush)
        self.setLayout(self.layout)
        self.cmd = None
        self.setGeometry(100,100, 800, 300)
        self.setMaximumHeight(300)
        self.setMaximumWidth(800)
        self.setWindowTitle(title)
        self.edit.setText(text)
        #self.show()

        # Add the process and start it
        self.process = QProcess()
        self.setupProcess()
        self.stoppush.clicked.connect(self.kill)
        self.process.finished.connect(lambda: self.edit.append('Done'))

    def setupProcess(self):
        # Set the channels
        self.process.setProcessChannelMode(QProcess.MergedChannels)
        # Connect the signal readyReadStandardOutput to the slot of the widget
        self.process.readyReadStandardOutput.connect(self.readStdOutput)

    def start_process(self):
        # Show the widget
        self.show()
        # print('starting process')
        self.process.start(self.cmd)
        # print('started')

    def __del__(self):
        # If QApplication is closed attempt to kill the process
        self.process.terminate()
        # Wait for Xms and then elevate the situation to terminate
        if not self.process.waitForFinished(10000):
            print('killing process')
            self.process.kill()

    def kill(self):
        print('killing process')
        self.process.terminate()
        self.edit.close()


    def readStdOutput(self):
        # Every time the process has something to output we attach it to the QTextEdit
        #self.edit.setText(str(self.process.readAllStandardOutput()))
        self.edit.append(str(self.process.readAllStandardOutput()))

    def main():
        app = QApplication(sys.argv)
        w = MyQProcess()

        return app.exec_()


class massagewidget(QWidget):
    def __init__(self, massage):
        super().__init__()
        """create a windoe whith a massage for the user"""
        self.massage = QLabel(massage)
        self.setFixedSize(300, 300)
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.addWidget(self.massage)


class treewidget(QTreeWidget):
    def __init__(self):
        super().__init__()
    def keyPressEvent(self, event):
        """when 'delet' key is pressed a signal for deleting the current layer from the pair widget is emmited"""
        if event.key() == Qt.Key_Delete:
            self.takeTopLevelItem(self.indexOfTopLevelItem(self.currentItem()))
        else:
                pass


class bands_pairing2(QWidget):
    def __init__(self, dataview):
        super().__init__()
        """a tree widget to create a list of datasets and select bands from each dataset"""

        self.dataview = dataview
        self.firstband = QTreeView()
        self.secondband = QTreeView()
        self.firstband.setModel(self.dataview.model)
        self.secondband.setModel(self.dataview.model)
        self.pairs = treewidget()
        self.pairs.setColumnCount(2)
        self.pairs.setHeaderLabels(['first band', 'second band'])
        self.pairbutton = QPushButton('Pair')

        self.pairbutton.clicked.connect(self.add_pair)
        mainlayout = QVBoxLayout()
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.firstband)
        sublayout.addWidget(self.secondband)
        firstsecondgroup = QGroupBox()
        firstsecondgroup.setLayout(sublayout)
        mainlayout.addWidget(firstsecondgroup)
        mainlayout.addWidget(self.pairbutton)
        mainlayout.addWidget(self.pairs)
        self.maingroup = QGroupBox()
        self.maingroup.setLayout(mainlayout)

    def additems(self):
        """when the widget is activated, a list of selected bands will be added"""
        dict = self.dataview.collect_user_input()
        for i in dict['bandsdict'].keys():
            name = os.path.basename(i)
            for j in dict['bandsdict'][name].keys():
                band = QListWidgetItem(j)
                band2 = QListWidgetItem(j)
                self.firstband.addItem(band)
                self.secondband.addItem(band2)

    def add_pair(self):
        """when pair button is pressed the paire will be add to the list"""
        # get selected index
        firstitem = self.firstband.selectedIndexes()
        # item text (example:band1)
        firstitemtext = self.firstband.model().itemData(firstitem[0])[0]
        # parent text (example: rastername.tif)
        firstparent = self.firstband.model().itemFromIndex(firstitem[0]).parent().data(0)
        #text to appear on the pairing widget
        firstpairtext = os.path.basename(firstparent) + ' - ' + firstitemtext

        # get selected index
        seconditem = self.secondband.selectedIndexes()
        # item text (example:band1)
        seconditemtext = self.secondband.model().itemData(seconditem[0])[0]
        # parent text (example: rastername.tif)
        secondparent = self.firstband.model().itemFromIndex(firstitem[0]).parent().data(0)
        # text to appear on the pairing widget
        secondpairtext = os.path.basename(secondparent) + ' - ' + seconditemtext

        print(firstitemtext)
        print(os.path.basename(firstparent))

        pairitem = QTreeWidgetItem()
        pairitem.setText(0, firstpairtext)
        pairitem.setText(1, secondpairtext)
        self.pairs.addTopLevelItem(pairitem)
        #self.get_pairs()

    def get_pairs(self):
        """returns  1. a dictionary of selected bands created with the datatreeview widget, 2. a list of featurebands,
         3. a list of texts from the items in the widgets (dataset and band number) """
        bandsdict = self.dataview.collectinput()[0]
        print (bandsdict)
        datasets = self.dataview.collectinput()[1]
        selectedbands = self.dataview.collectinput()[2]
        print(selectedbands)
        featurebands = []
        feturebandstext = []
        for i in range(self.pairs.topLevelItemCount()):
            item = self.pairs.topLevelItem(i)
            item1text = item.text(0)
            item2text = item.text(1)
            # get the list of the items from the widget
            feturebandstext += [[item1text, item2text]]
            band1 = bandsdict[item1text]
            band2 = bandsdict[item2text]
            # get the pair of bands by indexes
            pair = [selectedbands.index(band1), selectedbands.index(band2)]
            featurebands += [pair]
        print(selectedbands)
        print(featurebands)
        return [selectedbands, featurebands,feturebandstext]














