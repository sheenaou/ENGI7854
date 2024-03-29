from PIL import Image, ImageFilter
import cv2
import numpy as np
from copy import copy
import os
import shutil

def convert_to_grey_scale(image):
    """Converts an opened Image object to black/white

        args:
            image - A Pillow image object
    """
    return image.convert("1")

def save_image(image, name):
    """This function will save the Pillow image object to disk in a temporary location

        args:
            image - A Pillow image object
            name - The name that the image will be saved under
    """
    image.save(name)
    return

def dilation(image):
    """This function will perform the dilation image processing technique on the provided image

        args:
            image - A Pillow image object
    """
    filter = ImageFilter.MinFilter(3) # Should be MaxFilter if white on black
    filtered = image.filter(filter)
    return filtered

def erosion(image):
    """This function will perform the erosion image processing technique on the provided image

        args:
            image - A Pillow image object
    """
    filter = ImageFilter.MaxFilter(3) # Should be MinFilter if white on black
    filtered = image.filter(filter)
    return filtered

def line_closing(image_file): #color demo
    """This function will close any gaps found in the borders of the rooms

        args:
            image_file - The file path to the image
    """
    image = cv2.imread(image_file)
    edges = cv2.Canny(image, 75, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=150)
    for line in lines:
        x1, y1, x2, y2 = line[0]
        cv2.line(image, (x1, y1), (x2, y2), (0, 0, 0), 5)

    kernel = np.ones((5, 5), np.uint8)
    new_image = cv2.dilate(image, kernel, iterations=2)
    return new_image


def opencv_write(image, name):
    """This function will save the OpenCV image to disk

        args:
            image - A OpenCV image object
            name - The name that the image will be saved under
    """
    cv2.imwrite(name, image)

def room_detection(base_image):
    """This function will detect all the rooms in the floor plan and generate a set of image
    highlighting a different room that will be saved to disk. It will also collect details
    about each room from the user via command line

        args:
            base_image - The file path to an image which has already had line closing
    """
    # Find all the contours in the base image
    image = cv2.imread(base_image)
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

    # Find the contours of the entire floor
    floor_contour = None
    for i in range(0, len(room_contours)):
        x, y, w, h = cv2.boundingRect(room_contours[i])
        max_x, max_y, max_w, max_h =  cv2.boundingRect(floor_contour)
        if w * h > max_w * max_h:
            floor_contour = room_contours[i]
    room_contours.remove(floor_contour)

    # Generate each room image
    path = os.getcwd() + "/rooms"
    if not os.path.exists(path):
        os.mkdir(path)
    for i in range(0, len(room_contours)):
        cv2.drawContours(image, room_contours, i, (0, 0, 255), 3)
        cv2.imwrite(path + "//room{}.png".format(i), image)
        cv2.drawContours(image, room_contours, i, (0, 0, 0), 3) # restore original image

    # Collect room information from the user
    rooms = {}
    for i in range(0, len(room_contours)):
        name = input("\nEnter the name of the room displayed in room{}.png\n".format(i)).upper()
        real_width = input("\nEnter the width (x dimension) of the room displayed in room{}.png in metres\n".format(i)).upper()
        real_height = input("\nEnter the length (y dimension) displayed in room{}.png in metres\n".format(i)).upper()
        x, y, w, h = cv2.boundingRect(room_contours[i])
        sub_dict = {
            "X":x,
            "Y":y,
            "WIDTH":w,
            "HEIGHT":h,
            "REAL_WIDTH":real_width,
            "REAL_HEIGHT":real_height,
            "CONTOUR":room_contours[i]}
        rooms.update({name:sub_dict})

    return image, rooms

def change_rooms(image, rooms):
    """This function provides a command line interface to the user where they can modify the floor plan as desired.
    It responsible for generate two possible images for the user to chose from and persisting the chosen option.

        args:
            image - An OpenCV image object
            rooms - A dictionary containing information collected about each room
    """
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

            axis = input("Which dimension would you like to change? X/Y").upper()
            while axis not in ["X", "Y"]:
                axis = input("INVALID ROOM...TRY AGAIN\n"
                               "Which dimension would you like to change? X/Y").upper()
            dimension = "WIDTH" if axis == "X" else "HEIGHT"

            length = int(input("Current value of the dimension is {} metres.\n"
                               "What would you like to change it to in metres?".format(rooms[key]["REAL_" + dimension])))

            # Calculate scaling factor
            before = int(rooms[key]["REAL_" + dimension])
            scale = length / before

            # Generate temporary directory to store images
            path = os.getcwd() + "/options"
            if not os.path.exists(path):
                os.mkdir(path)

            # Generate the two option images
            new_contours = scale_contour(rooms[key]["CONTOUR"], scale, axis)
            temp0, temp1 = copy(image), copy(image)
            cv2.drawContours(temp0, new_contours, 0, (255, 255, 255), -1)
            cv2.drawContours(temp0, new_contours, 0, (0, 0, 0), 5)
            cv2.imwrite(path + "//option_a.jpg", temp0)

            cv2.drawContours(temp1, new_contours, 1, (255, 255, 255), -1)
            cv2.drawContours(temp1, new_contours, 1, (0, 0, 0), 5)
            cv2.imwrite(path + "//option_b.jpg", temp1)

            response = input("Which option would you like to keep? A, B, or None?")
            if response.upper() == "A":
                maintain = 0
                image = temp0
                rooms[key].update({rooms[key]["REAL_" + dimension]: length})
            elif response.upper() == "B":
                maintain = 1
                image = temp1
                rooms[key].update({rooms[key]["REAL_" + dimension]: length})
            else:
                maintain = None

            # Persist information if necessary
            if maintain is not None:
                x, y, w, h = cv2.boundingRect(new_contours[maintain])
                sub_dict = {
                    "X": x,
                    "Y": y,
                    "WIDTH": w,
                    "HEIGHT": h,
                    "REAL_WIDTH": rooms[key]["REAL_WIDTH"],
                    "REAL_HEIGHT": rooms[key]["REAL_HEIGHT"],
                    "CONTOUR": new_contours[maintain]}
                rooms.update({key: sub_dict})

            cv2.imwrite("new_image.jpg", eval("temp"+str(maintain)))

def scale_contour(contour, scale, axis):
    """This method will shift the contour along the x or y axis by the scaling factor

        args:
            contour -- An ndarray contour object
            scale -- The integer value representing the scaling factor
            axis -- The axis in which the contour will be scaled in (X/Y)
    """

    # Get limits for x and y axis
    x, y,= copy(contour[0][0][0]), copy(contour[0][0][1])
    for vertex in contour:
        x = vertex[0][0] if x < vertex[0][0] else x
        y = vertex[0][1] if y < vertex[0][1] else y

    # Normalize the contour
    M = cv2.moments(contour)
    cx = int(M['m10']/M['m00'])
    cy = int(M['m01']/M['m00'])
    normalized_contour = contour - [cx, cy]

    # Scaled the contour
    scaled_contour = copy(contour) # initialize
    for i in range(0, len(scaled_contour)):
        if axis.upper() == "X":
            scaled_contour[i] = [(normalized_contour[i][0][0] * scale) + cx, normalized_contour[i][0][1] + cy]
        elif axis.upper() == "Y":
            scaled_contour[i] = [normalized_contour[i][0][0] + cx, (normalized_contour[i][0][1] * scale) + cy]
        else:
            print("Invalid axis..no operation completed")
    scaled_contour = scaled_contour.astype(np.int32)

    # Get new bounds for x and y axis
    new_x, new_y = copy(scaled_contour[0][0][0]), copy(scaled_contour[0][0][1])
    for vertex in scaled_contour:
        new_x = vertex[0][0] if new_x < vertex[0][0] else new_x
        new_y = vertex[0][1] if new_y < vertex[0][1] else new_y

    # Shift axis to match limits
    shifted_contour = [copy(scaled_contour), copy(scaled_contour)] # initialize
    if axis.upper() == "X":
        shift = x - new_x
        for i in range(0, len(scaled_contour)):
            shifted_contour[0][i] = [shifted_contour[0][i][0][0] + shift, shifted_contour[0][i][0][1]]
            shifted_contour[1][i] = [shifted_contour[1][i][0][0] - shift, shifted_contour[1][i][0][1]]

    elif axis.upper() == "Y":
        shift = y - new_y
        for i in range(0, len(scaled_contour)):
            shifted_contour[0][i] = [shifted_contour[0][i][0][0], shifted_contour[0][i][0][1] + shift]
            shifted_contour[1][i] = [shifted_contour[1][i][0][0], shifted_contour[1][i][0][1] - shift]

    return shifted_contour

def main():
    # Create standard floor plan skeleton
    test_image = Image.open("color_demo.png")
    grey = convert_to_grey_scale(test_image)
    threshold = dilation(erosion(erosion(grey)))
    save_image(threshold, "temp.png")

    # Perform line closing operation
    new_image = line_closing("temp.png")
    opencv_write(new_image, "temp.png")

    # Room identification and segmentation
    image, rooms = room_detection("temp.png")

    # Room modification
    change_rooms(image, rooms)

    # Clean up temporary files
    path = os.getcwd()
    os.remove(path + "//temp.png")
    shutil.rmtree(path + "//rooms")
    shutil.rmtree(path + "//options")

main()




