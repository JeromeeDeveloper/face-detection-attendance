from django.shortcuts import render
import cv2
from django.http import StreamingHttpResponse
import face_recognition





def gen(camera):
    while True:
        ret, frame = camera.read()
        if not ret:
            break
        # Encode the frame in JPEG format
        ret, jpeg = cv2.imencode('.jpg', frame)
        # Convert the frame to bytes and yield it
        frame = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    # Capture video from webcam
    camera = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not access webcam.")
        exit()

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame from webcam.")
            break

        # Convert the frame from BGR to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        # Find face locations
        face_locations = face_recognition.face_locations(rgb_frame)

        if face_locations:
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                matches = face_recognition.compare_faces([ref_encoding], face_encoding)

                if matches[0]:
                    label = 'Face Recognized'
                    color = (0, 255, 0)  # Green for recognized face
                else:
                    label = 'Face Not Recognized'
                    color = (0, 0, 255)  # Red for unrecognized face

                # Draw rectangle around the face
                cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        else:
            # If no face is detected
            cv2.putText(frame, 'No Face Detected', (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        # Display the resulting frame
        cv2.imshow('Face Detection and Recognition', frame)

        # Break the loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the webcam and close all OpenCV windows
    cap.release()
    cv2.destroyAllWindows()
    return StreamingHttpResponse(gen(cap),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def Home(request):
    return render(request, 'attendance_logs/app1.html')

def load_reference_encoding(image_path):
    image = face_recognition.load_image_file(image_path)
    encodings = face_recognition.face_encodings(image)
    if len(encodings) == 0:
        raise ValueError("No face detected in the reference image.")
    return encodings[0]

# Use the absolute path to the reference image
reference_image_path = r'C:\Users\porca.UE\OneDrive\Desktop\django\attendance\attendance\attendance_logs\pictures\jenny.jpg'

try:
    print(f"Loading reference image from: {reference_image_path}")
    ref_encoding = load_reference_encoding(reference_image_path)
except ValueError as e:
    print(e)
    exit()
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

# Access the webcam

