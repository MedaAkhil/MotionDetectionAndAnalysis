import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.fft import fft
import os

from django.shortcuts import render, get_object_or_404
from .models import ProcessedVideo
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from django.conf import settings  

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()

            return redirect('video_detail', pk=instance.pk)
    else:
        form = VideoUploadForm()
    return render(request, 'video_processing/upload_video.html', {'form': form})

def video_detail(request, pk):
    plot_path = settings.MEDIA_URL + 'plots/path_to_save_plot.png'
    video = get_object_or_404(ProcessedVideo, pk=pk)

    count = 0
    video_path = os.path.join(settings.MEDIA_ROOT, str(video.video))
    print(video_path)
    video_capture = cv2.VideoCapture(video_path)  

    if not video_capture.isOpened():
        print("Error: Could not open video source.")
        exit()

    status, background = video_capture.read()
    if not status:
        print("Error: Could not read the first frame.")
        exit()

    background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    background = cv2.GaussianBlur(background, (21, 21), 0)
    while True:
        status, frame = video_capture.read()
        if not status:
            print("End of video.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        diff = cv2.absdiff(background, gray)
        np.savetxt('vibration_data.txt', diff)
        thresh = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        cnts, res = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in cnts:
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            count += 1

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()
    vibration_signal = np.loadtxt('vibration_data.txt')
    sampling_rate = 1000
    n = len(vibration_signal)
    frequencies = np.fft.fftfreq(n, 1 / sampling_rate)
    amplitude_spectrum = np.abs(fft(vibration_signal))
    half_length = n // 2

    plt.figure(figsize=(10, 6))
    plt.xlim(0, 500)
    plt.ylim(0, 10000)
    plt.plot(frequencies[:half_length], amplitude_spectrum[:half_length])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title('Frequency Analysis of Vibration Data')
    plt.grid(True)
    plt.savefig(settings.MEDIA_ROOT + '/plots/path_to_save_plot.png') 
    plt.close()  

    return render(request, 'video_processing/video_detail.html', {'video': video, 'plot_path': settings.MEDIA_URL + 'plots/path_to_save_plot.png'})
