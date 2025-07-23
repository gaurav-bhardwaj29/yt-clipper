
import argparse
import ffmpeg
import os

def extract_audio(input_video, output_audio=None):
    """
    Extracts audio from a video file and saves it as an MP3.

    :param input_video: Path to the input video file.
    :param output_audio: Path to the output audio file (optional).
    """
    if not os.path.exists(input_video):
        print(f"Error: Input file not found at '{input_video}'")
        return

    if not output_audio:
        base, _ = os.path.splitext(input_video)
        output_audio = f"{base}.mp3"

    try:
        (
            ffmpeg
            .input(input_video)
            .output(output_audio, acodec='libmp3lame', audio_bitrate='192k')
            .run(overwrite_output=True, quiet=True)
        )
        print(f"Audio successfully extracted to {output_audio}")
    except ffmpeg.Error as e:
        print("ffmpeg error:")
        print(e.stderr.decode())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract audio from video")
    parser.add_argument("input_video", help="path to input video.")
    parser.add_argument("-o", "--output", help="output audio filename") # if not specified, saves as <input_video_filename>.mp3

    args = parser.parse_args()
    extract_audio(args.input_video, args.output)
