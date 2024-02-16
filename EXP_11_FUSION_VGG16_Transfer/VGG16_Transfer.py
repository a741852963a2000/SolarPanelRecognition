import tensorflow as tf
from tensorflow.keras.layers import *
import numpy as np

import os

class VGG16_Transfer():
	def __init__(self, weightDir='./weight'):
		self.name = 'VGG16_Transfer'
		self.weightPath = '%s/%s.h5' % (weightDir, self.name)
		
		self.model = self.createModel()
		self.loadWeights()

	def saveWeights(self):
		self.model.save_weights(self.weightPath)

	def loadWeights(self):
		if os.path.isfile(self.weightPath):
			self.model.load_weights(self.weightPath)

	def createModel(self):
		input = Input(shape=(60, 60, 3), name='MS_input')
		
		Model = tf.keras.applications.vgg16.VGG16(include_top=False, weights='imagenet', input_tensor=input)
		Model.trainable = False
		
		layer = Flatten(name='flatten')(Model.output)
		layer = Dense(256, activation='relu', name='dense_0')(layer)
		layer = Dropout(0.3, name='dropout')(layer)
		output_layer = Dense(2, activation='softmax', name='dense_1')(layer)
		
		model = tf.keras.Model(inputs=[input, ], outputs=[output_layer], name=self.name)
		return model