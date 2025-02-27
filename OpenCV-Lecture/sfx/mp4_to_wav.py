import sys
from moviepy import *

def convert_mp4_to_wav(mp4_file, wav_file):
    # Load the video file
    video = VideoFileClip(mp4_file)
    # Extract the audio from the video
    audio = video.audio
    # Write the audio to a WAV file
    audio.write_audiofile(wav_file, codec='pcm_s16le')
    # Close the clip objects to free resources
    audio.close()
    video.close()

if __name__ == "__main__":
    convert_mp4_to_wav("Startup.mp4", "Startup.wav")

    convert_mp4_to_wav("Shutdown.mp4", "Shutdown.wav")
