import numpy as np
from skimage import io
from neural_network.preprocessing import FaceDetector, FaceAligner


def load_image(filename, im_size=217, border=5):
    """
        Extract face from image

        @type  filename: str
        @param filename: Path to image

        @type  im_size: int
        @param im_size: Image size

        @type  border: int
        @param border: Border size

        @rtype : np.array
        @return :
    """

    fd = FaceDetector()
    fa = FaceAligner("neural_network\\data\\shape_predictor_68_face_landmarks.dat",
                     "neural_network\\data\\face_template.npy")

    total_size = im_size + 2 * border

    img = io.imread(filename)
    faces = fd.detect_faces(img, get_top=1)  # get_top how many faces can be found

    if len(faces) == 0:
        return None  # one face

    if len(faces) > 1:
        pass  # return None  # more then one face

    face = fa.align_face(img, faces[0], dim=im_size, border=border).reshape(1, total_size, total_size, 3)
    face /= 255.0

    mean = np.load("neural_network\\data\\mean.npy")
    std = np.load("neural_network\\data\\std.npy")

    face -= mean
    face /= std

    del img

    return face.astype(np.float32)
