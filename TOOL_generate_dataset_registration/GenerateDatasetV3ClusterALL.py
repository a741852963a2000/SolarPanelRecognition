from osgeo import gdal
from ShapefileReader import ShapefileReader
from GeoTiffTranslater import GeoTiffTranslater
import os

if __name__ == '__main__':
	fusionList = [
	r'./source_data/G004_PANSHARPEN.tif',
	r'./source_data/G005_PANSHARPEN.tif',
	r'./source_data/G015_PANSHARPEN.tif',
	r'./source_data/G016_PANSHARPEN.tif',
	r'./source_data/G030_PANSHARPEN.tif',
	]
	msList = [
		r'./source_data/G004_MS.tif',
	r'./source_data/G005_MS.tif',
	r'./source_data/G015_MS.tif',
	r'./source_data/G016_MS.tif',
	r'./source_data/G030_MS.tif',
	]
	panList = [
		r'./source_data/G004_PAN.tif',
	r'./source_data/G005_PAN.tif',
	r'./source_data/G015_PAN.tif',
	r'./source_data/G016_PAN.tif',
	r'./source_data/G030_PAN.tif',
	]
	shapefileList = [
		r'./shape_file/D4SG_cluster_0_of_3.shp',
		r'./shape_file/D4SG_cluster_1_of_3.shp',
		r'./shape_file/D4SG_cluster_2_of_3.shp',
	]

	# construct object
	fusionSource = GeoTiffTranslater(fusionList)
	msSource = GeoTiffTranslater(msList)
	panSource = GeoTiffTranslater(panList)
	shapefiles = [ShapefileReader(shapefilePath) for shapefilePath in shapefileList]
	print("----- generate negative centers -----")
	negative_centers = [shapefile.getNegativeCenterV3MT(num=20) for shapefile in shapefiles]
	print("----- generate positive centers -----")
	positive_centers = [shapefile.getCenterV3MT(num=20) for shapefile in shapefiles]
	
	def mkdir(path):
		if not os.path.exists(path):
			os.makedirs(path)
	
	for i in range(len(shapefileList)):
		outpu_dir = r'./NON_PACK_DATASET/%s' % (i)
		postive_dst = outpu_dir + r'/POSITIVE'
		negative_dst = outpu_dir + r'/NEGATIVE'
		mkdir(outpu_dir)
		mkdir(postive_dst)
		mkdir(negative_dst)
		mkdir(postive_dst + '/FUSION')
		mkdir(postive_dst + '/MS')
		mkdir(postive_dst + '/PAN')
		mkdir(negative_dst + '/FUSION')
		mkdir(negative_dst + '/MS')
		mkdir(negative_dst + '/PAN')
		
		print("generate negative samples %d" % (i))
		start_id = 0
		fusionSource.cutImageByCenterL(negative_centers[i], 120, negative_dst + '/FUSION', id=start_id)
		msSource.cutImageByCenterL(negative_centers[i], 120, negative_dst + '/MS', id=start_id)
		panSource.cutImageByCenterL(negative_centers[i], 120, negative_dst + '/PAN', id=start_id)

		print("generate positive samples %d" % (i))
		fusionSource.cutImageByCenterL(positive_centers[i], 120, postive_dst + '/FUSION', id=start_id)
		msSource.cutImageByCenterL(positive_centers[i], 120, postive_dst + '/MS', id=start_id)
		panSource.cutImageByCenterL(positive_centers[i], 120, postive_dst + '/PAN', id=start_id)
