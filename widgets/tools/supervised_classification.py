#open input

# -*- coding: utf-8 -*-
"""
Created on Tue Oct 25 18:07:51 2016

@author: alon
"""

# -*- coding: utf-8 -*-
"""
Created on Tue Oct  4 13:09:33 2016

@author: alon
"""

import sys
import numpy as np
# import os
__linux__o = True
epif = True

if not __linux__o:
    sys.path.append('/dvlp/misc/texturerecog_vs12/python_texturerecog/geosml')

sys.path.append('/home/inbal/inbal/python_texturerecog/')

from geosml import object_classifier as ocl

gpu_acc = True

if __linux__o:
    if epif:
        if gpu_acc:
            outPath = input_dict['outpath']

        dataset = input_dict['dataset']
        trainingSites = input_dict['trainingset'][0]
        roi = input_dict['roi'][0]
    else:
        if gpu_acc:
            outPath = input_dict['outpath']
        else:
            outPath = input_dict['outpath']

        dataset = input_dict['dataset']
        trainingSites = input_dict['trainingset'][0]
        roi = input_dict['roi'][0]
else:
    if gpu_acc:
        outPath = input_dict['outpath']
    else:
        outPath = input_dict['outpath']

    dataset = input_dict['dataset']
    trainingSites = input_dict['trainingset'][0]
    # roi = 'C:/ac/samples/metula/training/metula_roi.shp'
    roi = input_dict['roi'][0]

testArea = ''

bands = np.array(input_dict['bands'])
featureBands = np.array(input_dict['featurebands'])

bandNormalization = [
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
    ocl.ObjectClassifier.BandNormalization.cumulativeNormalization,
]
params = ocl.ObjectClassifier.Params()
params.gpuAcceleration = gpu_acc
params.classAttribute = input_dict['classname']
params.grid.minCellSize = input_dict['mincellsize']
params.grid.maxCellSize = input_dict['maxcellsize']
# params.grid.sizeRatio = 2.
# params.grid.minCellSampleFraction = .3
params.grid.overlapRatio = input_dict['ovelrlapratio']
params.grid.objectResolution = input_dict['objectresolution']
if epif:
    params.tileSize = 2000;
else:
    params.tileSize = 2000;

params.texture.minOccurenceDistance = input_dict['minocurencedistance']
params.texture.maxOccurenceDistance = input_dict['maxocurencedistance']

# params.texture.occurenceDistanceRatio = 2.
params.texture.levels = 32

params.texture.quantileRange = .999
params.texture.textureFeatures = 6

params.classifierModel = ocl.SVM_CLASSIFIER
params.maxTrainingSamples = 640000
params.maxTrainingSamples = 32000

params.scaleData = True
params.ngaussians = 1

params.dimensionalityReduction = 10
params.rejection = False
params.rejectionThreshold = 2.
params.applyPrediction = True

params.acceleration.gpuAcceleration = params.gpuAcceleration
params.acceleration.nstreams = 1
params.acceleration.concurrentStreams = 1
if epif:
    params.acceleration.maxMemoryAllocation = 4 * 1024 * 1024 * 1024
else:
    params.acceleration.maxMemoryAllocation = 2 * 1024 * 1024 * 1024

objectClassifier = ocl.ObjectClassifier(params)
objectClassifier.input.dataset = dataset
objectClassifier.input.trainingSites = trainingSites
objectClassifier.input.roi = roi
objectClassifier.process(bands, featureBands, outPath=outPath, bandNormalization=bandNormalization)

objectClassifier.computePerfMeasures(False)
# objectClassifier.computePerfMeasures(True)
