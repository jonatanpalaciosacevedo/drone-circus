import cv2
import mediapipe as mp


# https://google.github.io/mediapipe/solutions/pose

class PoseDetector:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=True,
            model_complexity=2,
            enable_segmentation=True,
            min_detection_confidence=0.5)

    def __prepare(self, image):
        '''Prepare a list with the marks of 33 pose landmarks
        if no pose is detected the list in empty.
        Each mark is represented by (x,y), being x and y
        normalized to [0.0, 1.0] by the image width and height respectively.
        The function returns also the image including the drawing of detected
        pose landmarks and conecting lines'''

        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.pose.process(image)
        image.flags.writeable = True

        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        self.mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            self.mp_pose.POSE_CONNECTIONS,
            landmark_drawing_spec=self.mp_drawing_styles.get_default_pose_landmarks_style())
        poseLandmarks = []
        if results.pose_landmarks:
            for landmark in results.pose_landmarks.landmark:
                poseLandmarks.append([landmark.x, landmark.y])
        return poseLandmarks, image

    # these are 3 examples of difficult patterns

    def __p1(self, poseLandmarks):

        if ((poseLandmarks[24][0] > poseLandmarks[26][0])
                and (poseLandmarks[26][0] < poseLandmarks[28][0])
                and (poseLandmarks[28][1] < poseLandmarks[25][1])

                and (poseLandmarks[12][1] < poseLandmarks[14][1])
                and (poseLandmarks[14][1] < poseLandmarks[16][1])
                and (poseLandmarks[11][1] < poseLandmarks[13][1])
                and (poseLandmarks[13][1] < poseLandmarks[15][1])):
            return True
        else:
            return False

    def __p2(self, poseLandmarks):

        if ((poseLandmarks[23][0] < poseLandmarks[25][0])
                and (poseLandmarks[25][0] > poseLandmarks[27][0])
                and (poseLandmarks[27][1] < poseLandmarks[26][1])
                and (poseLandmarks[12][1] < poseLandmarks[14][1])
                and (poseLandmarks[14][1] < poseLandmarks[16][1])
                and (poseLandmarks[11][1] < poseLandmarks[13][1])
                and (poseLandmarks[13][1] < poseLandmarks[15][1])):
            return True
        else:
            return False

    # este
    def __p3(self, poseLandmarks):

        if ((poseLandmarks[11][0] < poseLandmarks[13][0])
                and (poseLandmarks[13][0] < poseLandmarks[15][0])
                and (poseLandmarks[11][1] > poseLandmarks[13][1])
                and (poseLandmarks[13][1] > poseLandmarks[15][1])

                and (poseLandmarks[25][0] > poseLandmarks[23][0])
                and (poseLandmarks[27][0] > poseLandmarks[25][0])
                and (poseLandmarks[25][0] > poseLandmarks[13][0])
                and (poseLandmarks[27][1] < poseLandmarks[28][1])):

            return True
        else:
            return False

    # oeste
    def __p4(self, poseLandmarks):

        if ((poseLandmarks[12][0] > poseLandmarks[14][0])
                and (poseLandmarks[14][0] > poseLandmarks[16][0])
                and (poseLandmarks[12][1] > poseLandmarks[14][1])
                and (poseLandmarks[14][1] > poseLandmarks[16][1])

                and (poseLandmarks[26][0] < poseLandmarks[24][0])
                and (poseLandmarks[28][0] < poseLandmarks[26][0])
                and (poseLandmarks[26][0] < poseLandmarks[14][0])
                and (poseLandmarks[28][1] < poseLandmarks[27][1])):

            return True
        else:
            return False

    # drop
    def __p5(self, poseLandmarks):

        if ((poseLandmarks[23][0] < poseLandmarks[25][0])
                and (poseLandmarks[25][0] > poseLandmarks[27][0])
                and (poseLandmarks[26][0] > poseLandmarks[24][0])
                and (poseLandmarks[26][0] > poseLandmarks[28][0])):

            return True
        else:
            return False

    # return
    def __p6(self, poseLandmarks):

        if ((poseLandmarks[24][0] > poseLandmarks[26][0])
                and (poseLandmarks[26][0] < poseLandmarks[28][0])
                and (poseLandmarks[28][1] < poseLandmarks[25][1])

                and (poseLandmarks[12][1] > poseLandmarks[14][1])
                and (poseLandmarks[14][1] > poseLandmarks[16][1])
                and (poseLandmarks[14][0] < poseLandmarks[12][0])
                and (poseLandmarks[14][0] < poseLandmarks[16][0])

                and (poseLandmarks[11][1] > poseLandmarks[13][1])
                and (poseLandmarks[13][1] > poseLandmarks[15][1])
                and (poseLandmarks[13][0] > poseLandmarks[11][0])
                and (poseLandmarks[13][0] > poseLandmarks[15][0])

        ):
            return True
        else:
            return False

    # stop
    def __p0(self, poseLandmarks):

        if ((poseLandmarks[26][0] < poseLandmarks[24][0])
                and (poseLandmarks[26][0] < poseLandmarks[30][0])
                and (poseLandmarks[25][0] > poseLandmarks[23][0])
                and (poseLandmarks[25][0] > poseLandmarks[29][0])):

            return True
        else:
            return False

    def __poseD3(self, poseLandmarks):
        if ((poseLandmarks[16][0] > poseLandmarks[12][0])
                and (poseLandmarks[12][0] > poseLandmarks[14][0])
                and (poseLandmarks[16][1] < poseLandmarks[14][1])
                and (poseLandmarks[14][1] < poseLandmarks[12][1])
                and (poseLandmarks[15][0] < poseLandmarks[11][0])
                and (poseLandmarks[11][0] < poseLandmarks[13][0])
                and (poseLandmarks[15][1] < poseLandmarks[13][1])
                and (poseLandmarks[13][1] < poseLandmarks[11][1])
                and (poseLandmarks[15][0] > poseLandmarks[16][0])

                and (poseLandmarks[23][0] > poseLandmarks[25][0])
                and (poseLandmarks[25][0] > poseLandmarks[27][0])
                and (poseLandmarks[26][0] < poseLandmarks[24][0])
                and (poseLandmarks[24][0] < poseLandmarks[28][0])
                and (poseLandmarks[28][1] < poseLandmarks[25][1])):
            return True
        else:
            return False

    def __poseD2(self, poseLandmarks):
        if ((poseLandmarks[16][0] > poseLandmarks[12][0])
                and (poseLandmarks[12][0] > poseLandmarks[14][0])
                and (poseLandmarks[16][1] < poseLandmarks[14][1])
                and (poseLandmarks[14][1] < poseLandmarks[12][1])
                and (poseLandmarks[15][0] < poseLandmarks[11][0])
                and (poseLandmarks[11][0] < poseLandmarks[13][0])
                and (poseLandmarks[15][1] < poseLandmarks[13][1])
                and (poseLandmarks[13][1] < poseLandmarks[11][1])
                and (poseLandmarks[15][0] < poseLandmarks[16][0])

                and (poseLandmarks[23][0] < poseLandmarks[25][0])
                and (poseLandmarks[27][0] < poseLandmarks[25][0])
                and (poseLandmarks[26][0] < poseLandmarks[28][0])
                and (poseLandmarks[26][0] < poseLandmarks[24][0])):
            return True
        else:
            return False

    def __poseD1(self, poseLandmarks):
        if ((poseLandmarks[16][0] < poseLandmarks[14][0])

                and (poseLandmarks[14][0] < poseLandmarks[12][0])
                and (poseLandmarks[16][1] < poseLandmarks[14][1])
                and (poseLandmarks[14][1] < poseLandmarks[12][1])

                and (poseLandmarks[11][0] < poseLandmarks[13][0])
                and (poseLandmarks[13][0] < poseLandmarks[15][0])
                and (poseLandmarks[15][1] < poseLandmarks[13][1])
                and (poseLandmarks[13][1] < poseLandmarks[11][1])

                and (poseLandmarks[12][0] < poseLandmarks[11][0])

                and (poseLandmarks[24][1] < poseLandmarks[26][1])
                and (poseLandmarks[26][1] < poseLandmarks[28][1])
                and (poseLandmarks[28][0] < poseLandmarks[26][0])
                and (poseLandmarks[26][0] < poseLandmarks[24][0])

                and (poseLandmarks[23][0] < poseLandmarks[25][0])
                and (poseLandmarks[25][0] > poseLandmarks[27][0])
                and (poseLandmarks[23][1] < poseLandmarks[25][1])
                and (poseLandmarks[25][1] < poseLandmarks[27][1])

                and (poseLandmarks[24][0] < poseLandmarks[23][0])):
            return True
        else:
            return False

    def detect(self, image):
        level = "easy"
        poseLandmarks, img = self.__prepare(image)
        res = ''
        if len(poseLandmarks) > 17:
            if level == 'difficult':
                if self.__p0(poseLandmarks):
                    res = 0
                elif self.__p1(poseLandmarks):
                    res = 1
                elif self.__p2(poseLandmarks):
                    res = 2
                elif self.__p3(poseLandmarks):
                    res = 3
                elif self.__p4(poseLandmarks):
                    res = 4
                elif self.__p5(poseLandmarks):
                    res = 5
                elif self.__p6(poseLandmarks):
                    res = 6
            else:
                # to see what are the easy patterns see picture assets/poses_faciles.png
                if ((poseLandmarks[12][1] < poseLandmarks[14][1])
                        and (poseLandmarks[14][1] < poseLandmarks[16][1])
                        and (poseLandmarks[11][1] < poseLandmarks[13][1])
                        and (poseLandmarks[13][1] < poseLandmarks[15][1])
                        and (poseLandmarks[18][0] < poseLandmarks[17][0])):
                    res = 0  # STOP
                elif ((poseLandmarks[12][1] < poseLandmarks[14][1])
                      and (poseLandmarks[14][1] < poseLandmarks[16][1])
                      and (poseLandmarks[11][1] < poseLandmarks[13][1])
                      and (poseLandmarks[13][1] < poseLandmarks[15][1])
                      and (poseLandmarks[18][0] > poseLandmarks[17][0])):
                    res = 5  # DROP
                elif ((poseLandmarks[14][1] > poseLandmarks[12][1])
                      and (poseLandmarks[14][1] > poseLandmarks[16][1])
                      and (poseLandmarks[13][1] > poseLandmarks[11][1])
                      and (poseLandmarks[13][1] > poseLandmarks[15][1])
                      and (poseLandmarks[18][0] < poseLandmarks[17][0])):
                    res = 6  # RETURN

                elif (poseLandmarks[12][1] < poseLandmarks[14][1]) and (poseLandmarks[11][1] > poseLandmarks[13][1]):
                    res = 3  # EAST
                elif (poseLandmarks[12][1] > poseLandmarks[14][1]) and (poseLandmarks[11][1] < poseLandmarks[13][1]):
                    res = 4  # WEST
                elif (poseLandmarks[12][1] > poseLandmarks[14][1]) and (poseLandmarks[11][1] > poseLandmarks[13][1]):
                    if (poseLandmarks[18][0] > poseLandmarks[17][0]):
                        res = 2  # SOUTH
                    if (poseLandmarks[18][0] < poseLandmarks[17][0]):
                        res = 1  # NORTH

        return res, img
