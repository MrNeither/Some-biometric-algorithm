from neural_network.FaceDetection import FaceDetection
import os

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

Test_DIR = "C:\\Users\\SandersPC\\Downloads\\For neural network\\faces\\"
IMAGES_DIR = "C:\\Users\\SandersPC\\PycharmProjects\\Some-biometric-algorithm\\images_for_check\\"

###
img_path_0 = IMAGES_DIR + '0_0.jpg'
img_path_1 = IMAGES_DIR + '0_1.jpg'
dist = 0.90


classifier = FaceDetection(Test_DIR)

im_0 = classifier.predict(img_path_0)
im_1 = classifier.predict(img_path_1)

print(classifier.compare(dist, im_0, im_1))

