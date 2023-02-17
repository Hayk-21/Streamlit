import os
import streamlit as st
import face_recognition
import av
import cv2
from streamlit_webrtc import VideoProcessorBase, webrtc_streamer

class FaceRecognizer(VideoProcessorBase):
    def __init__(self):
        self.known_faces = []
        self.known_names = []
        self.load_known_faces()
        self.face_location = None
        self.face_encoding = None

    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        image = frame.to_ndarray(format="bgr24")
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)
        for face_encoding, face_location in zip(face_encodings, face_locations):
            results = face_recognition.compare_faces(self.known_faces, face_encoding, tolerance=0.6)
            name = "Unknown"
            (top, right, bottom, left) = face_location
            
            if True in results:
                match_index = results.index(True)
                name = self.known_names[match_index]
 
            cv2.rectangle(image, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.putText(image, name, (left, top-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            self.face_location = face_location
            self.face_encoding = face_encoding
        return av.VideoFrame.from_ndarray(image, format="bgr24")

    def load_known_faces(self):
        face_dir = "faces"
        image_extensions = {"jpg", "jpeg", "png"}
        for filename in os.listdir(face_dir):
            name, ext = os.path.splitext(filename)
            image = face_recognition.load_image_file(os.path.join(face_dir, filename))
            face_encoding = face_recognition.face_encodings(image)[0]
            self.known_faces.append(face_encoding)
            self.known_names.append(name)
