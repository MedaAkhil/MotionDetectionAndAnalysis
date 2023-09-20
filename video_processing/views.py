# from django.shortcuts import render

# # Create your views here.


import numpy as np
import cv2
import matplotlib.pyplot as plt
from scipy.fft import fft

from django.shortcuts import render, get_object_or_404
from .models import ProcessedVideo
from django.shortcuts import render, redirect
from .forms import VideoUploadForm
from django.conf import settings  # Import the settings
# from .models import ProcessedVideo

# # Import your video processing script here

def upload_video(request):
    if request.method == 'POST':
        form = VideoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the uploaded video
            instance = form.save()

            # Process the video (Use your provided script)
            # ...

            # Save the plot as an image
            # ...

            return redirect('video_detail', pk=instance.pk)
    else:
        form = VideoUploadForm()
    return render(request, 'video_processing/upload_video.html', {'form': form})

# def video_detail(request, pk):
#     video = ProcessedVideo.objects.get(pk=pk)
#     return render(request, 'video_processing/video_detail.html', {'video': video})



















def video_detail(request, pk):
    plot_path = settings.MEDIA_URL + 'plots/path_to_save_plot.png'
    video = get_object_or_404(ProcessedVideo, pk=pk)

    # Your video processing code here
    # ...
    count=0
    video = cv2.VideoCapture('./media/videos/test.mp4')


# Check if the video source was successfully opened
    if not video.isOpened():
        print("Error: Could not open video source.")
        exit()

# Read the first frame to initialize the background
    status, background = video.read()
    if not status:
        print("Error: Could not read the first frame.")
        exit()

    background = cv2.cvtColor(background, cv2.COLOR_BGR2GRAY)
    background = cv2.GaussianBlur(background, (21, 21), 0)
    x=0
    while True:
    # Read the next frame
        status, frame = video.read()
        print(x)
    # Check if the frame was successfully read
        if not status:
            print("End of video.")
            break

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        diff = cv2.absdiff(background, gray)
        np.savetxt('vibration_data.txt',diff)
        thresh = cv2.threshold(diff, 5, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        cnts, res = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for contour in cnts:
        # if cv2.contourArea(contour) < 10000:
        #     continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 3)

            count += 1
        x=x+1

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

# Release the video source and close all OpenCV windows
    video.release()
    cv2.destroyAllWindows()
    # Generate and save the plot as an image
    vibration_signal = np.loadtxt('vibration_data.txt')
    sampling_rate = 1000  # Adjust as needed
    n = len(vibration_signal)
    frequencies = np.fft.fftfreq(n, 1 / sampling_rate)
    amplitude_spectrum = np.abs(fft(vibration_signal))
    half_length = n // 2

    # Plot the amplitude spectrum and save it as an image
    plt.figure(figsize=(10, 6))
    plt.xlim(0, 500)
    plt.ylim(0, 10000)
    plt.plot(frequencies[:half_length], amplitude_spectrum[:half_length])
    plt.xlabel('Frequency (Hz)')
    plt.ylabel('Amplitude')
    plt.title('Frequency Analysis of Vibration Data')
    plt.grid(True)
    plt.savefig(r'media/plots/path_to_save_plot.png')  # Save the plot as an image
    plt.close()  # Close the plot to free up resources

    return render(request, 'video_processing/video_detail.html', {'video': video, 'plot_path': settings.MEDIA_URL + 'plots/path_to_save_plot.png'})
