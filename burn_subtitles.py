
import argparse
import ffmpeg
import os
import subprocess
import pysubs2

def burn_subtitles(
    input_video,
    subtitle_file,
    output_video=None,
    sync=False,
    encoding='utf-8'
):
    """
    Burns subtitles into a video file, fixing overlaps.
    """
    if not os.path.exists(input_video):
        print(f"Error: Input video not found at '{input_video}'")
        return

    if not os.path.exists(subtitle_file):
        print(f"Error: Subtitle file not found at '{subtitle_file}'")
        return

    if not output_video:
        base, _ = os.path.splitext(input_video)
        output_video = f"{base}_subtitled.mp4"

    temp_subtitle_files = []
    final_subtitle_file = subtitle_file

    if sync:
        print("Syncing subtitles...")
        synced_subtitle_file = f"synced_{os.path.basename(subtitle_file)}"
        temp_subtitle_files.append(synced_subtitle_file)
        try:
            subprocess.run(
                [
                    'ffsubsync',
                    input_video,
                    '-i',
                    subtitle_file,
                    '-o',
                    synced_subtitle_file,
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding=encoding
            )
            print(f"Synced subtitles saved to {synced_subtitle_file}")
            final_subtitle_file = synced_subtitle_file
        except FileNotFoundError:
            print("ffsubsync not found. Please install it with: pip install ffsubsync")
            return
        except subprocess.CalledProcessError as e:
            print("Error syncing subtitles:")
            print(e.stderr)
            return

    try:
        # fix overlaps
        subs = pysubs2.load(final_subtitle_file, encoding=encoding)
        for i in range(len(subs) - 1):
            if subs[i].end > subs[i+1].start:
                subs[i].end = subs[i+1].start - 1 # Leave a 1ms gap


        ass_temp_file = "temp_subtitles.ass"
        subs.save(ass_temp_file)
        temp_subtitle_files.append(ass_temp_file)

        print("Burning subtitles...")
        (
            ffmpeg
            .input(input_video)
            .output(output_video, vf=f"subtitles={ass_temp_file}")
            .run(overwrite_output=True, quiet=True)
        )
        print(f"Subtitled video saved as {output_video}")

    except ffmpeg.Error as e:
        print("ffmpeg error:")
        print(e.stderr.decode())
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        for f in temp_subtitle_files:
            if os.path.exists(f):
                os.remove(f)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Burn subtitles into a video file, fixing rendering issues.")
    parser.add_argument("input_video", help="The path to the input video file.")
    parser.add_argument("subtitle_file", help="The path to the subtitle file (.srt).")
    parser.add_argument("-o", "--output", help="The output video filename (optional).")
    parser.add_argument("--sync", action="store_true", help="Sync subtitles before burning.")
    parser.add_argument(
        '--encoding',
        default='utf-8',
        help='The character encoding of the subtitle file (e.g., utf-8, latin-1).'
    )

    args = parser.parse_args()
    burn_subtitles(args.input_video, args.subtitle_file, args.output, args.sync, args.encoding)
