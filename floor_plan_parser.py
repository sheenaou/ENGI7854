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
        name = input("\nEnter the name of the room displayed in room{}.png\n".format(i)).upper()
        x, y, w, h = cv2.boundingRect(contours[i])
        sub_dict = {"X":x, "Y":y, "WIDTH":w, "HEIGHT":h, "CONTOUR":room_contours[i]}
        rooms.update({name:sub_dict})

    return image, rooms

def change_rooms(image, rooms):
    status = True
    while status:
        response = input("Would you like to make any alterations? Y/N\n>").upper()
        status = True if response == "Y" else False
        if status:
            print("Available Rooms:")
            for room in rooms.keys():
                print("> ", room)

            key = input("Which room would you like to change?").upper()
            while key not in rooms.keys():
                key = input("INVALID ROOM...TRY AGAIN\n"
                            "Which room would you like to change?").upper()

            action = input("Which dimension would you like to change? X/Y").upper()
            while action not in ["X", "Y"]:
                action = input("INVALID ROOM...TRY AGAIN\n"
                               "Which dimension would you like to change? X/Y").upper()
            dimension = "WIDTH" if action == "X" else "HEIGHT"

            length = input("Current value of the dimension is {}.\n"
                           "What would you like to change it to?".format(rooms[key][dimension]))

            # _, contours, _ = cv2.findContours(mask.astype(np.uint8), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
            #
            # coef_y = img_orig.shape[0] / img_resized.shape[0]
            # coef_x = img_orig.shape[1] / img_resized.shape[1]
            #
            # for contour in contours:
            #     contour[:, :, 0] = contour[:, :, 0] * coef_x
            #     contour[:, :, 1] = contour[:, :, 1] * coef_y
            #
            #     cv2.drawContours(img_orig, contour, -1, (0, 255, 0), 2)
            test = "this"


def main():
    test_image = Image.open("color_floor_plan.jpg")
    grey = convert_to_grey_scale(test_image)
    threshold = dilation(erosion(erosion(grey)))
    save_image(threshold, "temp.png")
    new_image = line_closing("temp.png")
    opencv_write(new_image, "new_image.png")
    image, rooms = room_detection("new_image.png")
    change_rooms(image, rooms)

main()




