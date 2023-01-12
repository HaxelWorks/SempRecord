import cv2
import numpy as np

fourcc = cv2.VideoWriter_fourcc(*"XVID")
out = cv2.VideoWriter("output.avi", fourcc, 15.0, (1920, 1080))

while True:
    img = np.array(cv2.imread("screen.png", -1))
    out.write(img)
    cv2.imshow("screen", img)
    if cv2.waitKey(1) == ord("q"):
        break

out.release()
cv2.destroyAllWindows()
