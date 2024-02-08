# Copyright (c) OpenMMLab. All rights reserved.
#!pip install opencv-python
#!pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
#!pip install ood-metrics

import os
import cv2
import glob
import torch
import random
from PIL import Image
import numpy as np
from erfnet import ERFNet
import os.path as osp

import torch.nn.functional as F

from argparse import ArgumentParser
from ood_metrics import fpr_at_95_tpr, calc_metrics, plot_roc, plot_pr,plot_barcode
from sklearn.metrics import roc_auc_score, roc_curve, auc, precision_recall_curve, average_precision_score


print("GPU disponibile:" , torch.cuda.is_available())
seed = 42

# general reproducibility
random.seed(seed)
np.random.seed(seed)
torch.manual_seed(seed)

NUM_CHANNELS = 3
NUM_CLASSES = 20
# gpu training specific
torch.backends.cudnn.deterministic = True
torch.backends.cudnn.benchmark = True

def main():
       
    parser = ArgumentParser()
    parser.add_argument(
        "--input",
        default="~39347\\Desktop\\DAAI_Project\\eval\\Validation_Dataset\\RoadAnomaly\\images\\*.jpg",
        nargs="+")
    
    
    ##DATASETS - PATHS
    
    # RoadObsticle21
    # ~39347\\Desktop\\DAAI_Project\\eval\\Validation_Dataset\\RoadObsticle21\\images\\*.webp
    
    # FS_LostFound_full
    # ~39347\\Desktop\\DAAI_Project\\eval\\Validation_Dataset\\FS_LostFound_full\\images\\*.png
    
    # fs_static
    # ~39347\\Desktop\\DAAI_Project\\eval\\Validation_Dataset\\fs_static\\images\\*.jpg
    
    # RoadAnomaly
    # ~39347\\Desktop\\DAAI_Project\\eval\\Validation_Dataset\\RoadAnomaly\\images\\*.jpg
    
    # RoadAnomaly21
    # ~39347\\Desktop\\DAAI_Project\\eval\\Validation_Dataset\\RoadAnomaly21\\images\\*.png
    
    parser.add_argument('--loadDir',default="../trained_models/")
    parser.add_argument('--loadWeights', default="erfnet_pretrained.pth")
    parser.add_argument('--loadModel', default="erfnet.py")
    parser.add_argument('--subset', default="val")  #can be val or train (must have labels)
    parser.add_argument('--datadir', default="/home/shyam/ViT-Adapter/segmentation/data/cityscapes/")
    parser.add_argument('--num-workers', type=int, default=4)
    parser.add_argument('--batch-size', type=int, default=1)
    parser.add_argument('--cpu', action='store_true')
    args = parser.parse_args()
    anomaly_score_list = []
    ood_gts_list = []

    if not os.path.exists('results.txt'):
        open('results.txt', 'w').close()
    file = open('results.txt', 'a')

    modelpath = args.loadDir + args.loadModel
    weightspath = args.loadDir + args.loadWeights

    print ("Loading model: " + modelpath)
    print ("Loading weights: " + weightspath)

    model = ERFNet(NUM_CLASSES)

    if (not args.cpu):
        model = torch.nn.DataParallel(model).cuda()

    def load_my_state_dict(model, state_dict):  #custom function to load model when not all dict elements
        own_state = model.state_dict()
        for name, param in state_dict.items():
            if name not in own_state:
                if name.startswith("module."):
                    own_state[name.split("module.")[-1]].copy_(param)
                else:
                    print(name, " not loaded")
                    continue
            else:
                own_state[name].copy_(param)
        return model

    model = load_my_state_dict(model, torch.load(weightspath, map_location=lambda storage, loc: storage))
    print ("Model and weights LOADED successfully")
    model.eval()

    for path in glob.glob(os.path.expanduser(str(args.input))):
       
        #print(path)
        
        images = torch.from_numpy(np.array(Image.open(path).convert('RGB'))).unsqueeze(0).float()
        images = images.permute(0,3,1,2)
        with torch.no_grad():
            result = model(images)
        
        ## MaxLogit
        #anomaly_result = 1.0 - np.max(result.squeeze(0).data.cpu().numpy(), axis=0)            
        
        ## MSP
        #softmax_probs = F.softmax(result.squeeze(0), dim=0)
        #anomaly_result = 1-(np.max(softmax_probs.data.cpu().numpy(), axis=0))
        
        ## MSP - Temperature
        #temperature = 0.5
        #temperature = 0.75
        #temperature = 1.1
        #softmax_probs = F.softmax(result.squeeze(0) / temperature, dim=0)
        #anomaly_result = 1-(np.max(softmax_probs.data.cpu().numpy(), axis=0))
        
        ## Max entropy
        softmax_probs = F.softmax(result.squeeze(0), dim=0)+1e-8
        #print(softmax_probs.size())
        #print(result.squeeze(0).size())
    
        anomaly_result = torch.div(torch.sum(-softmax_probs * F.log_softmax(result.squeeze(0), dim=0), dim=0), torch.log(torch.tensor(result.size(0), dtype=torch.float))+1e-8)
        anomaly_result = anomaly_result.data.cpu().numpy()
        #print(anomaly_result)
        
        pathGT = path.replace("images", "labels_masks")                
        if "RoadObsticle21" in pathGT:
           pathGT = pathGT.replace("webp", "png")
        if "fs_static" in pathGT:
           pathGT = pathGT.replace("jpg", "png")                
        if "RoadAnomaly" in pathGT:
           pathGT = pathGT.replace("jpg", "png")  

        mask = Image.open(pathGT)
        ood_gts = np.array(mask)

        if "RoadAnomaly" in pathGT:
            ood_gts = np.where((ood_gts==2), 1, ood_gts)
        if "LostAndFound" in pathGT:
            ood_gts = np.where((ood_gts==0), 255, ood_gts)
            ood_gts = np.where((ood_gts==1), 0, ood_gts)
            ood_gts = np.where((ood_gts>1)&(ood_gts<201), 1, ood_gts)

        if "Streethazard" in pathGT:
            ood_gts = np.where((ood_gts==14), 255, ood_gts)
            ood_gts = np.where((ood_gts<20), 0, ood_gts)
            ood_gts = np.where((ood_gts==255), 1, ood_gts)

        if 1 not in np.unique(ood_gts):
            continue              
        else:
             ood_gts_list.append(ood_gts)
             anomaly_score_list.append(anomaly_result)
        del result, anomaly_result, ood_gts, mask
        torch.cuda.empty_cache()

    file.write( "\n")

    ood_gts = np.array(ood_gts_list)
    anomaly_scores = np.array(anomaly_score_list)

    ood_mask = (ood_gts == 1)
    ind_mask = (ood_gts == 0)

    ood_out = anomaly_scores[ood_mask]
    ind_out = anomaly_scores[ind_mask]

    ood_label = np.ones(len(ood_out))
    ind_label = np.zeros(len(ind_out))
    
    val_out = np.concatenate((ind_out, ood_out))
    val_label = np.concatenate((ind_label, ood_label))

    prc_auc = average_precision_score(val_label, val_out)
    fpr = fpr_at_95_tpr(val_out, val_label)

    print(f'AUPRC score: {prc_auc*100.0}')
    print(f'FPR@TPR95: {fpr*100.0}')

    file.write(('    AUPRC score:' + str(prc_auc*100.0) + '   FPR@TPR95:' + str(fpr*100.0) ))
    file.close()

if __name__ == '__main__':
    main()