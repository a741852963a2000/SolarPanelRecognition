import numpy as np

from tensorflow import keras
import tensorflow as tf

from HPF_MS_NewVGG16 import HPF_MS_NewVGG16
from DatasetLoader import load_data

def main():
	batchSize = 256
	model = HPF_MS_NewVGG16()
	data = load_data(path='../DS_full_dataset/TestSet')
	
	metrics = {
		'Precision':tf.keras.metrics.Precision(),
		'Recall':tf.keras.metrics.Recall(),
		'Accuracy':tf.keras.metrics.Accuracy(),
		'TP':tf.keras.metrics.TruePositives(),
		'FN':tf.keras.metrics.FalseNegatives(),
		'FP':tf.keras.metrics.FalsePositives(),
		'TN':tf.keras.metrics.TrueNegatives(),
	}
	model.model.compile(optimizer='sgd', loss='mse')
	y_pred = model.model.predict(x=(data['PAN'], data['MS']), batch_size=batchSize, verbose=2)
	
	y_pred = np.argmax(y_pred, axis=1)
	y_true = np.argmax(data['labels'], axis=1)
	
	[v.update_state(y_true, y_pred) for k, v in metrics.items()]
	metrics = {k: v.result().numpy() for (k, v) in metrics.items()}
	p = metrics['Precision']
	r = metrics['Recall']
	metrics.update({'F1':(2 * p * r / (p+r))})
	print(metrics)



if __name__ == '__main__':
	main()