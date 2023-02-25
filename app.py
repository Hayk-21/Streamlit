!pip install --upgrade pip
import streamlit as st
import cv2
import os
import time
import face_recognition
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer
from recognition import FaceRecognizer
from PIL import Image

def take_photo():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        st.error("Unable to access camera")
        return

    # Read the image from the camera
    ret, frame = cap.read()
    if not ret:
        st.error("Unable to read camera frame")
        return

    # Release the camera
    cap.release()

    return frame

def detect_face(image):
    # Load the Haar cascade for face detection
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Convert the image to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Detect faces in the grayscale image
    faces = face_cascade.detectMultiScale(gray, 1.3, 5)

    # If faces were detected, return True, else return False
    if len(faces) > 0:
        return True
    else:
        return False

def save_photo(image, user_name):
    # Create the "faces" folder if it doesn't exist
    if not os.path.exists("faces"):
        os.makedirs("faces")

    # Save the image to a file in the "faces" folder
    image_path = os.path.join("faces", f"{user_name}.jpg")
    cv2.imwrite(image_path, image)
    st.success('Photo saved successfully!')

def main(isadmin):

    if isadmin:
        pages = {
            "User Photos": show_photos,
        }

        page_titles = pages.keys()

        page_title = st.sidebar.selectbox(
            "Choose the Admin desk mode",
            page_titles,
        )
    else: 
        st.title("Face recognition application")

        pages = {
            "User Profile": user_profile,
            "Live Recognition": recognition
        }
    
        page_titles = pages.keys()

        page_title = st.sidebar.selectbox(
            "Choose the app mode",
            page_titles,
        )
        
    st.subheader(page_title)
    page_func = pages[page_title]
    page_func()

def show_photos():
    # Get a list of all image files in the "faces" folder
    image_files = os.listdir("faces")

    # Create two columns to display the images
    col1, col2, col3 = st.columns(3)

    # Display each image in its own column
    for i, image_file in enumerate(image_files):
        # Open the image using Pillow
        image = Image.open(os.path.join("faces", image_file))

        # Determine which column to put the image in (alternating between col1 and col2)
        if i % 3 == 0:
            col = col1
        elif i % 2 == 0:
            col = col2
        else:
            col = col3

        # Display the image in the column
        col.image(image, width=200)
        col.caption(image_file.split('.jpg')[0])
    
def user_profile():

    user_name = st.text_input("Enter your full name:")

    st.write("Please take a photo of yourself:")

    if user_name != None and st.button("Take photo"):
        image = take_photo()
        if image is not None:
            # Display the captured photo
            if detect_face(image=image):
                st.image(image, caption="Your photo", use_column_width=True)
                # Save the captured photo to a file
                save_photo(image, user_name)
                # Redirect to the other app
                if st.button("Clear"):
                    # Clear the cache to clear the screen
                    st.caching.clear_cache()
                    st.experimental_rerun()
            else:
                st.warning('There is no face in the photo!')
        else:
            st.write("Unable to capture photo")

    if user_name:
        st.write("Full name:", user_name)
        if user_name == "Hayk Sakoyan":
            main(True)
    else:
        st.write("Please enter your full name.")

def recognition():

    face_recognizer = None
    webrtc_ctx = webrtc_streamer(key="example", video_processor_factory=FaceRecognizer)

    if webrtc_ctx.video_processor:
        face_recognizer = webrtc_ctx.video_processor

if __name__ == "__main__":
    main(False)
