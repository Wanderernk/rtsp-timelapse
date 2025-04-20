# RTSP Timelapse

Connects to an RTSP stream, takes a photo, and stitches it together to make a timelapse.
Then sends a the timelapse video to your favourite service [using Apprise](https://github.com/caronc/apprise).

## Hardware
- Raspberry Pi (any model will probably do) or x86 Linux/Windows system
- An IP camera or Recorder that supports RTSP

## Service description
Service consists of the following parts:

### Config file
Used for setting the RTSP stream details: IP and RTSP names, and Apprise services. 
Also RTSP names used for folder names.

### Recorder
Recorder is a service that takes a photo from the RTSP stream and saves it to a directory. It is used to create the timelapse.
The service is configured in the docker-compose.yml file. It should be started with `docker-compose up -d`

### Timelapse
The timelapse service makes a video from the images in the input directory for desired camera and time. By default it creates a timelapse for the previous week. After creating it send the video to the configured Apprise services.
For usage copy example.docker-compose-timelapse.yml to docker-compose-timelapse.yml. And run `docker-compose -f docker-compose-timelapse.yml up -d`

## Usage in docker

1. Copy example.config.py to config.py
2. Update config.py with your RTSP stream details and Apprise services
3. Copy example.docker-compose.yml to docker-compose.yml
4. Copy example.docker-compose-timelapse.yml to docker-compose-timelapse.yml
5. Run `docker-compose up -d` for build and run Recorder service
6. Run `docker-compose -f docker-compose-timelapse.yml up -d` for build and run Timelapse service
7. Add a cron job to run the Timelapse container service every week. For example:
```bash
45 8 1 * * docker start timelapse
```


## Development
- Create a python3 virtual environment and install the project's requirements:
```
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -r requirements.txt
```
- You will also need [ffmpeg](https://ffmpeg.org/) installed on your machine.  This can usually be
installed using a package manager.  For example:
```
$ sudo apt-get install ffmpeg
```
- Open config.py and enter the camera's
  - RTSP username
  - RTSP password
  - IP address
- Also in config.py, enter where you want your timelapse videos to be sent. See
[Apprise's github page](https://github.com/caronc/apprise) for examples. An
example for Telegram and Discord would look something like this:
```
# The list of services to notify
apprise_services = [
    "tgram://bottoken/ChatID",
    "discord://webhook_id/webhook_token",
]
```
- You should now be able to start the program:
```
(rtsp_timelapse) $ python main.py
```

# Creating the timelapses
The script is intended to be run regularly on a cronjob.  It will connect to the IP camera, take a photo 
and save the image to the **input** folder.

Once a week's worth of photos have been taken, the script will stitch the photos together using
[ffmpeg](https://ffmpeg.org/) and save the video to the **output** directory.  Once saved, it will send the videos to
the Apprise services set in config.py.  The images used to create the timelapse will then be
deleted.

Two copies of the timelapse will be created in the **output** directory.
- normal_timelapse - This contains timelapses at the default framerate - 24fps
- forced_fps - This contains timelapses at a framerate of 60fps

# ToDo
- [ ] merge two docker compose files into one
- [ ] set framerate setting to environment variable