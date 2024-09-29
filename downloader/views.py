import os
import re
from django.shortcuts import render
from pytube import YouTube
from downloader.forms import YouTubeDownloadForm
from django.http import FileResponse, HttpResponse

# Function to extract and download YouTube video
def download_youtube_video(url):
    # Step 1: Extract the video ID from the URL using a regular expression
    def extract_video_id(url):
        # Pattern to capture only the video ID from the URL, ignoring query parameters
        video_id_match = re.search(r'(https?://)?(www\.)?(youtube|youtu\.be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})', url)
        if video_id_match:
            return video_id_match.group(5)  # Group 5 contains the video ID
        else:
            raise ValueError("Invalid YouTube URL")

    try:
        # Extract the video ID
        video_id = extract_video_id(url)

        # Step 2: Reconstruct the base URL using the video ID
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"Downloading video from: {video_url}")

        # Step 3: Download the video using pytube
        yt = YouTube(video_url)

        # Get the highest resolution stream available
        stream = yt.streams.get_highest_resolution()

        # Ensure that the 'videos/' directory exists
        output_path = os.path.join('videos')
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        # Download the video
        file_path = os.path.join(output_path, f"{yt.title}.mp4")
        print(f"Downloading: {yt.title}")
        stream.download(output_path=output_path, filename=f"{yt.title}.mp4")
        print(f"Download completed: {yt.title}")

        return file_path

    except Exception as e:
        raise Exception(f"An error occurred: {str(e)}")

# Django view function to handle the form and call the download function
def download_video(request):
    if request.method == 'POST':
        form = YouTubeDownloadForm(request.POST)
        if form.is_valid():
            url = form.cleaned_data['url']
            try:
                # Call the function to download the video
                file_path = download_youtube_video(url)

                # Serve the file as a download response
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))

            except Exception as e:
                # Handle any error that occurs during the download process
                return HttpResponse(f"Error occurred during the download: {str(e)}", status=500)

    else:
        form = YouTubeDownloadForm()

    return render(request, 'download.html', {'form': form})