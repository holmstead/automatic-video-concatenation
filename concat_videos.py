## created by holmstead ##
#
# example command:
# python3 ~/python/video_editing/concat_videos.py video_list 720
#
#

import subprocess, sys
from pathlib import Path

inf_extension =".mp4"
outf_extension = ".mp4"
vcodec = "libx264" 		# "libx264", "mpeg4"
acodec = "aac"			# "mp3", "aac"
fps = "30"
crf = "23"
qscale = "0"
preset = "medium" 		# veryfast/fast/normal/slow/veryslow/
tune = "film" 			# animation/grain/still-image/film
scale = None 			# 845:480, 1280:720, 1920:1080, 4000:3000

transition_dur = "0.5"
## choose transitions between video:
# fade, pixelise, circleopen, circleclose, radial, hblur, hrslice,
# hlslice, vuslice, vdslice, fadegrays, fadewhite, rectcrop,
# circlecrop, distance, diagtl, wipeleft, wiperight, slidedown,
# slideup, wipeleft, slideright
transitions = ["hblur", "pixelize", "rectcrop", "diagtl", "radial", "hblur", "circleopen", "fadewhite", "wipeleft", "slideleft", "fade", "hblur", "pixelize", "rectcrop", "diagtl", "radial", "hblur", "circleopen", "fadewhite", "wipeleft", "hblur", "pixelize", "rectcrop", "diagtl", "radial", "hblur", "circleopen", "fadewhite", "wipeleft", "slideleft", "fade", "hblur", "pixelize", "rectcrop", "diagtl", "radial", "hblur", "circleopen", "fadewhite", "wipeleft"]

video_list = []
temp_video_list = []
video_durations = []
offsets = []

## FUNCTION DECLARATIONS ##

def create_temp_video(video):
	'''
	this create temporary videos from the given arguement which
	have all the same attributes
	'''
	inf = Path(video)
	print('\nInput file: ', inf)
	inf_wo_ext = inf.with_suffix('')
	print('Input file w/o ext: ', inf_wo_ext)
	outf = str(inf_wo_ext) + "_temp.mp4"
	print('Temporary output file: ', outf)
	print()

	subprocess.run(["ffmpeg", "-i", video, \
	 "-filter_complex","scale="+str(scale)+ \
	 ":force_original_aspect_ratio=decrease,setsar=1,fps="+str(fps)+",format=yuv420p", \
	 "-c:v", vcodec, "-preset", preset, "-crf", crf, "-tune", \
	  tune, "-c:a", acodec, "-movflags", "+faststart", outf])

def get_video_duration(video):
	duration = subprocess.check_output(['ffprobe', '-i', video, \
				'-show_entries', 'format=duration', '-v', 'quiet', \
				'-of', 'csv=%s' % ("p=0")], universal_newlines=True)
	print("Video duration: ", duration)
	video_durations.append(duration)

def update_temp_video_list(video):
	print('\nVideo list: ', video)
	inf = Path(video)
	inf_wo_ext = inf.with_suffix('')
	print('\nVideo without extension: ', inf_wo_ext)
	inf = str(inf_wo_ext) + "_temp.mp4"
	temp_video_list.append(inf)
	print()


## MAIN PROGRAM ##

if sys.argv[2] == "1080":
	scale = "1920:1080"
elif sys.argv[2] == "1620x1080":
	scale = "1620:1080"
elif sys.argv[2] == "720":
	scale = "1280:720"
elif sys.argv[2] == "4000":
	scale = "4000:3000"
elif sys.argv[2] == "480":
	scale = "845:480"
elif sys.argv[2] == "640x352":
	scale = "640:352"
print("\nScale: ", scale)

## read file with video names, determine no. of videos to be concatenated
with open(sys.argv[1], 'r') as inf:
	lines = inf.read().splitlines()
	video_count = len(lines)
	print("\nNumber of clips: ", video_count)

	i = 0
	while (i < video_count):
		video_list.append(lines[i])
		i += 1

for video in video_list:
	print(video)

## create temporary videos, all with same attributes
for video in video_list:
	create_temp_video(video)
	update_temp_video_list(video)
	get_video_duration(video)

print("\nTemporary video list:\n", temp_video_list)
print("\nLength of video list:\n", len(video_list))
print("\nVideo durations:\n", video_durations)
 
## determine offsets for audio/video streams
offsets.append((float(video_durations[0])-float(transition_dur)))
print(offsets)
j=0
while (j < video_count-1):
	#print("offset: ", offsets[j])
	#print("video_dur: ", video_durations[j])
	offsets.append(offsets[j] + (float(video_durations[j+1])-float(transition_dur)))
	j += 1
print("\nOffsets: ")
print(offsets)
print()	



## concatenate temp videos
outf = sys.argv[1] + outf_extension

#inputs =  " -i, " + str(temp_video_list[0]) + ", -i, " + str(temp_video_list[1]) + ", -i, " + str(temp_video_list[2])
#print(inputs)

video_settings =  "[0][1]xfade=transition="+str(transitions[0])+":duration="+str(transition_dur)+":offset="+str(offsets[0])
i = 1
while (i < video_count-1):
	transition = "transition"+str(i)
	print(transition)	
	video_settings += "[V"+str(i)+"];[V"+str(i)+"]["+str(i+1)+"]xfade=transition="+str(transitions[i])+":duration="+str(transition_dur)+":offset="+str(offsets[i])
	i+=1
video_settings += ",format=yuv420p[video];"

audio_settings =  "[0:a][1:a]acrossfade=d="+str(transition_dur)
i = 1
while (i < video_count-1):
	audio_settings += "[A"+str(i)+"];[A"+str(i)+"]["+str(i+1)+":a]acrossfade=d="+str(transition_dur)
	i+=1
audio_settings += "[audio]"

print("\nConcatenation settings: \n", video_settings+audio_settings)
print()

if video_count ==2:
	subprocess.run(["ffmpeg",
	"-i", temp_video_list[0], "-i", temp_video_list[1],
	"-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map",
	"[audio]", "-crf", crf, "-movflags", "+faststart", outf])

if video_count ==3:
	subprocess.run(["ffmpeg",
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2],
	"-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map",
	"[audio]", "-crf", crf, "-movflags", "+faststart", outf])

if video_count ==4:
	subprocess.run(["ffmpeg",
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], 
	"-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map",
 		"[audio]", "-crf", crf, "-movflags", "+faststart", outf])

if video_count == 5:
	subprocess.run(["ffmpeg",  
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 6:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 7:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 8:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 9:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 10:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 11:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 12:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 13:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 14:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 15:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 16:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 17:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 18:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 19:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 20:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 21:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 22:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20], "-i", temp_video_list[21],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 23:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20], "-i", temp_video_list[21], "-i", temp_video_list[22],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 24:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20], "-i", temp_video_list[21], "-i", temp_video_list[22], "-i", temp_video_list[23],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 25:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20], "-i", temp_video_list[21], "-i", temp_video_list[22], "-i", temp_video_list[23], "-i", temp_video_list[24],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 26:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20], "-i", temp_video_list[21], "-i", temp_video_list[22], "-i", temp_video_list[23], "-i", temp_video_list[24],
	"-i", temp_video_list[25],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

if video_count == 34:
	subprocess.run(["ffmpeg", 
	"-i", temp_video_list[0], "-i", temp_video_list[1], "-i", temp_video_list[2], "-i", temp_video_list[3], "-i", temp_video_list[4], 
	"-i", temp_video_list[5], "-i", temp_video_list[6], "-i", temp_video_list[7], "-i", temp_video_list[8], "-i", temp_video_list[9],
	"-i", temp_video_list[10], "-i", temp_video_list[11], "-i", temp_video_list[12], "-i", temp_video_list[13], "-i", temp_video_list[14],
	"-i", temp_video_list[15], "-i", temp_video_list[16], "-i", temp_video_list[17], "-i", temp_video_list[18], "-i", temp_video_list[19],
	"-i", temp_video_list[20], "-i", temp_video_list[21], "-i", temp_video_list[22], "-i", temp_video_list[23], "-i", temp_video_list[24],
	"-i", temp_video_list[25], "-i", temp_video_list[26], "-i", temp_video_list[27], "-i", temp_video_list[28], "-i", temp_video_list[29],
	"-i", temp_video_list[30], "-i", temp_video_list[31], "-i", temp_video_list[32], "-i", temp_video_list[33],
	"-crf", crf, "-filter_complex", (video_settings + audio_settings), "-map", "[video]", "-map", "[audio]", "-movflags", "+faststart", outf])

#print("\nDeleting temporary files")
#for video in temp_video_list:	
#	print(video)
#	subprocess.run(["rm", video])

