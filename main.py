import apprise
import config
import glob
import os
import subprocess
from datetime import datetime


images_directory = "input"
timelapse_directory = "output"


def create_timelapse_for_stream(subfolder, week_number, force_framerate=False):
    """
    Uses ffmpeg to stitch all images in a directory (in datetime order) together
    to make a timelapse.
    :param force_framerate: Force the output to run at a different framerate
    than default (which is 24fps). If this is True, the output will be forced to
    60fps.
    :returns: The filepath of the timelapse video
    """
    # Use ffmpeg to stitch the images together into a timelapse
    # ffmpeg -pattern_type glob -i "*.png" output/<output>
    # ffmpeg -r 60 -pattern_type glob -i "*.png" output/<output>

    time_moment = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}"

    image_files = []
    for day_number in range(1,5):
        for hour in range(8,20):
            image_files += glob.glob(f"{images_directory}/{subfolder}/{week_number}/*-{day_number}-{hour:02d}*.png")
    image_files = sorted(image_files)
    
    index_filename = f"{time_moment}-index.txt"
    with open(index_filename, "w") as f:
        for image_file in image_files:
            f.write(f"file '{image_file}'\n")    
    print(f"Created {index_filename} with {len(image_files)} images")
    
    if force_framerate:
        framerate = "60"
        print(f"Creating timelapse at {framerate}fps")
    
        timelapse_filename = f"{time_moment}_fps_{framerate}.mp4"   

        timelapse_filepath = (
            f"{timelapse_directory}/{subfolder}/forced_fps/{timelapse_filename}"
        )
        
        timelapse_directory_full = f"{timelapse_directory}/{subfolder}/forced_fps"
        if not os.path.exists(timelapse_directory_full):
            os.makedirs(timelapse_directory_full)
        params = [
                "ffmpeg",
                "-r",
                framerate,
                # "-pattern_type",
                # "glob",
                "-f",
                "concat",
                "safe",
                "0",
                "-i",
                # f"{images_directory}/{subfolder}/{week_number}/*.png",
                f"'{index_filename}'",
				"-c:v",
				"libx264",
				"-crf",
				"23",
                "-vf",
                "scale=-1:720",
				"-maxrate",
				"4.5M",
				"-preset",
				"faster",
				"-flags",
				"+global_header",
				"-pix_fmt",
				"yuv420p", 
				"-profile:v", 
				"baseline", 
				"-movflags", 
				"+faststart",
				"-c:a", 
				"aac", 
				"-ac", 
				"2",
                timelapse_filepath,
            ]
        print(f"Running {' '.join(params)}")
        subprocess.run(
            params
        )
    else:
        framerate = "24"
        print(f"Creating timelapse at {framerate}fps")
        print(f"Creating a normal timelapse")

        timelapse_filename = f"{time_moment}_fps_{framerate}.mp4"   

        timelapse_filepath = (
            f"{timelapse_directory}/{subfolder}/normal_fps/{timelapse_filename}"
        )

        timelapse_directory_full = f"{timelapse_directory}/{subfolder}/normal_fps"
        if not os.path.exists(timelapse_directory_full):
            os.makedirs(timelapse_directory_full)

        params = [
                "ffmpeg",
                "-r",
                framerate,
                # "-pattern_type",
                # "glob",
                "-f",
                "concat",
                "safe",
                "0",
                "-i",
                # f"{images_directory}/{subfolder}/{week_number}/*.png",
                f"'{index_filename}'",
				"-c:v",
				"libx264",
				"-crf",
				"23",
				"-vf",
                "scale=-1:720",
				"-maxrate",
				"4.5M",
				"-preset",
				"faster",
				"-flags",
				"+global_header",
				"-pix_fmt",
				"yuv420p", 
				"-profile:v", 
				"baseline", 
				"-movflags", 
				"+faststart",
				"-c:a", 
				"aac", 
				"-ac", 
				"2",
                timelapse_filepath,
            ]
        print(f"Running {' '.join(params)}")
        subprocess.run(
            params
        )
    return timelapse_filepath


def create_timelapse(for_prev_week=False):
    
    """
    Creates a timelapse from images in the input directory and sends it to
    the configured Apprise services.

    It creates a timelapse for each camera in the config, and only creates
    a timelapse once we have a weeks worth of photos.

    It sends the timelapse to the Apprise services with a title and body.
    The title is "Timelapse", and the body is "Видео за <week_number> неделю. <stream_name>".
    The message is sent with the timelapse as an attachment.

    It also deletes the images in the input directory after sending the
    timelapse.

    :param None:

    :return: None
    """
    streams = config.streams
    
    week_number_dec = datetime.now().isocalendar()[1]
    
    # calc previous week
    if for_prev_week:
        if week_number_dec == 1:
            week_number_dec = 52
        else:
            week_number_dec = week_number_dec - 1

    week_number = f"{week_number_dec:02d}"

    for stream in streams:
        # Only create a timelapse once we have a weeks worth of photos

        stream_dir = f"{stream.get('stream_name')}"

        # Create the timelapse
        normal_timelapse_filepath = create_timelapse_for_stream(stream_dir, week_number)
        # forced_fps_timelapse_filepath = create_timelapse_for_camera(camera_dir, week_number, force_framerate=True)

        if os.path.exists(normal_timelapse_filepath):
            # Create an Apprise instance
            app = apprise.Apprise()

            for service in config.apprise_services:
                app.add(service)

            attachments = [
                normal_timelapse_filepath,
                # forced_fps_timelapse_filepath,
            ]

            # Send the message to the Apprise services
            print(f"Sending notification with {attachments}")
            app.notify(body=f"Видео за {week_number_dec} неделю. {stream.get('stream_name')}", title="Timelapse", attach=attachments)

            # Delete the images
            # print("Starting deletion")
            # for image_file in image_files:
            #     image_filepath = f"{images_directory}/{image_file}"
            #     if os.path.exists(image_filepath):
            #         print(f"Deleting {image_filepath}")
            #         os.remove(image_filepath)
        else:
            print(f"No timelapse created for {stream_dir} for week {week_number}")


def record_stream():

    stream = config.streams

    week_number_dec = datetime.now().isocalendar()[1]
    week_number = f"{week_number_dec:02d}"
    
    # read array of credentials and ips from config file
    for stream in stream:
        print("=========================================")
        print(f"Starting to record stream {stream['stream_name']}")
        rtsp_path = stream.get("stream_url")
        stream_dir = f"{images_directory}/{stream.get('stream_name')}/{week_number}"
        
        if not os.path.exists(stream_dir):
            os.makedirs(stream_dir)

        print(f"Stream dir is {stream_dir}")
        # Use ffmpeg to connect to the rtsp stream and save 1 frame
        # ffmpeg -i <stream> -frames:v 1 <output>
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    rtsp_path,
                    "-frames:v",
                    "1",
                    f"{stream_dir}/{datetime.now().strftime('%Y%m%d-%u-%H%M%S')}.png",
                ]
            )
            print("Finished recording stream")

        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    
    appmode = os.getenv('appmode','recorder')
    for_prev_week = os.getenv('for_prev_week', False)
    
    if appmode == "timelapse":
        create_timelapse(for_prev_week)
    else:
        record_stream()
