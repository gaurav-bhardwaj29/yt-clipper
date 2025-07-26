
import argparse
import os
import subprocess
import yt_dlp
import ffmpeg
import pysubs2

def yt_clipper_pro(
    url,
    start_time,
    end_time,
    fps,
    output_filename,
    subtitle_file=None,
    subtitle_lang='en',
    sync=True
):
    """
    Downloads a YouTube video, adds subtitles,
    syncs them, and burns them into the video.
    """
    temp_video_filename = f"temp_video_{os.path.basename(output_filename)}"
    
    def time_to_seconds(t):
        try:
            h, m, s = map(int, t.split(':'))
            return h * 3600 + m * 60 + s
        except ValueError:
            return float(t)

    start_seconds = time_to_seconds(start_time)
    end_seconds = time_to_seconds(end_time)

    ydl_opts_video = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        'merge_output_format': 'mp4',
        'outtmpl': temp_video_filename,
        'download_ranges': yt_dlp.utils.download_range_func(None, [(start_seconds, end_seconds)]),
        'force_keyframes_at_cuts': True,
        'quiet': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts_video) as ydl:
        ydl.download([url])
    if not subtitle_file:
        print(f"No subtitle file provided. Attempting to download auto-generated subtitles in '{subtitle_lang}'...")
        temp_subtitle_filename = f"temp_subtitles.{subtitle_lang}.vtt"
        ydl_opts_subs = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': [subtitle_lang],
            'skip_download': True,
            'outtmpl': 'temp_subtitles',
        }
        with yt_dlp.YoutubeDL(ydl_opts_subs) as ydl:
            ydl.download([url])
        
        if not os.path.exists(temp_subtitle_filename):
            print(f"Could not download subtitles. The video will be created without subtitles.")
            subtitle_file = None
        else:
            subtitle_file = temp_subtitle_filename

    if subtitle_file:
        final_subtitle_file = subtitle_file
        if sync:
            print("Syncing subtitles...")
            synced_subtitle_file = f"synced_{os.path.basename(subtitle_file)}.srt"
            try:
                subprocess.run(
                    [
                        'ffsubsync',
                        temp_video_filename,
                        '-i',
                        subtitle_file,
                        '-o',
                        synced_subtitle_file,
                    ],
                    check=True, capture_output=True, text=True, encoding='utf-8'
                )
                final_subtitle_file = synced_subtitle_file
                print(f"Synced subtitles saved to {final_subtitle_file}")
            except (FileNotFoundError, subprocess.CalledProcessError) as e:
                print(f"Could not sync subtitles: {e}. Proceeding with unsynced subtitles.")

        try:
            print("Adjusting subtitle timing and converting to ASS format...")
            subs = pysubs2.load(final_subtitle_file, encoding='utf-8')
            for i in range(len(subs) - 1):
                if subs[i].end > subs[i+1].start:
                    subs[i].end = subs[i+1].start - 1
            
            ass_temp_file = "temp_final_subtitles.ass"
            subs.save(ass_temp_file)

            print("Burning subtitles into video...")
            (
                ffmpeg
                .input(temp_video_filename)
                .output(output_filename, vf=f"subtitles={ass_temp_file}", r=fps, video_bitrate='5000k', audio_bitrate='192k')
                .run(overwrite_output=True, quiet=True)
            )
            print(f"Successfully created subtitled video: {output_filename}")

        except Exception as e:
            print(f"An error occurred during subtitle processing: {e}")
            ffmpeg.input(temp_video_filename).output(output_filename, r=fps).run(overwrite_output=True, quiet=True)
            print(f"Created video without subtitles: {output_filename}")

        finally:
            if 'temp_subtitles' in final_subtitle_file and os.path.exists(final_subtitle_file):
                os.remove(final_subtitle_file)
            if 'synced' in final_subtitle_file and os.path.exists(final_subtitle_file):
                os.remove(final_subtitle_file)
            if os.path.exists("temp_final_subtitles.ass"):
                os.remove("temp_final_subtitles.ass")

    else: 
        print("No subtitles found or provided. Creating video without subtitles...")
        ffmpeg.input(temp_video_filename).output(output_filename, r=fps).run(overwrite_output=True, quiet=True)
        print(f"Successfully created video: {output_filename}")

    if os.path.exists(temp_video_filename):
        os.remove(temp_video_filename)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download a YouTube clip, add subtitles, and burn them in.")
    parser.add_argument("url", help="The URL of the YouTube video.")
    parser.add_argument("start_time", help="The start time in HH:MM:SS or seconds.")
    parser.add_argument("end_time", help="The end time in HH:MM:SS or seconds.")
    parser.add_argument("fps", type=int, help="The desired frames per second.")
    parser.add_argument("-o", "--output", default="output.mp4", help="The output filename.")
    parser.add_argument("-s", "--subtitle_file", help="Path to an external subtitle file (.srt, .vtt, .ass).", default=None)
    parser.add_argument("-sl", "--subtitle_lang", default='en', help="Language code for auto-generated subtitles (e.g., en, es, fr).")
    parser.add_argument("--no-sync", dest='sync', action='store_false', help="Do not attempt to sync subtitles.")
    
    args = parser.parse_args()
    
    yt_clipper_pro(args.url, args.start_time, args.end_time, args.fps, args.output, args.subtitle_file, args.subtitle_lang, args.sync)
