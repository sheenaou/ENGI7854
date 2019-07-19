from PIL import Image, ImageFilter
import cv2
import numpy as np

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

def line_closing(image_file):
    image = cv2.imread(image_file)
    edges = cv2.Canny(image, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=160)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), 5)

    kernel = np.ones((5, 5), np.uint8)
    dilate = cv2.dilate(image, kernel, iterations=2)
    return dilate

def opencv_write(image, name):
    cv2.imwrite(name, image)

def main():
    test_image = Image.open("color_floor_plan.jpg")
    grey = convert_to_grey_scale(test_image)
    threshold = dilation(erosion(erosion(grey)))
    save_image(threshold, "temp.png")
    new_image = line_closing("temp.png")
    opencv_write(new_image, "new_image.jpg")

main()




