from osgeo import gdal
from ShapefileReader import ShapefileReader

class GeoTiffTranslater:
	# 可以透過path list或單一path來建立
	def __init__(self, fileList=[]):
		self.imgList = []
		if(isinstance(fileList, str)):
			self.addFile(fileList)
		else:
			self.addFiles(fileList)
		return

	# 逐一讀取list中的檔案，並將其資訊加入list
	def addFiles(self, fileList):
		for path in fileList:
			self.addFile(path)
		return

	# 讀取單一檔案，並將其資訊加入list
	def addFile(self, path):
		img = gdal.Open(path)
		band = img.GetRasterBand(1)
		blockInfo = img.GetGeoTransform()
		xRange = sorted([blockInfo[0], blockInfo[0] + blockInfo[1] * band.XSize])
		yRange = sorted([blockInfo[3], blockInfo[3] + blockInfo[5] * band.YSize])
		# 建立影像資訊與範圍
		imgInfo = {
			'path':path,
			'xRange':xRange,
			'yRange':yRange
		}
		self.imgList.append(imgInfo)
		# 關閉檔案(另外一個方式是import _gdal，__swig_destroy__指向_gdal.delete_Dataset)
		img.__swig_destroy__(img)
		return

	# 尋找指定座標所屬圖片
	def findNearestImg(self, center):
		mean = lambda list: sum(list)/len(list)
		distanceCal = lambda img: (mean(img['xRange']) - center[0])**2 + (mean(img['yRange']) - center[1])**2
		return sorted(self.imgList, key=distanceCal)[0]

	# 檢查中心是否在圖片範圍內
	def containsCenter(self, center):
		between = lambda point,range : (point >= range[0] and point<= range[1])
		contain = False
		for image in self.imgList:
			xIn = between(center[0], image['xRange'])
			yIn = between(center[1], image['yRange'])
			if(xIn and yIn):
				contain = True
				break
		return contain

	# 透過中心點與大小來剪裁圖片
	def cutImageByCenter(self, centerList, boxSize, dst, id=0):
		between = lambda point,range : (point >= range[0] and point<= range[1])
		for center in centerList:
			target = self.findNearestImg(center)
			minX = center[0] - boxSize/2
			maxX = center[0] + boxSize/2
			minY = center[1] - boxSize/2
			maxY = center[1] + boxSize/2
			xIn = between(minX, target['xRange']) and between(maxX, target['xRange'])
			yIn = between(minY, target['yRange']) and between(maxY, target['yRange'])
			if(xIn and yIn):
				gdal.Translate(dst + r'\%d.tiff'%(id), target['path'], projWin=(minX, maxY, maxX, minY))
			id+=1
			print("cut id : %d" % id)
		return id

	# 透過中心點與大小來剪裁圖片
	def cutImageByCenterL(self, centerList, boxSize, dst, id=0):
		between = lambda point,range : (point >= range[0] and point<= range[1])
		for center in centerList:
			target = self.findNearestImg(center)
			minX = center[0] - boxSize/2
			maxX = center[0] + boxSize/2
			minY = center[1] - boxSize/2
			maxY = center[1] + boxSize/2
			xIn = between(minX, target['xRange']) and between(maxX, target['xRange'])
			yIn = between(minY, target['yRange']) and between(maxY, target['yRange'])
			if(xIn and yIn):
				gdal.Translate(dst + r'/%d.tiff'%(id), target['path'], projWin=(minX, maxY, maxX, minY))
			id+=1
			#print("cut id : %d" % id)
		return id

# class test
if __name__ == '__main__':
	fileList = [
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G004_MS_L4_20160118_020339_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G005_MS_L4_20160118_020342_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G015_MS_L4_20160109_020339_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G016_MS_L4_20160109_020342_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G030_MS_L4_20160126_020340_ot.tif'
	]
	panList = [
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G004_PAN_L4_20160118_020338_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G005_PAN_L4_20160118_020342_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G015_PAN_L4_20160109_020338_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G016_PAN_L4_20160109_020342_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G030_PAN_L4_20160126_020340_ot.tif'
	]
	shapefileList = [
		r'C:\Users\Administrator\Desktop\NSPO\農試所shape file\全台太陽能板.shp',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\D4SG SHP\D4SG.shp'
	]
	# construct object
	imgSource = GeoTiffTranslater(fileList)
	panSource = GeoTiffTranslater(panList)
	shapefile = ShapefileReader(shapefileList)
	# generate
	GEN_NEGATIVE = False
	if(GEN_NEGATIVE):
		print("generate negative samples")
		dst = r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\negative\MS'
		panDst = r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\negative\PAN'
		center = shapefile.getNagtiveSample()
		# remember to set id
		imgSource.cutImageByCenter(center, 200, dst, id=40000)
		panSource.cutImageByCenter(center, 200, panDst, id=40000)
	else:
		print("generate positive samples")
		dst = r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\positive\MS'
		panDst = r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\positive\PAN'
		center = shapefile.getProjectCenterRandom()
		# remember to set id
		imgSource.cutImageByCenter(center, 200, dst, id=0)
		panSource.cutImageByCenter(center, 200, panDst, id=0)
		

