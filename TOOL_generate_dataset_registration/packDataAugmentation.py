import os
import cv2
import numpy as np

nonpack_path = os.getcwd() + r'/NON_PACK_DATASET/'
os.system('mkdir out')

def pack(path, msList, panList, fusionList, set_name, set_id):
	sample = []
	for file in msList:
		if(file in panList and file in fusionList):
			print("process : %s" % file)
			msFilePath = "%s/MS/%s" % (path, file)
			panFilePath = "%s/PAN/%s" % (path, file)
			fusionFilePath = "%s/FUSION/%s" % (path, file)
			
			msImg = cv2.imread(msFilePath, cv2.IMREAD_UNCHANGED)
			panImg = cv2.imread(panFilePath, cv2.IMREAD_GRAYSCALE)
			fusionImg = cv2.imread(fusionFilePath, cv2.IMREAD_UNCHANGED)
			# 原圖與鏡像
			sample.append(np.array({"MS":msImg, "PAN":panImg, "FUSION":fusionImg, "ID":file}))
			sample.append(np.array({"MS":np.fliplr(msImg), "PAN":np.fliplr(panImg), "FUSION":np.fliplr(fusionImg), "ID":file+"_flip"}))
			# 旋轉90度
			rotTime = 1
			sample.append(np.array({"MS":np.rot90(msImg, rotTime), "PAN":np.rot90(panImg, rotTime), "FUSION":np.rot90(fusionImg, rotTime), "ID":file+"_rot90"}))
			sample.append(np.array({"MS":np.rot90(np.fliplr(msImg), rotTime), "PAN":np.rot90(np.fliplr(panImg), rotTime), "FUSION":np.rot90(np.fliplr(fusionImg), rotTime), "ID":file+"_flip_rot90"}))
			# 旋轉180度
			rotTime = 2
			sample.append(np.array({"MS":np.rot90(msImg, rotTime), "PAN":np.rot90(panImg, rotTime), "FUSION":np.rot90(fusionImg, rotTime), "ID":file+"_rot180"}))
			sample.append(np.array({"MS":np.rot90(np.fliplr(msImg), rotTime), "PAN":np.rot90(np.fliplr(panImg), rotTime), "FUSION":np.rot90(np.fliplr(fusionImg), rotTime), "ID":file+"_flip_rot180"}))
			# 旋轉270度
			rotTime = 3
			sample.append(np.array({"MS":np.rot90(msImg, rotTime), "PAN":np.rot90(panImg, rotTime), "FUSION":np.rot90(fusionImg, rotTime), "ID":file+"_rot270"}))
			sample.append(np.array({"MS":np.rot90(np.fliplr(msImg), rotTime), "PAN":np.rot90(np.fliplr(panImg), rotTime), "FUSION":np.rot90(np.fliplr(fusionImg), rotTime), "ID":file+"_flip_rot270"}))
	print("count read : %s" % len(sample))
	np.savez_compressed("out/set%s_%s_sample" % (set_id, set_name), sample)

for id in os.listdir(nonpack_path):
	set_path = nonpack_path + r'%s/' % id
	positive_path = set_path + r'/POSITIVE'
	negative_path = set_path + r'/NEGATIVE'
	positive_ms_list = os.listdir(positive_path + r'/MS')
	positive_pan_list = os.listdir(positive_path + r'/PAN')
	positive_fusion_list = os.listdir(positive_path + r'/FUSION')

	negative_ms_list = os.listdir(negative_path + r'/MS')
	negative_pan_list = os.listdir(negative_path + r'/PAN')
	negative_fusion_list = os.listdir(negative_path + r'/FUSION')

	pack(positive_path, positive_ms_list, positive_pan_list, positive_fusion_list, "positive", id)
	pack(negative_path, negative_ms_list, negative_pan_list, negative_fusion_list, "negative", id)


