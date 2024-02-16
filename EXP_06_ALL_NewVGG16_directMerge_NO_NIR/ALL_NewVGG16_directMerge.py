import tensorflow as tf
from tensorflow.keras.layers import *
import numpy as np

import os

class ALL_NewVGG16_directMerge():
	def __init__(self, weightDir='./weight'):
		self.name = 'ALL_NewVGG16_directMerge'
		self.weightPath = '%s/%s.h5' % (weightDir, self.name)
		
		self.model = self.createModel()
		self.loadWeights()

	def saveWeights(self):
		self.model.save_weights(self.weightPath)

	def loadWeights(self):
		if os.path.isfile(self.weightPath):
			self.model.load_weights(self.weightPath)

	def createModel(self):
		PAN_input = Input(shape=(60, 60, 1), name='PAN_input')
		MS_input = Input(shape=(15, 15, 3), name='MS_input')
		MS_resize = Lambda(lambda t:tf.image.resize(t, [60, 60], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR), name="MS_resize")(MS_input)
		
		concat = Concatenate()([PAN_input, MS_resize])
		
		Model = tf.keras.applications.vgg16.VGG16(include_top=False, weights=None, input_tensor=concat)
		
		layer = Flatten(name='flatten')(Model.output)
		layer = Dense(256, activation='relu', name='dense_0')(layer)
		layer = Dropout(0.3, name='dropout')(layer)
		output_layer = Dense(2, activation='softmax', name='dense_1')(layer)
		
		model = tf.keras.Model(inputs=[PAN_input, MS_input], outputs=[output_layer], name=self.name)
		return model