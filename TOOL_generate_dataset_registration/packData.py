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
			sample.append(np.array({"MS":msImg, "PAN":panImg, "FUSION":fusionImg, "ID":file}))

	print("count read : %s" % len(sample))
	np.savez_compressed("no_argumentation_out/set%s_%s_sample" % (set_id, set_name), sample)

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


