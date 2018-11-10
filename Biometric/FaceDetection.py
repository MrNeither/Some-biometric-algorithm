import os.path
import numpy as np
from Biometric.preprocessing import FaceDetector, FaceAligner
from Biometric.models import build_cnn, build_tpe


GREATER_THAN = 32
BATCH_SIZE = 128
IM_SIZE = 217
IM_BORDER = 5
TOTAL_SIZE = IM_SIZE + 2 * IM_BORDER


class FaceDetection:

    def __init__(self, model_dir):

        self._model_dir = model_dir

        self._model_files = {
            'shape_predictor': os.path.join(model_dir, 'shape_predictor_68_face_landmarks.dat'),
            'face_template': os.path.join(model_dir, 'face_template.npy'),
            'mean': os.path.join(model_dir, 'mean.npy'),
            'stddev': os.path.join(model_dir, 'stddev.npy'),
            'cnn_weights': os.path.join(model_dir, 'weights_cnn.h5'),
            'tpe_weights': os.path.join(model_dir, 'weights_tpe.h5'),
        }

        for model_file in self._model_files.values():
            if not os.path.exists(model_file):
                raise FileNotFoundError(model_file)

        self._mean = np.load(self._model_files['mean'])
        self._stddev = np.load(self._model_files['stddev'])

        self._fd = FaceDetector()
        self._fa = FaceAligner(self._model_files['shape_predictor'],
                               self._model_files['face_template'])

        cnn = build_cnn(227, 266)
        cnn.load_weights(self._model_files['cnn_weights'])
        cnn.pop()
        self._cnn = cnn

        _, tpe = build_tpe(256, 256)
        tpe.load_weights(self._model_files['tpe_weights'])
        self._tpe = tpe

    def predict(self, img):

        face = self._fd.detect_faces(img, get_top=1)  # get_top how many faces can be found

        if len(face) == 0:
            return None  # one face
        if len(face) > 1:
            pass  # return None  # Todo more then one face

        face = self._fa.align_face(img, face[0], dim=IM_SIZE, border=IM_BORDER).reshape(1, TOTAL_SIZE, TOTAL_SIZE, 3)

        del img

        face /= 255.0
        face = face.astype(np.float32)
        face = (face - self._mean) / self._stddev

        face_feat = self._cnn.predict(face, batch_size=BATCH_SIZE)
        predict = self._tpe.predict(face_feat, batch_size=BATCH_SIZE)

        return predict

    @staticmethod
    def compare(dist: int, xs, ys):
        xs = np.array(xs)
        ys = np.array(ys)
        scores = xs @ ys.T
        return scores, scores > dist
