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
    # lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=300)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), 5)

    kernel = np.ones((5, 5), np.uint8)
    dilate = cv2.dilate(image, kernel, iterations=2)
    return dilate
    # return image

def opencv_write(image, name):
    cv2.imwrite(name, image)

def room_detection(test_image):
    image = cv2.imread(test_image)
    height, width, channels = image.shape
    im_bw = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    thresh, im_bw = cv2.threshold(im_bw, 127, 255, 0)
    contours, hierarchy = cv2.findContours(im_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Remove image border from contours
    room_contours = []
    for i in range(0, len(contours)):
        x, y, w, h = cv2.boundingRect(contours[i])
        if w != width and h != height:
            room_contours.append(contours[i])

    # Find the Contours of the entire floor
    floor_contour = None
    for i in range(0, len(room_contours)):
        x, y, w, h = cv2.boundingRect(room_contours[i])
        max_x, max_y, max_w, max_h =  cv2.boundingRect(floor_contour)
        if w != width and h != height:
            if w * h > max_w * max_h:
                floor_contour = room_contours[i]
    room_contours.remove(floor_contour)

    # Get each room
    for i in range(0, len(room_contours)):
        cv2.drawContours(image, room_contours, i, (0, 0, 255), 3)
        cv2.imwrite("room{}.png".format(i), image)
        cv2.drawContours(image, room_contours, i, (0, 0, 0), 3) # restore original image

    rooms = {}
    for i in range(0, len(room_contours)):
        name = input("\nEnter the name of the room displayed in room{}.png\n".format(i))
        x, y, w, h = cv2.boundingRect(contours[i])
        rooms.update({name:[x,y,w,h]})

    test = "this"
    # cv2.drawContours(image, room_contours, -1, (0, 255, 0), 3)
    # cv2.imwrite("test.png", image)


def main():
    test_image = Image.open("color_floor_plan.jpg")
    grey = convert_to_grey_scale(test_image)
    threshold = dilation(erosion(erosion(grey)))
    save_image(threshold, "temp.png")
    new_image = line_closing("temp.png")
    opencv_write(new_image, "new_image.png")
    room_detection("new_image.png")

main()




