import cv2
import mediapipe as mp


# https://google.github.io/mediapipe/solutions/hands.html

class FingerDetector:
    def __init__(self):
        self.mp_drawing = mp.solutions.drawing_utils
        self.mp_drawing_styles = mp.solutions.drawing_styles
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(
            model_complexity=0,
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5)

    def __prepare(self, image):
        '''Prepare two lists of marks, one for each hand (left and right)
        if one of the hands (or both) is not detected the corresponding list in empty.
        Each list has 21 marks corresponding to 21  hand-knuckles.
        Each mark is represented by (x,y), being x and y
        normalized to [0.0, 1.0] by the image width and height respectively.
        The function returns also the image including the drawing of detected
        hand-knuckles and conecting lines'''
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = self.hands.process(image)

        # Draw the hand annotations on the image.
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        leftHandLandmarks = []
        rightHandLandmarks = []

        if results.multi_hand_landmarks:

            for hand_landmarks in results.multi_hand_landmarks:

                # Get hand index to check label (left or right)
                handIndex = results.multi_hand_landmarks.index(hand_landmarks)
                handLabel = results.multi_handedness[handIndex].classification[0].label
                # Set variable to keep landmarks positions (x and y)
                if handLabel == "Left":
                    # Fill list with x and y positions of each landmark
                    for landmarks in hand_landmarks.landmark:
                        leftHandLandmarks.append([landmarks.x, landmarks.y])
                if handLabel == "Right":
                    # Fill list with x and y positions of each landmark
                    for landmarks in hand_landmarks.landmark:
                        rightHandLandmarks.append([landmarks.x, landmarks.y])
                # draw hand-knuckles and conecting lines in image
                self.mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    self.mp_hands.HAND_CONNECTIONS,
                    self.mp_drawing_styles.get_default_hand_landmarks_style(),
                    self.mp_drawing_styles.get_default_hand_connections_style())

        return leftHandLandmarks, rightHandLandmarks, image

    # this is an example of difficult pattern detection
    # the difficult pattern is the OK gesture
    def __poseD1(self, leftHandLandmarks, rightHandLandmarks):
        leftHandLandmarks = rightHandLandmarks
        if len(leftHandLandmarks) > 0:

            if ((leftHandLandmarks[18][1] > leftHandLandmarks[19][1])
                    and (leftHandLandmarks[19][1] > leftHandLandmarks[20][1])
                    and (leftHandLandmarks[14][1] > leftHandLandmarks[15][1])
                    and (leftHandLandmarks[15][1] > leftHandLandmarks[16][1])
                    and (leftHandLandmarks[10][1] > leftHandLandmarks[11][1])
                    and (leftHandLandmarks[8][0] < leftHandLandmarks[5][0])
                    and (leftHandLandmarks[6][1] < leftHandLandmarks[5][1])
                    and (leftHandLandmarks[6][1] < leftHandLandmarks[7][1])
                    and (leftHandLandmarks[7][1] < leftHandLandmarks[8][1])
                    and (leftHandLandmarks[4][0] < leftHandLandmarks[3][0])
                    and (leftHandLandmarks[4][1] < leftHandLandmarks[3][1])
                    and (leftHandLandmarks[3][1] < leftHandLandmarks[2][1])
                    and abs(leftHandLandmarks[8][1] - leftHandLandmarks[4][1]) < 0.05
                    and abs(leftHandLandmarks[8][0] - leftHandLandmarks[4][0]) < 0.05):

                return True
            else:
                return False
        else:
            return False

    def detect(self, image):
        level = "easy"
        leftHandLandmarks, rightHandLandmarks, img = self.__prepare(image)
        res = ''
        if level == 'difficult':
            if self.__poseD1(leftHandLandmarks, rightHandLandmarks):
                res = 'Pose D11111'
            '''elif self.__poseD2( leftHandLandmarks, rightHandLandmarks):
                res = 'Pose D22222'
            elif self.__poseD3( leftHandLandmarks, rightHandLandmarks):
                res = 'Pose D333333'''
            return res, img
        else:
            # returns the number of risen fingers
            # ATTENTION: WE DO NOT TAKE INTO ACCOUNT THE THUMB FINGER
            # Initially set finger count to 0 for each cap
            fingerCount = 0
            if len(leftHandLandmarks) > 0:
                if leftHandLandmarks[8][1] < leftHandLandmarks[6][1]:  # Index finger
                    fingerCount = fingerCount + 1
                if leftHandLandmarks[12][1] < leftHandLandmarks[10][1]:  # Middle finger
                    fingerCount = fingerCount + 1
                if leftHandLandmarks[16][1] < leftHandLandmarks[14][1]:  # Ring finger
                    fingerCount = fingerCount + 1
                if leftHandLandmarks[20][1] < leftHandLandmarks[18][1]:  # Pinky
                    fingerCount = fingerCount + 1

            if len(rightHandLandmarks) > 0:

                if rightHandLandmarks[8][1] < rightHandLandmarks[6][1]:  # Index finger
                    fingerCount = fingerCount + 1
                if rightHandLandmarks[12][1] < rightHandLandmarks[10][1]:  # Middle finger
                    fingerCount = fingerCount + 1
                if rightHandLandmarks[16][1] < rightHandLandmarks[14][1]:  # Ring finger
                    fingerCount = fingerCount + 1
                if rightHandLandmarks[20][1] < rightHandLandmarks[18][1]:  # Pinky
                    fingerCount = fingerCount + 1

            return fingerCount, img
