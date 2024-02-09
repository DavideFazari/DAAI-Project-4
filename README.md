# Real-Time-Anomaly-Segmentation Project
This repository provides all the material used for the Real-Time Anomaly Segmentation project of the Data Analysis and Artificial Intelligence course. 

## Packages
For instructions, please refer to the README in each folder:

* [train](train) contains tools for training the network for semantic segmentation.
* [eval](eval) contains tools for evaluating/visualizing the network's output and performing anomaly segmentation.
* [imagenet](imagenet) Contains script and model for pretraining ERFNet's encoder in Imagenet.
* [trained_models](trained_models) Contains the trained models used in the papers.
* [createTrainIdLabelImgs](createTrainIdLabelImgs) Contains the function that allow to convert the polygonal annotations of the Cityscapes dataset to images, where pixel values encode ground truth classes.
* [cityscapesScripts-master](cityscapesScripts-master) Contains the some scripts that were downloaded with the Cityscapes dataset.
* The Cityscapes dataset This folder is actually empty 
* In this folder were present the "leftImg8bit" and the "gtFine" folders. The first contains the RGB images instead the second contains the labels. 
