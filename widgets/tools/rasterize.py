from osgeo import gdal, ogr
import csv


class Rasterize:
    def __init__(self, shapefile_path, out_raster_path, reference_raster, out_raster_name='predicted_raster',
                 field_name='id', lables_file=None):
        shapefile_data_source = ogr.Open(shapefile_path, 1)
        reference = gdal.Open(reference_raster)
        self.source_layer = shapefile_data_source.GetLayer(0)
        self.srs = self.source_layer.GetSpatialRef()
        self.target_ds = gdal.GetDriverByName('GTiff').Create(out_raster_path + out_raster_name,reference.RasterXSize,
                                                              reference.RasterYSize, 1, gdal.GDT_Byte)
        self.target_ds.SetGeoTransform(reference.GetGeoTransform())
        self.field_name = field_name
        self.layerdefinition = self.source_layer.GetLayerDefn()
        self.targetfield = self.getfieldbyname()
        self.fieldslst = self.getfieldslist()
        if lables_file is not None:
            self.lables_file = open(lables_file)
            self.lablesdict = self.create_lables_vals_dict()
        self.rasterize()

    def create_lables_vals_dict(self):
        """ this function gets lables txt file and returns a dictionary in wich every lable(key) gets a pixel value """
        # mapping between the labels in labels file and pixel values(dict keys are labels and pixel values
        #  are dict values)

        # read csv into a list of labels:
        reader = csv.reader(self.lables_file, delimiter='\n')
        labels_lst = []
        for line in reader:
            labels_lst += line
        # create a dictionary for mapping between labels and pixel values:
        labels_dict = {}
        val = 0
        for i in labels_lst:
            val += 1
            labels_dict[i] = val
        return labels_dict

    def getfieldbyname(self):
        """ the function gets a field name and a layer definition and returns field definition of the
        desirable field """
        for i in range(self.layerdefinition.GetFieldCount()):
            if self.layerdefinition.GetFieldDefn(i).GetName() == self.field_name:
                fieldef = self.layerdefinition.GetFieldDefn(i)
                return fieldef

    def getfieldslist(self):
        """ the function get a layer definition and returns a list of fields in this layer """
        fieldlst = []
        for i in range(self.layerdefinition.GetFieldCount()):
            fieldlst += [self.layerdefinition.GetFieldDefn(i).GetName()]
        return fieldlst

    def rasterize(self):
        # set the output raster srs according to the input shapefile
        if self.srs is not None:
            self.target_ds.SetProjection(self.srs.ExportToWkt())
        # if fieldname is 'class' or another string type field:
        fieldtype = self.targetfield.GetType()
        if fieldtype == 'String':
            # if 'id' field exist use it for rasterization:
            if 'id' in self.fieldslst:
                self.field_name = 'id'
            # if 'id' field doesn't exist, create a new field 'id' with the matching pixel value for
            # each label and use it for rasterization
            else:
                # create a dictionary for labels and pixel values
                value_field = ogr.FieldDefn('id')
                self.source_layer.CreateField(value_field)
                # assign an id value for every feature in the layer
                for feature in self.source_layer:
                    self.source_layer.SetFeature(feature)
                    get_lable = feature.GetField('class')
                    if get_lable in self.lablesdict:
                        feature.SetField('id', self.lablesdict[get_lable])
                        self.source_layer.SetFeature(feature)
                        self.field_name = 'id'

        # Rasterization
        gdal.RasterizeLayer(self.target_ds, [1], self.source_layer, options=["ATTRIBUTE=" + self.field_name],
                            burn_values=[0])
        print('End')


if __name__ == '__main__':
    shapepath = '/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/thematic.shp'
    outpath = '/home/inbal/inbal/qgis_programing/standaloneapp/apptrials/'
    reference = '/home/inbal/inbal/gdal/outputs/rasterize/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_5.0_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif'

    ras = Rasterize(shapepath, outpath, reference, out_raster_name='metulapred.tif')

