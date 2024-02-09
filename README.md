# DAAI-Project-4
Project 4 Delivery

# Real-Time-Anomaly-Segmentation [Course Project]
This repository provides a starter-code setup for the Real-Time Anomaly Segmentation project of the Machine Learning Course. It consists of the code base for training ERFNet on the Cityscapes dataset and perform anomaly segmentation.

## Packages
For instructions, please refer to the README in each folder:

* [train](train) contains tools for training the network for semantic segmentation.
* [eval](eval) contains tools for evaluating/visualizing the network's output and performing anomaly segmentation.
* [imagenet](imagenet) Contains script and model for pretraining ERFNet's encoder in Imagenet.
* [trained_models](trained_models) Contains the trained models used in the papers. 

## Requirements:

* **The Cityscapes dataset**: Download the "leftImg8bit" for the RGB images and the "gtFine" for the labels. **Please note that for training you should use the "_labelTrainIds" and not the "_labelIds", you can download the [cityscapes scripts](https://github.com/mcordts/cityscapesScripts) and use the [conversor](https://github.com/mcordts/cityscapesScripts/blob/master/cityscapesscripts/preparation/createTrainIdLabelImgs.py) to generate trainIds from labelIds**
* **Python 3.6**: If you don't have Python3.6 in your system, I recommend installing it with [Anaconda](https://www.anaconda.com/download/#linux)
* **PyTorch**: Make sure to install the Pytorch version for Python 3.6 with CUDA support (code only tested for CUDA 8.0). 
