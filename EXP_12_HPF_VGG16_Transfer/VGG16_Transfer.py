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

	def get_conv_ident(self, size=3):
		result = np.zeros(shape=(size, size))
		center = int(size/2)
		result[center, center] = 1
		return result.copy()

	def get_conv_zero(self, size=3):
		result = np.zeros(shape=(size, size))
		return result.copy()

	def get_conv_mean(self, size=3):
		result = np.ones(shape=(size, size)) / (size*size)
		return result.copy()

	def get_fusion_conv_weight(self, k=3, i=5, f=3):
		weights = np.zeros(shape=(k, k, i, f))
		weights[:, :, 0, :] = np.stack([self.get_conv_ident(k)]*f, axis=-1)
		weights[:, :, 1, :] = np.stack([-self.get_conv_mean(k)]*f, axis=-1)
		weights[:, :, 2, :] = np.stack([self.get_conv_ident(k), self.get_conv_zero(k), self.get_conv_zero(k)], axis=-1)
		weights[:, :, 3, :] = np.stack([self.get_conv_zero(k), self.get_conv_ident(k), self.get_conv_zero(k)], axis=-1)
		weights[:, :, 4, :] = np.stack([self.get_conv_zero(k), self.get_conv_zero(k), self.get_conv_ident(k)], axis=-1)
		return weights

	def VggFinetune(self):
		self.VGG.trainable=True

	def HpfFinetune(self):
		self.fusion_conv.trainable = True

	def createModel(self):
		PAN_input = Input(shape=(60, 60, 1), name='PAN_input')
		MS_input = Input(shape=(15, 15, 3), name='MS_input')
		MS_resize = Lambda(lambda t:tf.image.resize(t, [60, 60], method=tf.image.ResizeMethod.NEAREST_NEIGHBOR), name="MS_resize")(MS_input)
		
		concat = Concatenate()([PAN_input, PAN_input, MS_resize])
		# fusion conv
		k = 3
		fusion_conv = Conv2D(filters=3, kernel_size=k, padding='same')
		fusion = fusion_conv(concat)
		weights, bias = fusion_conv.get_weights()
		weights = self.get_fusion_conv_weight(k)
		fusion_conv.set_weights([weights, bias])
		fusion_conv.trainable = False
		self.fusion_conv = fusion_conv
		
		Model = tf.keras.applications.vgg16.VGG16(include_top=False, weights=None, input_tensor=fusion)
		Model.trainable = False
		self.VGG = Model
		
		layer = Flatten(name='flatten')(Model.output)
		layer = Dense(256, activation='relu', name='dense_0')(layer)
		layer = Dropout(0.3, name='dropout')(layer)
		output_layer = Dense(2, activation='softmax', name='dense_1')(layer)
		
		model = tf.keras.Model(inputs=[PAN_input, MS_input], outputs=[output_layer], name=self.name)
		return model