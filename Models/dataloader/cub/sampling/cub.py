import os
import os.path as osp

import torch
import numpy as np
from PIL import Image
from torch.utils.data import Dataset
from torchvision import transforms

class CUB(Dataset):

    def __init__(self, setname, args=None):
        IMAGE_PATH = os.path.join(args.data_dir, 'cub/')
        SPLIT_PATH = os.path.join(args.data_dir, 'cub/split/')
        txt_path = osp.join(SPLIT_PATH, setname + '.csv')
        lines = [x.strip() for x in open(txt_path, 'r').readlines()][1:]

        data = []
        label = []
        lb = -1
        self.wnids = []

        if setname == 'train':
            lines.pop(5864)#this image file is broken

        if 'num_patch' not in vars(args).keys():
            self.num_patch = 9
            print('no num_patch parameter, set as default:',self.num_patch)
        else:
            self.num_patch = args.num_patch

        for l in lines:
            context = l.split(',')
            name = context[0]
            wnid = context[1]
            path = osp.join(IMAGE_PATH, name)
            if wnid not in self.wnids:
                self.wnids.append(wnid)
                lb += 1

            data.append(path)
            label.append(lb)

        self.data = data
        self.label = label
        self.num_class = np.unique(np.array(label)).shape[0]

        image_size = 84
        self.transform = transforms.Compose([
            transforms.RandomResizedCrop(image_size),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(np.array([x / 255.0 for x in [125.3, 123.0, 113.9]]),
                                 np.array([x / 255.0 for x in [63.0, 62.1, 66.7]]))
        ])

    def __len__(self):
        return len(self.data)

    def __getitem__(self, i):
        path, label = self.data[i], self.label[i]
        patch_list = []
        for _ in range(self.num_patch):
            patch_list.append(self.transform(Image.open(path).convert('RGB')))

        patch_list = torch.stack(patch_list, dim=0)

        return patch_list, label


if __name__ == '__main__':
    pass