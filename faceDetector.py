import mediapipe as mp
import cv2
import numpy as np
import itertools


class FaceDetector:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_face_mesh = mp.solutions.face_mesh
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.drawing_spec = self.mp_drawing.DrawingSpec(thickness=1, circle_radius=1)
        self.face_mesh = self.mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5)

    def __prepare(self, image):
        """Prepares list of face marks
        If face is not detected, the list is empty
        The list has 468 face marks
        each landmark is composed of x, y and z. x and y are normalized to [0.0, 1.0]
        by the image width and height respectively.
        Z represents the landmark depth with the depth at center of the head being the origin,
        and the smaller the value the closer the landmark is to the camera.
        The magnitude of z uses roughly the same scale as x.
        The function returns also the image including the drawing of detected
        face marks and connecting lines"""

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        self.results = self.face_mesh.process(image)
        image.flags.writeable= True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        if self.results.multi_face_landmarks:
            for face_landmarks in self.results.multi_face_landmarks:
                face = face_landmarks.landmark
                faceLandmarks = list(
                    np.array(
                    [[landmark.x, landmark.y, landmark.z, landmark.visibility] for landmark in face]).flatten())


            self.mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_tesselation_style())
            self.mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_contours_style())
            self.mp_drawing.draw_landmarks(
                image=image,
                landmark_list=face_landmarks,
                connections=self.mp_face_mesh.FACEMESH_IRISES,
                landmark_drawing_spec=None,
                connection_drawing_spec=self.mp_drawing_styles
                .get_default_face_mesh_iris_connections_style())

            return faceLandmarks, image
        else:
            return [],image

    def getSize(self,image, face_landmarks, INDEXES):
        '''
        This function calculate the height and width of a face part utilizing its landmarks.
        Args:
            image:          The image of person(s) whose face part size is to be calculated.
            face_landmarks: The detected face landmarks of the person whose face part size is to
                            be calculated.
            INDEXES:        The indexes of the face part landmarks, whose size is to be calculated.
        Returns:
            X,Y:        the coordinates of the left-top corner of the rectangle containing the part of the face
            width:     The calculated width of the rectangle containing the face part of the face whose landmarks were passed.
            height:    The calculated height of the rectangle containing the face part of the face whose landmarks were passed.
            landmarks: An array of landmarks of the face part whose size is calculated.
        '''

        # Retrieve the height and width of the image.
        image_height, image_width, _ = image.shape

        # Convert the indexes of the landmarks of the face part into a list.
        INDEXES_LIST = list(itertools.chain(*INDEXES))

        # Initialize a list to store the landmarks of the face part.
        landmarks = []

        # Iterate over the indexes of the landmarks of the face part.
        for INDEX in INDEXES_LIST:
            # Append the landmark into the list.
            landmarks.append([int(face_landmarks.landmark[INDEX].x * image_width),
                              int(face_landmarks.landmark[INDEX].y * image_height)])


        # Calculate the width and height of the face part.
        X, Y, width, height = cv2.boundingRect(np.array(landmarks))

        # Convert the list of landmarks of the face part into a numpy array.
        landmarks = np.array(landmarks)

        return X, Y, width, height, landmarks

    def inclinacion(self,image, face_mesh_results):
        # return 'left', 'right' or 'normal' depending of the inclination of the face
        # this is deduced from the coordinates of the eyes
        # Get the indexes of the eyes
        LEFT = self.mp_face_mesh.FACEMESH_LEFT_EYE
        RIGHT = self.mp_face_mesh.FACEMESH_RIGHT_EYE
        for face_no, face_landmarks in enumerate(face_mesh_results.multi_face_landmarks):
            # Get the height of the face part.
            LX, LY, _, _, _ = self.getSize(image, face_landmarks, LEFT)
            RX, RY, _, _, _ = self.getSize(image, face_landmarks, RIGHT)

            if (LY > RY + 20):
                return 'left'
            elif (RY > LY + 20):
                return 'right'
            else:
                return 'normal'

    def isOpen(self,image, face_mesh_results):
        '''
        This function checks whether the eyes and mouth are close, open or very open
        utilizing its facial landmarks.
        Args:
            image:             The image of person(s) whose an eye or mouth is to be checked.
            face_mesh_results: The output of the facial landmarks detection on the image.

        Returns 'Very Open', 'Open' or 'Closed' for evey eye and the mouth

        '''

        # Retrieve the height and width of the image.
        #image_height, image_width, _ = image.shape


        # Get the indexes of the eyes and mouth.
        LIP_INDEXES = self.mp_face_mesh.FACEMESH_LIPS
        LEFT_EYE_INDEXES = self.mp_face_mesh.FACEMESH_LEFT_EYE
        RIGHT_EYE_INDEXES = self.mp_face_mesh.FACEMESH_RIGHT_EYE

        # Iterate over the found faces.
        for face_no, face_landmarks in enumerate(face_mesh_results.multi_face_landmarks):
            # Get the height of the whole face.
            _, _, _, face_height, _ = self.getSize(image, face_landmarks, self.mp_face_mesh.FACEMESH_FACE_OVAL)

            # Get the height of the face mouth.
            _, _, _, lip_height, _ = self.getSize(image, face_landmarks, LIP_INDEXES)

            # Check if the face part is very open.
            if (lip_height / face_height) * 100 > 25:
                mouth = 'Very Open'
            # or open
            elif (lip_height / face_height) * 100 > 15:
                mouth = 'Open'
            else:
            # or closed
                mouth = 'Closed'

            # the same procedure for each eye
            _, _, _, left_eye_height, _ = self.getSize(image, face_landmarks, LEFT_EYE_INDEXES)


            if (left_eye_height / face_height) * 100 > 5.5:
                leftEye = 'Very Open'
            elif (left_eye_height / face_height) * 100 > 3:
                leftEye = 'Open'
            else:
                leftEye = 'Closed'

            _, _, _, right_eye_height, _ = self.getSize(image, face_landmarks, RIGHT_EYE_INDEXES)

            if (right_eye_height / face_height) * 100 > 5.5:
                rightEye = 'Very Open'
            elif (right_eye_height / face_height) * 100 > 3:
                rightEye = 'Open'
            else:
                rightEye = 'Closed'

        return mouth, leftEye, rightEye




    def detect(self, image):
        """Returns the pose made by the face"""
        faceLandmarks, img = self.__prepare(image)


        code = -1
        # Make Detections
        if faceLandmarks:
            mouth, leftEye, rightEye = self.isOpen(image, self.results)
            inclination = self.inclinacion(image, self.results)
            if (inclination == 'left'):
                code = 3  # east
            elif (inclination == 'right'):
                code = 4  # west
            elif (leftEye == 'Closed'  and mouth == 'Open' and inclination == 'normal'):
                code = 1 #NORTH
            elif (leftEye == 'Very Open' and rightEye == 'Very Open' and mouth == 'Closed' and inclination == 'normal'):
                code = 2  #south
            elif ( leftEye == 'Open' and rightEye == 'Closed' and  mouth == 'Very Open' and inclination == 'normal'):
                code = 5  #drop

            elif ( leftEye == 'Closed' and rightEye == 'Open' and  mouth == 'Very Open' and inclination == 'normal'):
                code = 0  #stop
            elif ( leftEye== 'Very Open'  and  rightEye== 'Very Open' and  mouth == 'Very Open' and inclination == 'normal'):
                code = 6  #return
        return code, img

