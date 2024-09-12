from django.core.files.storage import default_storage
from django.shortcuts import render, get_object_or_404
from django.http import StreamingHttpResponse
from django.utils import timezone
import cv2
import face_recognition
from .models import Member, AttendanceLog

def load_reference_encodings():
    encodings = {}
    members = Member.objects.all()
    for member in members:
        if member.image:
            image_path = default_storage.path(member.image.name)  # Use default_storage to resolve the file path
            try:
                image = face_recognition.load_image_file(image_path)
                encodings[member.id] = face_recognition.face_encodings(image)[0]
            except FileNotFoundError:
                print(f"File not found: {image_path}")
                continue  # Skip this member if the file does not exist
    return encodings

def gen(camera, reference_encodings):
    while True:
        ret, frame = camera.read()
        if not ret:
            break

        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        face_locations = face_recognition.face_locations(rgb_frame)
        face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

        for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
            matches = face_recognition.compare_faces(list(reference_encodings.values()), face_encoding)

            if any(matches):
                matched_id = list(reference_encodings.keys())[matches.index(True)]
                label = 'Face Recognized'
                color = (0, 255, 0)

                # Handle attendance logging
                now = timezone.now()
                member = get_object_or_404(Member, pk=matched_id)
                log_entry, created = AttendanceLog.objects.get_or_create(
                    profile=member,
                    timestamp__date=now.date(),
                    defaults={'photo': None, 'is_correct': True}
                )
                if created:
                    print(f"Attendance logged for {member.firstname} {member.lastname} at {now}")
                else:
                    print(f"Attendance already logged for {member.firstname} {member.lastname} today")

            else:
                label = 'Face Not Recognized'
                color = (0, 0, 255)

            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            cv2.putText(frame, label, (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)

        if not face_locations:
            cv2.putText(frame, 'No Face Detected', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

        ret, jpeg = cv2.imencode('.jpg', frame)
        frame = jpeg.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def video_feed(request):
    reference_encodings = load_reference_encodings()

    camera = cv2.VideoCapture(0)
    if not camera.isOpened():
        return StreamingHttpResponse("Could not access webcam", status=500)

    return StreamingHttpResponse(gen(camera, reference_encodings),
                                 content_type='multipart/x-mixed-replace; boundary=frame')

def Home(request):
    return render(request, 'attendance_logs/app1.html')
