#!/usr/bin/env python3

import subprocess
from os import listdir
from os import system
import json
import argparse
import datetime
# exiftool -ee -X -api LargeFileSupport=1 full2.MP4 > full2.xml
# ~/gpmf-parser/demo/gpmfdemo full2.MP4 -g
# exiftool -ee -G3 -X GX010238.MP4 > GX010238.xml


# TODO
# find an efficient way to add global metadata
# dynamically list streams and map them in the ffmpeg concat command

def print_list(l):
	for a in l:
		print("\t"+a)
def print_dict(d):
	for key in d:
		print(key)
		print_list(d[key])


def dump_metadata(file_path, output_name=None):
	print("Dumping metadata for: "+file_path)
	if output_name is None:
		output_name = file_path[:-4]+".xml"
	system("exiftool -b -ee -X "+file_path+">"+output_name)

def get_video_number(filename):
	return filename.split('/')[-1][4:-4]

def is_gopro_video_part(metadata):
	if not "creation_time" in metadata["format"]["tags"]:
		return False
	filename = metadata["format"]["filename"].split("/")[-1]
	if not filename.upper().endswith(".MP4"):
		return False
	if filename[:2] in ["GH", "GX", "GS", "GP", "GO", "3D"]:
		if len(filename[2:-4]) == 6:
			return True
	return False


def list_videos(base_path):
	parts_list = [ base_path+f for f in listdir(base_path) if f.upper().endswith("MP4")]
	#print(parts_list)
	parts_metadata = []
	for part_path in parts_list:
		# Use FFmpeg to extract metadata from the video file
		ffprobe_cmd = ['ffprobe', '-v', 'quiet', '-show_format', '-print_format', 'json', part_path]
		result = subprocess.run(ffprobe_cmd, capture_output=True, text=True)
		# Parse the JSON output from FFmpeg
		metadata = json.loads(result.stdout)
		# Print the video duration and metadata
		if is_gopro_video_part(metadata):
			parts_metadata.append({"create":metadata["format"]["tags"]["creation_time"],"name":part_path, "duration": metadata["format"]["duration"]})
	videos = {}
	videos_duration = {}
	for part in parts_metadata:
		if part["create"] in videos:
			videos[part["create"]].append(part["name"])
			videos_duration[part["create"]]+= float(part["duration"])
		else:
			videos[part["create"]] = [part["name"]]
			videos_duration[part["create"]]= float(part["duration"])
	return videos, videos_duration


def merge_with_metadata(videos, add_global_metadata=False, provided_video_number = None):
	for key in videos:
		videos[key].sort()#key= lambda a : a["name"])
	for key in videos:
		if provided_video_number is not None and get_video_number(videos[key][0]) != provided_video_number:
				continue
		video = videos[key]
		if len(video) <= 1:
			print("Short video, nothing todo")
			continue
		video_number = get_video_number(video[0])
		output_file_path = base_path+video_number+"_"+key.split(".")[0].replace(":","-")+"_full.MP4"
		print("Working on video: "+video_number)
		# Create the concat.txt file
		with open(base_path+video_number+"_concat.txt", "w") as concat_file:
		    for file_path in video:
		        concat_file.write(f"file '{file_path}'\n")
		#concat_cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', base_path+'concat.txt', '-c', 'copy', '-map_metadata', '0', output_file_path]
		concat_cmd = ['ffmpeg', '-f', 'concat', '-safe', '0', '-i', base_path+video_number+'_concat.txt','-ignore_unknown', '-c', 'copy', '-map' ,'0:0' ,'-map', '0:1','-map', '0:2', '-map', '0:3', output_file_path]
		result = subprocess.run(concat_cmd)
		if add_global_metadata:
			print("Adding global metadata.")
			#metadata_cmd = ['exiftool', '-api LargeFileSupport=1', '-TagsFromFile', video[0], '"-all:all>all:all"', output_file_path, '-overwrite_original']
			# will not run for now as it rewrites the whole file
			# with large files this puts a lot of stress on the disk
			# example of missing data <Track3:TrackCreateDate>0000:00:00 00:00:00</Track3:TrackCreateDate>
			# Note: find a way to only inject the global metadata
			# https://www.trekview.org/blog/2022/join-gopro-chaptered-split-video-files-preserve-telemetry/
			system('exiftool -ee -api LargeFileSupport=1 -TagsFromFile '+ video[0]+' "-all:all>all:all" '+output_file_path +' -overwrite_original')
			#subprocess.run(metadata_cmd)



if __name__ == "__main__":
	parser = argparse.ArgumentParser(
                    prog='GoPRoMerger',
                    description='Merges gorpro parts with their metadata.')
	parser.add_argument('-b', '--base_path', required=True, help="Path to video parts.")
	parser.add_argument('--list_videos', action="store_true", required=False, help="List videos and their parts from a folder of parts.")
	parser.add_argument('--merge', action="store_true", required=False, help="Merge video parts into a single video, keeps all metadata except the global ones.")
	parser.add_argument('--dump_metadata', action="store_true", required=False, help="Dump the metadata of each video part.")
	parser.add_argument('--add_global_metadata', action="store_true", required=False, help="Add global metadata to end file, this will rewrite the file.")
	parser.add_argument('--video_number', required=False, help="Only merge or dump metadata for the video number specified.")
	args = parser.parse_args()
	base_path = args.base_path
	if not base_path.endswith("/"):
		base_path = base_path+"/"
	videos, videos_duration = list_videos(base_path)
	if args.list_videos:
		for key in videos:
			videos[key].sort()
			duration = datetime.timedelta(seconds=videos_duration[key])
			video_number = get_video_number(videos[key][0])
			print("Video number: "+video_number+", creation date: "+key+", duration: "+str(duration).split(".")[0]+", parts:")
			print_list(videos[key])
	if args.merge:
		merge_with_metadata(videos, add_global_metadata=args.add_global_metadata, provided_video_number=args.video_number)
	if args.dump_metadata:
		for key in videos:
			if get_video_number(videos[key][0]) != args.video_number:
				continue
			for part in videos[key]:
				dump_metadata(part)
