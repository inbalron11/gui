from PyQt5.QtGui import QFont, QStandardItemModel, QDropEvent, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal, QFileInfo,QProcess
from PyQt5.QtWidgets import QDialogButtonBox, QVBoxLayout, QHBoxLayout, QGridLayout, QComboBox, QGroupBox,\
    QPushButton, QLineEdit, QWidget, QFrame, QLabel, QListWidget, QApplication, QFileSystemModel,QTreeView,\
    QListView, QListWidgetItem, QAbstractItemView, QMenuBar, QAction, QMenu, QCheckBox, QListWidgetItem, QMessageBox,\
    QCheckBox, QTreeWidget, QTreeWidgetItem, QGraphicsView, QFileDialog,QTextEdit
import sys
from qgis.core import *
from qgis.gui import *
import gdal
import os
import ast

class MyMenuProvider(QgsLayerTreeViewMenuProvider):
    
  def __init__(self, view):
    super().__init__()
    """this class creates a menue for controling the layers in the layerspanel. 
        the menue initialized when right clicking on a layer in the layers panel."""

    self.view = view

  def createContextMenu(self):
    if self.view.currentLayer():
        m = QMenu()
        m.addAction("Show Extent", self.showExtent)
        m.addAction("Zoom to layer", self.zoomtolayer)
        m.addAction("Remove layer", self.removelayer)

    elif self.view.currentGroupNode():
        m = QMenu()
        m.addAction("Show Extent", self.showExtent)
        m.addAction("Zoom to layer", self.zoomtolayer)
        m.addAction("Remove layer", self.removelayer)

    else:
        return None

    return m

  def showExtent(self):
      """when show extent clicked, a window pop with the layer extent properties"""
      r = self.view.currentLayer().extent()
      QMessageBox.information(None, "Extent", r.toString())

  def removelayer(self):
      """when remove layer is clicked the layer is removed from the pannel"""
      r = self.view.currentLayer().id()
      self.view.removelayer(r)

  def zoomtolayer(self):
      """when zoom to layer is clicked the canvas will zoom to the current layer extent"""
      r = self.view.currentLayer().extent()
      self.view.linkedcanvas.setExtent(r)
      self.view.linkedcanvas.refreshAllLayers()

  def remove_group_node_layer(self):
      #r = self.view.currentGroupNode().currentLayer()
      r = self.view.selectedLayerNodes()
      self.view.root.removeChildNode(r[0])


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

    def removelayer(self,layerid):
        """"the current layer will be deleted when layerdeletion signal is emmited"""
        self.project.removeMapLayer(layerid)
        self.linkedcanvas.refreshAllLayers()

    def remove_groupnode(self,currentgroupnode):
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
        """when dropped signal is emmited, the layer will be added to the layers pannel and to canvas"""
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
        self.show

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



class listview(QListWidget):

    dropped = pyqtSignal(list, name='dropped')
    itemdeletion = pyqtSignal(name='itemdeletion')
    def __init__(self):
        super().__init__()

        self.setAcceptDrops(True)
        self.setDragDropMode(QAbstractItemView.DropOnly)
        self.dropped.connect(self.add_to_list)
        self.dropIndicatorPosition()
        self.items =[]
        self.name = 'New group node'
        self.add_to_list(' ')

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls:
            event.acceptProposedAction()
        else:
            super(listview, self).dragEnterEvent(event)

    def dragMoveEvent(self, event):
        if event.mimeData().hasUrls():
            event.setDropAction(Qt.CopyAction)
            event.acceptProposedAction()
        else:
            super(listview, self).dragMoveEvent(event)

    def dropEvent(self, event):
        if event.mimeData().hasUrls():
            links = []
            for url in event.mimeData().urls():
                links.append(str(url.path()))
                self.dropped.emit(links)
            event.acceptProposedAction()
        else:
            super(listview, self).dropEvent(event)

    def add_to_list(self, item):
        for i in item:
            self.addItem(i)
            self.items += [i]

    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Delete:
            todelet = self.selectedItems()
            for i in todelet:
                self.takeItem(self.row(i))
                self.items.remove(i.text())

    def collect_input(self):
        items = []
        for row in range(self.count()):
            item = self.item(row)
            items += [item.text()]
        return items

    def load_data(self, lst):
        self.clear()
        for i in lst:
            self.addItem(i)




class lineedit(QLineEdit):
    dropped = pyqtSignal(str, name='dropped')
    def __init__(self):
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
        self.dropped.connect(self.collect_user_input)


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


    def keyPressEvent(self,event):
        if event.key() == Qt.Key_Delete:
            todelet = self.selectedIndexes()
            for i in todelet:
                self.root.removeRow(i.row())
        self.collect_user_input()


    def add_dataset(self, raster_links):
        # this allows GDAL to throw Python Exceptions
        gdal.UseExceptions()
        for i in raster_links:
            treeitem = QStandardItem(str(i))
            #print(str(i))
            #treeitem.setFlags(Qt.ItemIsDragEnabled | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
            try:
                src_ds = gdal.Open(i)
                bandscount = src_ds.RasterCount
                bandsindex = list(range(1, bandscount + 1))
                childrens = []
                for index in reversed(bandsindex):
                    band = QStandardItem('band' + ' ' + str(index))
                    band.setFlags(Qt.ItemIsUserCheckable | Qt.ItemIsUserCheckable | Qt.ItemIsEnabled)
                    band.setCheckState(Qt.Checked)
                    # childrens += [band]
                    treeitem.appendRow(band)
                treeitem.sortChildren(0, Qt.AscendingOrder)
                self.root.appendRows([treeitem])
            except:
                print('Unable to open INPUT tif')

    def clear(self):
        self.model.clear()
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Dataset'])
        self.root = self.model.invisibleRootItem()
        self.root.setFlags(Qt.ItemIsDropEnabled | Qt.ItemIsDragEnabled | Qt.ItemIsEditable | Qt.ItemIsEnabled | Qt.ItemIsSelectable)
        self.setModel(self.model)

    def collect_user_input(self):
        datasets = []
        selectedbands = []
        bandsdict={}
        for i in range(self.model.rowCount(self.root.index())):
            dataset = self.model.item(i)
            datasets += [dataset.text()]
            datasetname = (os.path.basename(dataset.text()))
            bandsdict[datasetname] = {}
            bands = []
            for j in range(self.model.rowCount(dataset.index())):
                band = dataset.child(j)
                if band.checkState() == Qt.Checked:
                    bands += [j]
            for k in bands:
                selectedbands += [[i, k]]
                bandsdict[datasetname][datasetname +' ' + ':'+ ' ' + dataset.child(k).text()] = [i, k]
        self.bandsdict = bandsdict
        #print({'datasets':datasets,'selectedbands':selectedbands, 'bandsdict':bandsdict})
        #print(self.bandsdict)
        inputdict = {'datasets':datasets,'selectedbands':selectedbands,'bandsdict':bandsdict}
        return inputdict




class bands_pairing(QWidget):
    def __init__(self, dataview):
        super().__init__()

        self.firstband = QListWidget()
        self.secondband = QListWidget()
        self.pairs = QTreeWidget()
        self.pairs.setColumnCount(2)
        self.pairs.setHeaderLabels(['first band', 'second band'])
        self.pairbutton = QPushButton('Pair')
        self.dataview = dataview
        self.pairbutton.clicked.connect(self.add_pair)

        mainlayout = QVBoxLayout()
        sublayout = QHBoxLayout()
        sublayout.addWidget(self.firstband)
        sublayout.addWidget(self.secondband)
        #sublayout.addWidget(self.pairbutton)
        #sublayout.addWidget(self.pairs)
        firstsecondgroup = QGroupBox()
        firstsecondgroup.setLayout(sublayout)
        mainlayout.addWidget(firstsecondgroup)
        mainlayout.addWidget(self.pairbutton)
        mainlayout.addWidget(self.pairs)
        self.maingroup = QGroupBox()
        self.maingroup.setLayout(mainlayout)

    def additems(self):
        dict = self.dataview.collect_user_input()
        for i in dict['bandsdict'].keys():
            #print(dict['bandsdict'].keys())
            name = os.path.basename(i)
            #print(name)
            for j in dict['bandsdict'][name].keys():
                band = QListWidgetItem(j)
                band2 = QListWidgetItem(j)
                self.firstband.addItem(band)
                self.secondband.addItem(band2)

    def add_pair(self):
        firstitem = self.firstband.selectedItems()
        firstitemtext = firstitem[0].text()
        seconditem = self.secondband.selectedItems()
        seconditemtext = seconditem[0].text()
        pairitem = QTreeWidgetItem()
        pairitem.setText(0 ,firstitemtext)
        pairitem.setText(1,seconditemtext )
        #self.pairs.addItem(firstitemtext+ ' '+ '+' + ' ' + seconditemtext)
        self.pairs.addTopLevelItem(pairitem)
        self.get_pairs()

    def get_pairs(self):
        dict = self.dataview.collect_user_input()
        pairs = []
        featurebands = []
        for i in range(self.pairs.topLevelItemCount()):
            item = self.pairs.topLevelItem(i)
            datasetname = item.text(0).split(' : ')[0]
            item1text = item.text(0)
            item2text = item.text(1)
            pairs += [item1text +'|'+ item2text]
            band1 = dict['bandsdict'][datasetname][item1text]
            band2 = dict['bandsdict'][datasetname][item2text]
            pair = [dict['selectedbands'].index(band1),dict['selectedbands'].index(band2)]
            featurebands += [pair]
        #print(dict['selectedbands'])
        #print(featurebands)
        return [dict['selectedbands'], featurebands, pairs]






class tree(QTreeView):
    def __init__(self):
        super().__init__()
        # create tree view
        self.model = QFileSystemModel()
        self.model.setRootPath('/home/inbal')
        self.setDragEnabled(True)
        self.model.removeColumn(1)
        self.model.removeColumn(3)
        self.setModel(self.model)
        self.setRootIndex(self.model.index('/home/inbal'))
        self.hideColumn(1)
        self.hideColumn(2)
        self.hideColumn(3)
        self.setAnimated(True)
        self.setIndentation(20)
        self.setSortingEnabled(True)







if __name__ == '__main__':

    app = QApplication(sys.argv)
    wnd = changing_UI()
    wnd.show()
    sys.exit(app.exec_())
