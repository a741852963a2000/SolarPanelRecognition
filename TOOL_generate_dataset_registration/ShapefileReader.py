from osgeo import ogr
from random import random
from random import randint
import datetime
import concurrent.futures

class ShapefileReader:
	# 可以透過path list或單一path來建立
	def __init__(self, fileList=[]):
		self.shapes = []
		if(isinstance(fileList, str)):
			self.addFile(fileList)
		else:
			self.addFiles(fileList)
		return

	# 逐一讀取list中的檔案，並將其shape加入list
	def addFiles(self, fileList):
		for path in fileList:
			self.addFile(path)
		return

	# 讀取單一檔案，並將其shape加入list
	def addFile(self, path):
		dataSource = ogr.GetDriverByName('ESRI Shapefile').Open(path)
		if dataSource is None:
			print('Could not open Shapefile : %s' % (path))
		else:
			layer = dataSource.GetLayer()
			for shape in layer:
				# 圖層中包含一個Layer是沒有形狀的，必須濾掉
				if(shape.geometry() is not None):
					# 因為讀取後會做release，這邊必須進行clone
					self.shapes.append(shape.geometry().Clone())
			# release data source
			dataSource.Release()
		return

	# 取得所有shape的原始物件
	def getGeometry(self):
		return self.shapes[:]

	# 由座標產生位移
	@staticmethod
	def makeShift(point, shift, mode=8):
		result = [];
		if mode == 8:
			result = [(point[0] + shx,point[1] + shy) for shx in [-shift, 0, shift] for shy in [-shift, 0, shift]]
		elif mode == 4:
			result = [(point[0] + sh[0],point[1] + sh[1]) for sh in [(0,0), (0, shift), (0, -shift), (shift, 0), (-shift, 0)]]
		return result

	# 由座標產生隨機位移
	@staticmethod
	def makeRandomShift(point, shiftLimit, number):
		result = [];
		shl = [(randint(-shiftLimit, shiftLimit), randint(-shiftLimit, shiftLimit)) for x in range(number)]
		shl.append((0,0))
		result = [(point[0] + sh[0], point[1] + sh[1]) for sh in shl]
		return result

	# 產生檢查用幾何物件
	@staticmethod
	def makeGeometry(center, size):
		r = size/2
		poly = "POLYGON ((%f %f, %f %f, %f %f, %f %f, %f %f))" % (
			center[0] + r, center[1] + r, 
			center[0] + r, center[1] - r, 
			center[0] - r, center[1] - r, 
			center[0] - r, center[1] + r, 
			center[0] + r, center[1] + r, 
		)
		return ogr.CreateGeometryFromWkt(poly)

	# 檢查shape的長寬限制
	@staticmethod
	def checkGeometrySize(shape, limit, mode="BOTH"):
		bound = shape.GetEnvelope()
		hw = [abs(bound[0] - bound[1]),abs(bound[2] - bound[3])]
		if mode == "BOTH":
			return min(hw) >= limit
		elif mode == "SINGLE":
			return max(hw) >= limit
		elif mode == "NOTPASS":
			return max(hw) < limit
		else:
			return

	# 取得幾何物件的中心點
	@staticmethod
	def getGeometryCenter(shape):
		return ((shape.GetEnvelope()[0] + shape.GetEnvelope()[1])/2, 
				(shape.GetEnvelope()[2] + shape.GetEnvelope()[3])/2)

	# 增加安全檢查的幾何物件重疊面積計算
	@staticmethod
	def getGeometryIntersectionArea(a, b):
		if (a.GetArea() * b.GetArea() > 0) and (a.Overlaps(b)):
			if(a.Intersection(b) is not None):
				return a.Intersection(b).GetArea()
		return 0
	
	# 取得所有shape的bounding box
	def getBoundingBox(self):
		return [shape.GetEnvelope() for shape in self.shapes]

	# 取得所有bounding box的中心點
	def getCenter(self):
		return [self.getGeometryCenter(shape) for shape in self.shapes]

	# 取得長寬皆大於8M的bounding box的中心點
	def getValidCenter(self):
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		return [self.getGeometryCenter(shape) for shape in validShape]

	# 取得專案所採用的中心點
	def getProjectCenterShift100Dir4Shift50Dir8(self):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		result = []
		for shape in validShape:
			center = self.getGeometryCenter(shape)
			area = shape.GetArea()
			newBox = [self.makeGeometry(center, 200) for center in self.makeShift(center, shift=100, mode=4)]
			newBox += [self.makeGeometry(center, 200) for center in self.makeShift(center, shift=50, mode=8)]
			centerList = [
				self.getGeometryCenter(box)
				for box in newBox
				if (self.getGeometryIntersectionArea(shape, box) / area) >= 0.5
			]
			centerList.append(center)
			result += centerList
		return result

	# 產生第二版正樣本，大小200M*200M，隨機移動100M，預設20+1個，包含樣本50%以上
	def getProjectCenterRandom(self, num=20):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		result = []
		for shape in validShape:
			center = self.getGeometryCenter(shape)
			area = shape.GetArea()
			newBox = [self.makeGeometry(center, 200) for center in self.makeRandomShift(center, shiftLimit=100, number=num)]
			centerList = [
				self.getGeometryCenter(box)
				for box in newBox
				if (self.getGeometryIntersectionArea(shape, box) / area) >= 0.5
			]
			centerList.append(center)
			result += centerList
		return result

	# 產生第三版正樣本，大小120M*120M，隨機移動60M，預設20+1個，包含樣本50%以上
	def getCenterV3(self, num=20):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		result = []
		for shape in validShape:
			center = self.getGeometryCenter(shape)
			area = shape.GetArea()
			newBox = [self.makeGeometry(center, 120) for center in self.makeRandomShift(center, shiftLimit=60, number=num)]
			centerList = [
				self.getGeometryCenter(box)
				for box in newBox
				if (self.getGeometryIntersectionArea(shape, box) / area) >= 0.5
			]
			centerList.append(center)
			result += centerList
		return result

	def getCenterV3MT(self, num=20):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		# 定義工作函數
		def GCV3(self, shape):
			center = self.getGeometryCenter(shape)
			area = shape.GetArea()
			newBox = [self.makeGeometry(center, 120) for center in self.makeRandomShift(center, shiftLimit=60, number=num)]
			centerList = [
				self.getGeometryCenter(box)
				for box in newBox
				if (self.getGeometryIntersectionArea(shape, box) / area) >= 0.5
			]
			centerList.append(center)
			return centerList
		# 平行處理
		with concurrent.futures.ThreadPoolExecutor() as executor:
			excutors = [executor.submit(GCV3, self, shape) for shape in validShape]
			results = [excutor.result() for excutor in excutors]
		result = []
		for r in results:
			result += r
		return result

	# 產生第三版負樣本，大小120M*120M，隨機移動120M，預設20個，不與任一正樣本重疊
	def getNegativeCenterV3(self, num=20):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		result = []
		i=0
		for shape in validShape:
			center = self.getGeometryCenter(shape)
			randBox = [self.makeGeometry(center, 120) for center in self.makeRandomShift(center, shiftLimit=120, number=num)]
			newBox = []
			print("[%s] Gnerate negative sample of shape : %6d/%6d" % (datetime.datetime.now().strftime('%H:%M:%S'), i, len(validShape)))
			i+=1
			for box in randBox:
				if sum([box.Intersection(shape).GetArea() for shape in self.shapes if box.Intersection(shape) is not None]) == 0:
					newBox.append(box)
			result += [self.getGeometryCenter(box) for box in newBox]
		return result

	# 產生第三版負樣本，大小120M*120M，隨機移動120M，預設20個，不與任一正樣本重疊
	def getNegativeCenterV3MT(self, num=20):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		# 定義工作函數
		def GNCV3(self, shape):
			center = self.getGeometryCenter(shape)
			randBox = [self.makeGeometry(center, 120) for center in self.makeRandomShift(center, shiftLimit=120, number=num)]
			newBox = []
			for box in randBox:
				if sum([box.Intersection(shape).GetArea() for shape in self.shapes if box.Intersection(shape) is not None]) == 0:
					newBox.append(box)
			return [self.getGeometryCenter(box) for box in newBox]
		# 平行處理
		with concurrent.futures.ThreadPoolExecutor() as executor:
			excutors = [executor.submit(GNCV3, self, shape) for shape in validShape]
			results = [excutor.result() for excutor in excutors]
		result = []
		for r in results:
			result += r
		return result

	# 產生第三版正樣本，大小120M*120M，隨機移動60M，預設20+1個，包含樣本可調整以上
	def getCenterV3Percent(self, num=20, pmin=0.5, pmax=1.0):
		# 只採用長寬皆大於8m的shape
		validShape = [shape for shape in self.shapes if self.checkGeometrySize(shape, 8, "BOTH")]
		between = lambda x, min, max:(x > min and x <= max)
		boxList = []
		for shape in validShape:
			center = self.getGeometryCenter(shape)
			area = shape.GetArea()
			newBox = [self.makeGeometry(center, 120) for center in self.makeRandomShift(center, shiftLimit=int(120*(1-pmin)), number=num)]
			boxList += newBox
		result = []
		shapeList = self.shapes
		for (i, box) in enumerate(boxList):
			print('process %d / %d' % (i, len(boxList)))
			iList = []
			boxCenter = self.getGeometryCenter(box)
			for shape in shapeList:
				shapeCenter = self.getGeometryCenter(shape)
				if abs(boxCenter[0] - shapeCenter[0]) <= 120 and abs(boxCenter[1] - shapeCenter[1]) <= 120:
					intersection = box.Intersection(shape)
					if intersection is None:
						shapeList.remove(shape)
					elif intersection.GetArea() != 0 :
						iList.append(intersection.GetArea()/shape.GetArea())
			if(len(iList)==1 and iList[0] > pmin and iList[0] <= pmax):
				result.append(self.getGeometryCenter(box))
		return result

	# 取得現有shape數量
	def getShapeCount(self):
		return len(self.shapes)

	# 產生負樣本
	def getNagtiveSample(self):
		# x in 160000~230000, y in 2590000~2540000
		randX = lambda : 160000 + 70000 * random()
		randY = lambda : 2590000 + 40000 * random()
		randClip = [self.makeGeometry((randX(), randY()), 200) for i in range(160000)]
		result = []
		i=0
		for clip in randClip:
			print(i)
			i+=1
			if sum([shape.Overlaps(clip) for shape in self.shapes]) == 0:
				result.append(clip)
		return [self.getGeometryCenter(clip) for clip in result]

# class test
if __name__ == '__main__':
	fileList = [
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G004_MS_L4_20160118_020339_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G005_MS_L4_20160118_020342_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G015_MS_L4_20160109_020339_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G016_MS_L4_20160109_020342_ot.tif',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\FS2_G030_MS_L4_20160126_020340_ot.tif'
	]
	imgSource = GeoTiffTranslater(fileList)
	
	fileList = [
		#r'C:\Users\Administrator\Desktop\NSPO\農試所shape file\全台太陽能板.shp',
		r'C:\Users\Administrator\Desktop\NSPO\NSPO\2017_07_11\D4SG SHP\D4SG.shp'
	]
	shapefile = ShapefileReader(fileList)
	shapeList = []
	for geo in shapefile.getGeometry():
		x = geo.GetEnvelope()
		center = shapefile.getGeometryCenter(geo)
		if imgSource.containsCenter(center):
			shapeList.append({'width':x[1]-x[0], 'length':x[3]-x[2], 'area':geo.GetArea(), 'center':center})
	
	print('width', 'length', 'area', 'center', 'source', sep='\t')
	for shape in shapeList:
		print(shape['width'], shape['length'], shape['area'], (shape['center']), 'D4SG', sep='\t')

