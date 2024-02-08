import subprocess
import sys
import os

# list of video files
video_list = []

# read file with video names, determine the number of videos to be concatenated
with open(sys.argv[1], 'r') as inf:
    lines = inf.read().splitlines()
    video_count = len(lines)
    print("\nNumber of clips: ", video_count)

    i = 0
    while i < video_count:
        video_list.append(lines[i])
        i += 1

#for video in video_list:
#    print(video)

# create the input string for ffmpeg
input_str = " ".join(['-i ' + v for v in video_list])
print('\n', input_str)

# create the output file name with an absolute path
output_file = os.path.abspath("pigeons_cove.mp4")
#print('\nOutput file: ', output_file)

# create the ffmpeg command
command = f'ffmpeg {input_str} -filter_complex "xfade=transition=fade:duration=0.5[video];acrossfade=d=0.5[audio]" -c:v libx264 -map [audio] -map [video] -crf 23 -preset veryfast -c:a aac -b:a 192k pigeons_cove.mp4'

print('\n', command)

# run the command
subprocess.run(command, shell=True)






