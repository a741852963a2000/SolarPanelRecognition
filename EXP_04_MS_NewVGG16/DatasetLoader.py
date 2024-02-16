import glob
import concurrent.futures
import numpy as np

def load_data(path='../DS_full_dataset/TrainingSet'):
	print(f'---- Load Cluster Dataset From: {path} ----')
	path = glob.escape(path) + '/*'
	with concurrent.futures.ThreadPoolExecutor() as executor:
		future = [executor.submit(load_npz, file_path) for file_path in glob.glob(path)]
		all_data = [f.result() for f in future]
	MS = np.concatenate([data['MS'] for data in all_data], axis=0)
	PAN = np.concatenate([data['PAN'] for data in all_data], axis=0)
	Fusion = np.concatenate([data['FUSION'] for data in all_data], axis=0)
	labels = np.concatenate([data['labels'] for data in all_data], axis=0)
	
	return {'MS':MS, 'PAN':PAN, 'FUSION':Fusion, 'labels':labels}

def norm(img):
	img = (img-127.5) / 255
	return img

def load_npz(file_path):
	label = [0,1] if 'positive' in file_path else [1,0]
	
	samples = np.load(file_path, allow_pickle=True)['arr_0']
	
	MS = np.array([sample[()]['MS'] for sample in samples], dtype=np.float32)
	PAN = np.array([sample[()]['PAN'] for sample in samples], dtype=np.float32)
	Fusion = np.array([sample[()]['FUSION'] for sample in samples], dtype=np.float32)
	labels = np.array([label] * len(MS))
	
	MS = norm(MS)
	PAN = norm(PAN)
	PAN = np.expand_dims(PAN, axis=-1)
	Fusion = norm(Fusion)
	
	print(f'file: {file_path} loaded')
	return {'MS':MS, 'PAN':PAN, 'FUSION':Fusion, 'labels':labels}