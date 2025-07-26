### Usage

  Scenario 1: Download a clip with auto-generated English subtitles

`python yt_clipper_pro.py "https://www.youtube.com/watch?v=123456" 00:00:10 00:00:20 30 -o my_clip.mp4`

  Scenario 2: Download a clip with auto-generated Spanish subtitles

`python yt_clipper_pro.py "https://www.youtube.com/watch?v=123456" 00:00:10 00:00:20 30 -o my_clip.mp4 -sl es`

  Scenario 3: Use a local subtitle file 

`python yt_clipper_pro.py "https://www.youtube.com/watch?v=123456" 00:00:10 00:00:20 30 -o my_clip.mp4 -s my_subtitles.srt`

  Scenario 4: Disable the automatic subtitle syncing

`python yt_clipper_pro.py "https://www.youtube.com/watch?v=123456" 00:00:10 00:00:20 30 -o my_clip.mp4 --no-sync`
