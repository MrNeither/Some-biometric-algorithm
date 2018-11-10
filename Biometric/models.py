from keras.layers import Flatten, Dense, Dropout, Lambda
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.layers.advanced_activations import PReLU
from keras.models import Sequential, Model
from keras import Input
import keras.backend as K
import numpy as np


def build_cnn(dim, n_classes):
    model = Sequential()

    model.add(Convolution2D(96, (11, 11),
                            strides=(4, 4),
                            input_shape=(dim, dim, 3),
                            kernel_initializer='glorot_uniform',
                            padding='same'))
    model.add(PReLU())
    model.add(MaxPooling2D((3, 3), strides=(2, 2)))

    model.add(Convolution2D(256, (5, 5),
                            strides=(1, 1),
                            kernel_initializer='glorot_uniform',
                            padding='same'))
    model.add(PReLU())
    model.add(MaxPooling2D((3, 3), strides=(2, 2)))

    model.add(Convolution2D(384, (3, 3),
                            strides=(1, 1),
                            kernel_initializer='glorot_uniform',
                            padding='same'))
    model.add(PReLU())

    model.add(Convolution2D(384, (3, 3),
                            strides=(1, 1),
                            kernel_initializer='glorot_uniform',
                            padding='same'))
    model.add(PReLU())

    model.add(Convolution2D(256, (3, 3),
                            strides=(1, 1),
                            kernel_initializer='glorot_uniform',
                            padding='same'))
    model.add(PReLU())
    model.add(MaxPooling2D((3, 3), strides=(2, 2)))

    model.add(Flatten())
    model.add(Dropout(0.5))

    model.add(Dense(2048, kernel_initializer='glorot_uniform'))
    model.add(PReLU())
    model.add(Dropout(0.5))

    model.add(Dense(256, kernel_initializer='glorot_uniform'))
    model.add(PReLU())

    model.add(Dense(n_classes, kernel_initializer='glorot_uniform', activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])

    return model


def triplet_loss(y_true, y_pred):
    return -K.mean(K.log(K.sigmoid(y_pred)))


def triplet_merge(inputs):
    a, p, n = inputs

    return K.sum(a * (p - n), axis=1)


def triplet_merge_shape(input_shapes):
    return input_shapes[0][0], 1


def build_tpe(n_in, n_out, w_pca=None):

    a = Input(shape=(n_in,))
    p = Input(shape=(n_in,))
    n = Input(shape=(n_in,))

    if w_pca is None:
        w_pca = np.zeros((n_in, n_out))

    base_model = Sequential()
    base_model.add(Dense(n_out, input_dim=n_in, use_bias=False, weights=[w_pca], activation='linear'))
    base_model.add(Lambda(lambda x: K.l2_normalize(x, axis=1)))

    a_emb = base_model(a)
    p_emb = base_model(p)
    n_emb = base_model(n)

    e = Lambda(function=triplet_merge, output_shape=triplet_merge_shape)([a_emb, p_emb, n_emb])

    model = Model(inputs=[a, p, n], outputs=e)
    predict = Model(inputs=a, outputs=a_emb)

    model.compile(loss=triplet_loss, optimizer='rmsprop')

    return model, predict


# def build_classifier(optimizer='rmsprop', shape=256):
#     # image_1_input = Input(shape=(shape,), name="image_1")
#     # image_1 = layers.Dense(128, activation='relu')(image_1_input)
#     # image_1 = layers.Dense(64, activation='relu')(image_1)
#     #
#     # image_2_input = Input(shape=(shape,), name="image_2")
#     # image_2 = layers.Dense(128, activation='relu')(image_2_input)
#     # image_2 = layers.Dense(64, activation='relu')(image_2)
#     #
#     # concatenated = layers.concatenate([image_1, image_2], axis=-1)
#     #
#     # out = layers.Dense(128, activation='relu')(concatenated)
#     # out = layers.Dense(32, activation='relu')(out)
#     # out = layers.Dense(2, activation='softmax')(out)
#     #
#     # model = Model([image_1_input, image_2_input], out)
#     #
#     # model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=["accuracy"])
#
#     image_1_input = Input(shape=(shape,), name="image_1")
#     image_2_input = Input(shape=(shape,), name="image_2")
#
#     base_model = Sequential()
#     base_model.add(Dense(64, input_dim=shape, use_bias=False, activation='linear'))
#     base_model.add(Lambda(lambda x: K.l2_normalize(x, axis=1)))
#
#     image_1 = base_model(image_1_input)
#     image_2 = base_model(image_2_input)
#
#     concatenated = layers.concatenate([image_1, image_2], axis=-1)
#     out = Dropout(0.5)(concatenated)
#     out = Dense(16, activation='relu')(out)
#     out = Dropout(0.5)(out)
#     out = Dense(1, activation='sigmoid')(out)
#
#     model = Model([image_1_input, image_2_input], out)
#
#     model.compile(loss="binary_crossentropy", optimizer=optimizer, metrics=["accuracy"])
#
#     return model
#
#
# def get_detector(cnn_weights_path, classifier_weights_path, mms_path):
#
#     cnn = build_cnn(227, 266)
#     cnn.load_weights(cnn_weights_path)
#     cnn.pop()
#
#     classifier = build_classifier()
#     classifier.load_weights(classifier_weights_path)
#
#     mms = None
#     with open(mms_path, 'rb') as f:
#         mms = pickle.load(f)
#
#     return cnn, classifier, mms
