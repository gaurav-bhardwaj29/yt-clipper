import argparse
import yt_dlp
import ffmpeg
import os

def dcv(url, start_time, end_time, fps, output_filename):
    
    def time_to_seconds(t):
        try:
            h, m, s = map(int, t.split(':'))
            return h * 3600 + m * 60 + s
        except:
            return float(t)

    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)
    temp_output = f"temp_{os.path.basename(output_filename)}"

    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': temp_output,
        'download_ranges': yt_dlp.utils.download_range_func(None, [(start_seconds, end_seconds)]),
        'force_keyframes_at_cuts': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    # re-encode for given FPS
    try:
        (
            ffmpeg
            .input(temp_output)
            .output(output_filename, r=fps, video_bitrate='5000k', audio_bitrate='192k')
            .run(overwrite_output=True, quiet=True)
        )
        print(f"Video saved as {output_filename}")
    except ffmpeg.Error as e:
        print('ffmpeg error:')
        print(e.stderr.decode())
    finally:
        if os.path.exists(temp_output):
            os.remove(temp_output)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and cut a YouTube video.")
    parser.add_argument("url", help="URL of the YouTube video.")
    parser.add_argument("start_time", help="start time in HH:MM:SS or seconds.")
    parser.add_argument("end_time", help="end time in HH:MM:SS or seconds.")
    parser.add_argument("fps", type=int, help="desired fps.")
    parser.add_argument("-o", "--output", default="output.mp4", help="output filename.")
    
    args = parser.parse_args()
    
    dcv(args.url, args.start_time, args.end_time, args.fps, args.output)