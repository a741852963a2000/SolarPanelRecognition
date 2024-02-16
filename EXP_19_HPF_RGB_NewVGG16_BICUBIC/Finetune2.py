import numpy as np

import tensorflow as tf

from HPF_RGB_NewVGG16 import HPF_RGB_NewVGG16
from DatasetLoader import load_data

def main():
	batchSize = 256
	
	model = HPF_RGB_NewVGG16()
	trainer = Trainer(model)
	data = load_data(path='../DS_full_dataset/TrainingSet')
	
	trainer.train(
		data=data,
		batchSize=batchSize,
		initialEpoch=0,
		endEpochs=2000,
		learningRate=1e-6,
	)

class Trainer():
	def __init__(self, model):
		self.model = model

	def train(self, data, batchSize, initialEpoch, endEpochs, learningRate=1e-3):
		print('start to train')

		#create casllback
		checkpoint = tf.keras.callbacks.ModelCheckpoint(self.model.weightPath, monitor='loss', mode='min', verbose=0, save_best_only=True, save_weights_only=True)
		early_stopping = tf.keras.callbacks.EarlyStopping(monitor='loss', min_delta=0.001, patience=20, verbose=1)
		callbacks = [checkpoint, early_stopping]

		#create parameter
		optimizer = tf.keras.optimizers.Adam(learning_rate=learningRate)
		metrics = [
			'acc',
		]
		loss = ["categorical_crossentropy"]
		lossWeight = [1]

		#compiling models
		model = self.model.model
		model.trainable=True
		model.compile(loss=loss, loss_weights=lossWeight, metrics=metrics, optimizer=optimizer)

		#training
		x = (data['PAN'], data['MS'][:,:,:,:3])
		y = (data['labels'])
		history = model.fit(x=x, y=y, batch_size=batchSize, epochs=endEpochs, initial_epoch=initialEpoch, callbacks=callbacks, workers=31, shuffle=True)

if __name__ == '__main__':
	main()