from PIL import Image, ImageFilter
test_image = Image.open("color_floor_plan.jpg")

def convert_to_grey_scale(image):
    """Converts an opened Image object to black/white"""
    return image.convert("1")

def save_image(image, name):
    image.save(name)
    return

def dilation(image):
    filter = ImageFilter.MinFilter(3) # Should be MaxFilter if white on black
    filtered = image.filter(filter)
    return filtered

def erosion(image):
    filter = ImageFilter.MaxFilter(3) # Should be MinFilter if white on black
    filtered = image.filter(filter)
    return filtered

test = convert_to_grey_scale(test_image)
test1 = dilation(erosion(erosion(test)))

save_image(test1, "test.jpg")

import cv2
import numpy as np

img = cv2.imread("test.jpg")
edges = cv2.Canny(img, 75, 150)
lines = cv2.HoughLinesP(edges, 1, np.pi/180, 50,maxLineGap=250)
for line in lines:
    x1, y1, x2, y2 = line[0]
    cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
# Show result
cv2.imwrite("edges.png", edges)

cv2.imwrite("Result.jpg", img)