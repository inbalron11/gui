import sys
import csv
import getopt
import numpy as np
from osgeo import ogr
from osgeo import gdal
from osgeo import osr


class Polygonize:
    """ This class converts Raster to shapefile and assigns a class attribute to each polygon according to its pixel
    value and a given label file.
       Args:
       raster_path(str):the path from which the raster to be converted will be imported
       labels_path(str):the path from which the txt file that contains the labels will be imported
       shapefile_path(str): the path for storing the new shapefile
       layer_name(str):the new shapefile name, defaults to 'thematic'
       class_name(str):the name of the class field, defaults to 'class'
       id(str): the name of the id (this field contains the original pixel value) field,defaults to 'id'
       methods:
       polygonize - creates a shapfile for all classes
       create_filtered_shapefile- creats a shapfile for a given class"""

    type_mapping = {gdal.GDT_Byte: ogr.OFTInteger, gdal.GDT_UInt16: ogr.OFTInteger, gdal.GDT_Int16: ogr.OFTInteger,
                    gdal.GDT_UInt32: ogr.OFTInteger, gdal.GDT_Int32: ogr.OFTInteger, gdal.GDT_Float32: ogr.OFTReal,
                    gdal.GDT_Float64: ogr.OFTReal, gdal.GDT_CInt16: ogr.OFTInteger, gdal.GDT_CInt32: ogr.OFTInteger,
                    gdal.GDT_CFloat32: ogr.OFTReal, gdal.GDT_CFloat64: ogr.OFTReal}
    shp_driver = ogr.GetDriverByName('ESRI Shapefile')

    def __init__(self, raster_path, shapefile_path, labels_path = None,labels_list = None , layer_name='thematic', class_name='class',
                 idfield='id'):

        self.rasterpath = raster_path
        self.class_name = class_name
        self.output_shp = shapefile_path
        self.layer_name = layer_name
        self.labels_path= labels_path
        if labels_path is not None:
            self.open_labeles = open(labels_path)
        self.id = idfield
        self.labels_list = labels_list
        # get raster data source
        self.src_raster = gdal.Open(self.rasterpath)
        self.input_band = self.src_raster.GetRasterBand(1)
        # define output layer srs
        if self.src_raster.GetProjectionRef() != ' ':
            self.srs = osr.SpatialReference(self.src_raster.GetProjectionRef())
            # srs.ImportFromWkt(src_raster.GetProjectionRef())

    def create_output_shp_fields(self, dst_layer):
        """creates new id(pixel value) field and classs field for the output shapefile."""
        raster_field = ogr.FieldDefn(self.id, self.type_mapping[self.input_band.DataType])
        dst_layer.CreateField(raster_field)
        class_field = ogr.FieldDefn(self.class_name)
        dst_layer.CreateField(class_field)

    def create_lables_dict(self):
        """creation of a dictionary for mapping between lables and pixel values"""
        labelsdict = {}
        lables_lst = []
        if self.labels_path is not None:
            reader = csv.reader(self.open_labeles, delimiter='\n')
            for line in reader:
                lables_lst += line
        elif self.labels_list is not None:
            lables_lst = self.labels_list

        else:
            print("labels where not defined")

        key = 0
        for i in range(len(lables_lst)):
            key += 1
            labelsdict[key] = lables_lst[i]
        return labelsdict

    def polygonize(self):
        """creates a shapfile for all classes"""
        lables_dict = self.create_lables_dict()
        output_shapefile = self.shp_driver.CreateDataSource(self.output_shp)
        dst_layer = output_shapefile.CreateLayer(self.layer_name, geom_type=ogr.wkbPolygon, srs=self.srs)
        self.create_output_shp_fields(dst_layer)

        # covertion from raster to vector
        gdal.Polygonize(self.input_band, self.input_band, dst_layer, 0, [], callback=None)
        dst_layer.SyncToDisk()
        # get new layer
        datasource = self.shp_driver.Open(self.output_shp, 1)
        layer = datasource.GetLayerByName(self.layer_name)
        # assignment of a class to each polygon according to its pixel value
        for feature in layer:
            layer.SetFeature(feature)
            pixval = int(feature.GetField(self.id))
            if pixval in lables_dict:
                feature.SetField(1, lables_dict[pixval])
                layer.SetFeature(feature)

    def create_filtered_shapefile(self, class_value):
        """creats a shapfile for a given class"""
        output_shapefile = self.shp_driver.CreateDataSource(self.output_shp)
        dst_layer = output_shapefile.CreateLayer(self.layer_name, geom_type=ogr.wkbPolygon, srs=self.srs)
        self.create_output_shp_fields(dst_layer)

        raster_data = self.input_band.ReadAsArray()
        pix_vals = np.unique(raster_data)
        vals_lst = pix_vals.tolist()
        vals_lst.remove(class_value)
        self.reclassifyer(self.rasterpath, vals_lst, 0, outpath=self.output_shp, new_raster_name=self.layer_name + '_' + 'mask')

        mask = self.output_shp + '/' + self.layer_name + '_' + 'mask'
        open_mask = gdal.Open(mask)
        mask_band = open_mask.GetRasterBand(1)

        # covertion from raster to vector
        gdal.Polygonize(self.input_band, mask_band, dst_layer, 0, [], callback=None)
        dst_layer.SyncToDisk()

    @staticmethod
    def reclassifyer(raster_path, origclass, new_class, outpath, new_raster_name):
        """converts pixels from one class to another class
        args:
        raster_path- the path of the classified raster (str)
        origclass - the classes to be changed, can be one or more classes (lst)
        new_class - the new class value that will be assighned to the pixels with the origclass value
        outpath- the path where the reclassified raster will be saved (str)
        new_raser_name - the name for the reclassified raster (str)"""

        # open the classified raster
        raster = gdal.Open(raster_path)
        raster_band = raster.GetRasterBand(1)
        source_srs = raster.GetProjection()

        # read thr raster into an array
        raster_data = raster_band.ReadAsArray()

        # reclassification of pixels in the array
        for j in range(raster.RasterXSize):
            for i in range(raster.RasterYSize):
                pixval = (raster_data[i, j])
                if pixval in origclass:
                    raster_data[i, j] = new_class

        # set the output raster dimensions according to the reference raster file reference file:
        target_ds = gdal.GetDriverByName('GTiff').Create(outpath + new_raster_name, raster.RasterXSize,
                                                         raster.RasterYSize, 1, gdal.GDT_Byte)
        target_ds.SetGeoTransform(raster.GetGeoTransform())

        # set the output raster srs according to the original raster
        if source_srs is not None:
            target_ds.SetProjection(source_srs)

        # write the array into a the new reclassified raster
        target_ds.GetRasterBand(1).WriteArray(raster_data)
        print('DOne')


if __name__ == '__main__':

    opts, args = getopt.getopt(sys.argv[1:], 'rlon', ['raster=', 'labels_path=', 'out_shapefile=', 'layer_name='])
    layer_name = 'thematic'
    for opt, val in opts:
        if (opt in ('-r', '--raster')):
            raster_path = val
        elif (opt in ('-l', '--labels_path')):
            labels_path = val
        elif (opt in ('-o', '--out_shapefile')):
            out_shapefile = val
        elif (opt in ('-n', '--layer_name')):
            layer_name = val

    Polygonize(raster_path = raster_path, labels_path = labels_path, shapefile_path=out_shapefile, layer_name=layer_name)

    raster = '/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif'
    shpfile = '/home/inbal/inbal/gdal/outputs/polygonize/'
    lables = '/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm.lbl'


    poly2 = Polygonize(raster_path=raster, labels_path=lables, shapefile_path=shpfile, layer_name= 'byclass')
    poly2.create_filtered_shapefile(2)
