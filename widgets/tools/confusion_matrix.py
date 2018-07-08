from osgeo import gdal
import numpy as np
import functools
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import itertools
import multiprocessing as multi


class Confusion_matrix:
    """ this function gets two raster files- one with true cell values and the other one with predicted cell values
    and compute a confusion matrix
    Args:
    true_raster_path(str): the path from which the true raster file will be imported
    predicted_raster_path(str): the path from which the predicted raster file will be imported
    export_path(str): the path where the matrix data fram will be exported to """

    def __init__(self, true_raster_path, predicted_raster_path, numpprocesses, outpath, show=False):
        # open the raster
        true_raster = gdal.Open(true_raster_path)
        predicted_raster = gdal.Open(predicted_raster_path)
        self.outpath = outpath
        self.numpprocesses = numpprocesses

        # read raster as ndrarray and split it into n nd arrays (n = number of processes)
        true_array = true_raster.GetRasterBand(1).ReadAsArray()
        predicted_array = predicted_raster.GetRasterBand(1).ReadAsArray()
        self.splittrue = np.array_split(true_array,  self.numpprocesses)
        self.splitpredicted = np.array_split(predicted_array,  self.numpprocesses)

        # get raster lables (unique pixel values)
        self.lables = np.unique(true_array)[1::]

        # collect the result of each process with Queue and move so dfs, than reduce the list of results in
        # dfs to self.final
        self.out_q = multi.Queue()
        self.dfs = []
        self.final = None
        self.processes_split()

        # visualize the confusion matrix with matplotlib and save it to outpath
        self.show = show
        self.show_matrix()



    def processes_split(self):
        """compute the confusion matrix with parallal processes"""
        processlst = []
        for i in range(self.numpprocesses):
            process = multi.Process(target=self.comput_matrix,
                                    args=(self.splittrue[i].ravel(), self.splitpredicted[i].ravel(),))
            process.start()
            processlst += [process]

        for process in processlst:
            process.join()
        for i in processlst:
            self.dfs += [self.out_q.get()]

        self.final = functools.reduce(lambda x, y: np.add(x, y), self.dfs)

    def comput_matrix(self, truesplit, predictedsplit):
        """ compute the confusion matrix with sklearn function- confusion_matrix(), with the true and predicted
         lists,and a list of lables as input """
        # compute the confusion matrix
        confusionmatrix = confusion_matrix(truesplit, predictedsplit, self.lables)
        self.out_q.put(confusionmatrix)

    def plot_confusion_matrix(self, normalize=False, title='Confusion matrix'):
        """This function prints and plots the confusion matrix.
        Normalization can be applied by setting `normalize=True`."""

        cm = self.final
        classes = self.lables

        if normalize:
            cm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis]
            print("Normalized confusion matrix")
        else:
            print('Confusion matrix, without normalization')

        cmap = plt.cm.Blues

        plt.imshow(cm, interpolation='nearest', cmap=cmap)
        plt.title(title)
        plt.colorbar()
        tick_marks = np.arange(len(classes))
        plt.xticks(tick_marks, classes, rotation=45)
        plt.yticks(tick_marks, classes)

        fmt = '.2f' if normalize else 'd'
        thresh = cm.max() / 2.
        for i, j in itertools.product(range(cm.shape[0]), range(cm.shape[1])):
            plt.text(j, i, format(cm[i, j], fmt),
                     horizontalalignment="center",
                     color="white" if cm[i, j] > thresh else "black")

        plt.tight_layout()
        plt.ylabel('True label')
        plt.xlabel('Predicted label')

    def show_matrix(self):
        """save png of the matrix with matplotlib. if 'show' is true this function will visualize
        the computed normalized and not normalized confusion matrix"""

        np.set_printoptions(precision=2)
        # Plot non-normalized confusion matrix
        plt.figure()
        self.plot_confusion_matrix(title='Confusion matrix, without normalization')
        plt.savefig(self.outpath + '/'+ 'confusion_matrix')

        # Plot normalized confusion matrix
        plt.figure()
        self.plot_confusion_matrix(normalize=True, title='Normalized confusion matrix')
        plt.savefig(self.outpath + '/' + 'normalized_confusion_matrix')

        if self.show is True:
            plt.show()


if __name__ == '__main__':

    trueras = '/home/inbal/data/metula/out_supervised2/B_00_01_02_03_FB_00_01_02_03_11_12_33_OR_2.5_CS2.5_20.0_OC_1.0_8.0_CL_32_TF_6_scl_svm__model.svm_OV_0.5_gpu0__llkMap.tif'
    predras = '/home/inbal/inbal/gdal/outputs/rasterize/outputsmetulapred'
    exppath = '/home/inbal/inbal/gdal/outputs/rasterize'

    con = Confusion_matrix(trueras, predras, 10, exppath, False)








