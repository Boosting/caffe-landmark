# coding: utf-8

import os
from os.path import join, exists
import time
import cv2
import math
import numpy as np
from .cnns import getCNNs


def logger(msg):
    """
        log message
    """
    now = time.ctime()
    print("[%s] %s" % (now, msg))

def createDir(p):
    if not os.path.exists(p):
        os.mkdir(p)
def shuffle_in_unison_scary_color(a1, a2, b1, b2, c1, c2):
    rng_state = np.random.get_state()
    np.random.shuffle(a1)
    np.random.set_state(rng_state)
    np.random.shuffle(b1)
    np.random.set_state(rng_state)
    np.random.shuffle(c1)
    np.random.set_state(rng_state)
    np.random.shuffle(a2)
    np.random.set_state(rng_state)
    np.random.shuffle(b2)
    np.random.set_state(rng_state)
    np.random.shuffle(c2)

def shuffle_in_unison_scary(a, b, c):
    rng_state = np.random.get_state()
    np.random.shuffle(a)
    np.random.set_state(rng_state)
    np.random.shuffle(b)
    np.random.set_state(rng_state)
    np.random.shuffle(c)

def drawLandmark(img, bbox, landmark):
    cv2.rectangle(img, (bbox.left, bbox.top), (bbox.right, bbox.bottom), (0,0,255), 2)
    for x, y in landmark:
        cv2.circle(img, (int(x), int(y)), 2, (0,255,0), -1)
    return img

def getDataFromTxt(txt, with_landmark=True):
    """
        Generate data from txt file
        return [(img_path, bbox, landmark)]
            bbox: [left, right, top, bottom]
            landmark: [(x1, y1), (x2, y2), ...]
    """
    dirname = os.path.dirname(txt)
    with open(txt, 'r') as fd:
        lines = fd.readlines()
    img_size = 1
    result = []
    for line in lines:
        line = line.strip()
        components = line.split(' ')
        img_path = os.path.join(dirname, components[0].replace('\\', '/')) # file path
        # bounding box, (left, right, top, bottom)
        bbox = (components[1], components[2], components[3], components[4])
        bbox = [int(_) for _ in bbox]
        # landmark
        if not with_landmark:
            result.append((img_path, BBox(bbox)))
            continue
        landmark = np.zeros((5, 2))
        eyeDist = np.zeros((1,1))
        for index in range(0, 5):
            rv = (float(components[5+2*index]), float(components[5+2*index+1]))
            landmark[index] = rv
        for index, one in enumerate(landmark):
            rv = ((one[0]-bbox[0])*img_size/(bbox[1]-bbox[0]), (one[1]-bbox[2])*img_size/(bbox[3]-bbox[2]))
            landmark[index] = rv
        eyeDist[0] = math.sqrt((landmark[0][0] - landmark[1][0])*(landmark[0][0] - landmark[1][0]) + (landmark[0][1] - landmark[1][1])*(landmark[0][1] - landmark[1][1]))
        result.append((img_path, BBox(bbox), landmark, eyeDist))
    return result

def getDataFromAFLWTxt(txt, with_landmark=True):
    """
        Generate data from txt file
        return [(img_path, bbox, landmark)]
            bbox: [left, right, top, bottom]
            landmark: [(x1, y1), (x2, y2), ...]
    """
    dirname = os.path.dirname(txt)
    with open(txt, 'r') as fd:
        lines = fd.readlines()
    img_size = 1
    result = []
    for line in lines:
        line = line.strip()
        components = line.split(' ')
        img_path = os.path.join(dirname, components[0].replace('\\', '/')) # file path
        # bounding box, (left, right, top, bottom)
        bbox = (components[1], components[2], components[3], components[4])
        bbox = [int(_) for _ in bbox]
        # landmark
        if not with_landmark:
            result.append((img_path, BBox(bbox)))
            continue
        landmark = np.zeros((5, 2))
        eyeDist = np.zeros((1,1))
        for index in range(0, 5):
            rv = (float(components[5+index]), float(components[10+index]))
            landmark[index] = rv
        for index, one in enumerate(landmark):
            rv = ((one[0]-bbox[0])*img_size/(bbox[1]-bbox[0]), (one[1]-bbox[2])*img_size/(bbox[3]-bbox[2]))
            landmark[index] = rv
        eyeDist[0] = math.sqrt((landmark[0][0] - landmark[1][0])*(landmark[0][0] - landmark[1][0]) + (landmark[0][1] - landmark[1][1])*(landmark[0][1] - landmark[1][1]))
        result.append((img_path, BBox(bbox), landmark, eyeDist))
    return result

def getPatch(img, bbox, point, padding):
    """
        Get a patch iamge around the given point in bbox with padding
        point: relative_point in [0, 1] in bbox
    """
    point_x = bbox.x + point[0] * bbox.w
    point_y = bbox.y + point[1] * bbox.h
    patch_left = point_x - bbox.w * padding
    patch_right = point_x + bbox.w * padding
    patch_top = point_y - bbox.h * padding
    patch_bottom = point_y + bbox.h * padding
    patch = img[patch_top: patch_bottom+1, patch_left: patch_right+1]
    patch_bbox = BBox([patch_left, patch_right, patch_top, patch_bottom])
    return patch, patch_bbox


def processImage(imgs, channel):
    """
        process images before feeding to CNNs
        imgs: N x 1 x W x H
    """
    imgs = imgs.astype(np.float32)
    if(channel == 1):
       m0 = np.mean(imgs[:,0,:,:],axis = 0)
       s0 = np.std(imgs[:,0,:,:],axis = 0)
       for i, img in enumerate(imgs):
           #m0 = imgs.mean()
           #s0 = imgs.std()
           imgs[i][0] = (imgs[i][0] - m0)/s0
    elif(channel == 3):
       m0 = np.mean(imgs[:,0,:,:],axis = 0)
       s0 = np.std(imgs[:,0,:,:],axis = 0)
       m1 = np.mean(imgs[:,1,:,:],axis = 0)
       s1 = np.std(imgs[:,1,:,:],axis = 0)
       m2 = np.mean(imgs[:,2,:,:],axis = 0)
       s2 = np.std(imgs[:,2,:,:],axis = 0)
       for i, img in enumerate(imgs):
           #m0 = imgs[i][0].mean()
           #s0 = imgs[i][0].std()
           #m1 = imgs[i][1].mean()
           #s1 = imgs[i][1].std()
           #m2 = imgs[i][2].mean()
           #s2 = imgs[i][2].std()
           imgs[i][0] = (imgs[i][0] - m0)/s0
           imgs[i][1] = (imgs[i][1] - m1)/s1
           imgs[i][2] = (imgs[i][2] - m2)/s2
    return imgs

def dataArgument(data):
    """
        dataArguments
        data:
            imgs: N x 1 x W x H
            bbox: N x BBox
            landmarks: N x 10
    """
    pass

class BBox(object):
    """
        Bounding Box of face
    """
    def __init__(self, bbox):
        self.left = bbox[0]
        self.right = bbox[1]
        self.top = bbox[2]
        self.bottom = bbox[3]
        self.x = bbox[0]
        self.y = bbox[2]
        self.w = bbox[1] - bbox[0]
        self.h = bbox[3] - bbox[2]

    def expand(self, scale=0.05):
        bbox = [self.left, self.right, self.top, self.bottom]
        bbox[0] -= int(self.w * scale)
        bbox[1] += int(self.w * scale)
        bbox[2] -= int(self.h * scale)
        bbox[3] += int(self.h * scale)
        return BBox(bbox)

    def project(self, point):
        x = (point[0]-self.x) / self.w
        y = (point[1]-self.y) / self.h
        return np.asarray([x, y])

    def reproject(self, point):
        x = self.x + self.w*point[0]
        y = self.y + self.h*point[1]
        return np.asarray([x, y])

    def reprojectLandmark(self, landmark):
        p = np.zeros((len(landmark), 2))
        for i in range(len(landmark)):
            p[i] = self.reproject(landmark[i])
        return p

    def projectLandmark(self, landmark):
        p = np.zeros((len(landmark), 2))
        for i in range(len(landmark)):
            p[i] = self.project(landmark[i])
        return p

    def subBBox(self, leftR, rightR, topR, bottomR, h, w):
        leftDelta = self.w * leftR
        rightDelta = self.w * rightR
        topDelta = self.h * topR
        bottomDelta = self.h * bottomR
        left = self.left + leftDelta
        if(left < 0):
           left = 0
        right = self.left + rightDelta
        if(right > w):
           right = w
        top = self.top + topDelta
        if(top < 0 ):
           top = 0
        bottom = self.top + bottomDelta
        if(bottom > h):
           bottom = h
        return BBox([left, right, top, bottom])
