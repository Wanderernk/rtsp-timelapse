import apprise
import config
import glob
import os
import subprocess
from datetime import datetime


images_directory = "input"
timelapse_directory = "output"


def create_timelapse_for_camera(subfolder, week_number, force_framerate=False):
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

    if force_framerate:
        framerate = "60"
        print(f"Creating timelapse at {framerate}fps")
        timelapse_filename = (
            f"{datetime.now().strftime('%Y%m%d-%H%M%S')}_fps_{framerate}.mp4"
        )
        timelapse_filepath = (
            f"{timelapse_directory}/{subfolder}/forced_fps/{timelapse_filename}"
        )
        
        timelapse_directory_full = f"{timelapse_directory}/{subfolder}/forced_fps"
        if not os.path.exists(timelapse_directory_full):
            os.makedirs(timelapse_directory_full)

        subprocess.run(
            [
                "ffmpeg",
                "-r",
                framerate,
                "-pattern_type",
                "glob",
                "-i",
                f"{images_directory}/{subfolder}/*-{week_number}-*.png",
                f"{timelapse_directory}/{subfolder}/forced_fps/{timelapse_filename}",
            ]
        )
    else:
        print(f"Creating a normal timelapse")
        timelapse_filename = f"{datetime.now().strftime('%Y%m%d-%H%M%S')}.mp4"
        timelapse_filepath = (
            f"{timelapse_directory}/{subfolder}/normal_fps/{timelapse_filename}"
        )

        timelapse_directory_full = f"{timelapse_directory}/{subfolder}/normal_fps"
        if not os.path.exists(timelapse_directory_full):
            os.makedirs(timelapse_directory_full)

        subprocess.run(
            [
                "ffmpeg",
                "-pattern_type",
                "glob",
                "-i",
                f"{images_directory}/{subfolder}/*-{week_number}-*.png",
                f"{timelapse_directory}/{subfolder}/normal_fps/{timelapse_filename}",
            ]
        )
    return timelapse_filepath


def main():

    # read array of credentials and ips from config file
    rtsp_username = config.rtsp_username
    rtsp_password = config.rtsp_password

    rtsp_ip_address = config.ip_cameras

    for camera_ip_address in rtsp_ip_address:
        rtsp_path = (
            f"rtsp://{rtsp_username}:{rtsp_password}@{camera_ip_address}/stream1"
        )
        camera_dir = f"{images_directory}/{camera_ip_address}"
        if not os.path.exists(camera_dir):
            os.makedirs(camera_dir)

        # Use ffmpeg to connect to the rtsp stream and save 1 frame
        # ffmpeg -i <stream> -vframes 1 <output>
        try:
            subprocess.run(
                [
                    "ffmpeg",
                    "-i",
                    rtsp_path,
                    "-frames:v",
                    "1",
                    f"{camera_dir}/{datetime.now().strftime('%Y%m%d-%W-%w-%H%M%S')}.png",
                ]
            )
        except subprocess.CalledProcessError as e:
            print(f"Error: {e}")


def create_timelapse():
    rtsp_ip_address = config.ip_cameras
    
    week_number_dec = datetime.now().isocalendar()[1]
    
    # calc previous week
    if week_number_dec == 0:
        week_number_dec = 52
    else:
        week_number_dec = week_number_dec - 1

    week_number = f"{week_number_dec:02d}"

    for camera_ip_address in rtsp_ip_address:
        # Only create a timelapse once we have a weeks worth of photos

        camera_dir = f"{camera_ip_address}"

        # Create the timelapse
        normal_timelapse_filepath = create_timelapse_for_camera(camera_dir, week_number)
        forced_fps_timelapse_filepath = create_timelapse_for_camera(camera_dir, week_number, force_framerate=True)

        # Create an Apprise instance
        app = apprise.Apprise()

        for service in config.apprise_services:
            app.add(service)

        attachments = [
            normal_timelapse_filepath,
            forced_fps_timelapse_filepath,
        ]

        # Send the message to the Apprise services
        print(f"Sending notification with {attachments}")
        app.notify(body="Weekly timelapse", title="Timelapse", attach=attachments)

        # Delete the images
        # print("Starting deletion")
        # for image_file in image_files:
        #     image_filepath = f"{images_directory}/{image_file}"
        #     if os.path.exists(image_filepath):
        #         print(f"Deleting {image_filepath}")
        #         os.remove(image_filepath)


if __name__ == "__main__":
    
    appmode = os.environ['appmode']
    
    if appmode == "timelapse":
        create_timelapse()
    else:
        main()
