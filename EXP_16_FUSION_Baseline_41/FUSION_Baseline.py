import tensorflow as tf
from tensorflow.keras.layers import *
import numpy as np

import os

class FUSION_Baseline():
	def __init__(self, weightDir='./weight'):
		self.name = 'FUSION_Baseline'
		self.weightPath = '%s/%s.h5' % (weightDir, self.name)
		
		self.model = self.createModel()
		self.loadWeights()

	def saveWeights(self):
		self.model.save_weights(self.weightPath)

	def loadWeights(self):
		if os.path.isfile(self.weightPath):
			self.model.load_weights(self.weightPath)

	def createModel(self):
		input = Input(shape=(60, 60, 4), name='input')
		
		stage_1 = Conv2D(filters=50, kernel_size=5, padding='same', activation='relu')(input)
		stage_1p = MaxPool2D(pool_size=2)(stage_1)
		stage_2 = Conv2D(filters=70, kernel_size=5, padding='same', activation='relu')(stage_1p)
		stage_2p = MaxPool2D(pool_size=2)(stage_2)
		stage_3 = Conv2D(filters=100, kernel_size=3, padding='same', activation='relu')(stage_2p)
		stage_3p = MaxPool2D(pool_size=2)(stage_3)
		stage_4 = Conv2D(filters=150, kernel_size=3, padding='same', activation='relu')(stage_3p)
		stage_4p = MaxPool2D(pool_size=2)(stage_4)
		stage_5 = Conv2D(filters=100, kernel_size=3, padding='same', activation='relu')(stage_4p)
		stage_6 = Conv2D(filters=70, kernel_size=3, padding='same', activation='relu')(stage_5)
		stage_7 = Conv2D(filters=70, kernel_size=3, padding='same', activation='relu')(stage_6)

		upsample_2 = UpSampling2D(size=2)(stage_2)
		upsample_3 = UpSampling2D(size=4)(stage_3)
		upsample_7 = UpSampling2D(size=20)(stage_7)
		feature_stack = Concatenate()([stage_1, upsample_2, upsample_3, upsample_7])
		integration = Conv2D(filters=70, kernel_size=3, padding='same', activation='relu')(feature_stack)
		
		layer = GlobalAveragePooling2D(name='GAP')(integration)
		layer = Dense(256, activation='relu', name='dense_0')(layer)
		layer = Dropout(0.3, name='dropout')(layer)
		output_layer = Dense(2, activation='softmax', name='dense_1')(layer)
		
		model = tf.keras.Model(inputs=[input, ], outputs=[output_layer], name=self.name)
		return model