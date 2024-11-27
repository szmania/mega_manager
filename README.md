# MEGA Manager
Cloud syncing manager for multiple <a href="https://mega.nz/">MEGA</a> cloud storage accounts with syncing, data gathering, compresssion and optimization capabilities. 

MEGA Manager allows MEGA users to manage and maintain multiple MEGA accounts all in one place! MEGA Manager is the only app that allows syncing capabilities on multiple MEGA accounts. Included in MEGA Manager are in-depth syncing capabilities, file optimization and compression, remote and local account data output, a Command Line Interface, and the ability to sync multiple remote locations to multiple local locations in one account.

* Allows users to manage multiple MEGA accounts all in one place
* Syncing capabilites that allows for syncing several remote and local file locations in the same account
* Optimization and compression capabilities for video and image file formats
* Output remote and local file data for each account
* Command Line Interface (CLI) for all the above features

#### A little about MEGA.nz...
##### <a href="https://mega.nz/">https://mega.nz/</a>
MEGA makes secure cloud storage simple. Create an account and get 50 GB free on MEGA's end-to-end encrypted cloud collaboration platform today!

<img src="http://cdn2.ubergizmo.com/wp-content/uploads/2013/11/mega-launch.png" alt="MEGA Cloud Sync" height="400">


## Usage
### Arguments
`--compress`

Compresses all images AND video files in local account locations.

`--compress-images`

Compresses all images in local account locations.

`--compress-videos`

Compresses all videos in local account locations.

`--config <path>`

Set MEGA Manager config file location. Default: "\<home\>/.mega_manager/mega_manager.cfg".

`--download`

Download from MEGA account remote locations to corresponding local locations.

`--download-speed <int>`

Set total download speed limit in Kb.

`--log <loglevel>`

Set log level. ie: "INFO", "WARN", "DEBUG", etc... Default: "INFO".

`--profile-output-data`

This will output all profile/account data to standard output.

`--remove-oldest-file-version`

This will remove outdated files locally or remotely that are older than their local/remote counterpart (syncing action).

`--remove-remote`

If set remote files that have no corresponding local file will be removed.

`--sync`

If true, local and remote files for accounts will be synced. Equivalent to using arguments "--download", "--remove_local",
"--remote-outdated", "--remove_remote" and "--upload" all at once.

`--upload`

If set files will be uploaded to MEGA account.

`--upload-speed <int>`

Set total upload speed limit in Kb.


### Examples

Calling the package directly will suffice. Otherwise one could call "megamanger\__main__.py"

`megamanager --upload --up-speed 500`

Upload files AND limit total upload speed to 500kb.

`megamanager\__main__.py --sync --down-speed 750`

Sync files AND limit total download speed to 750kb.

`megamanager --remove-oldest-file-version --config "dir\megamanager.cfg"`

Set config file to be "dir\mega_manger.cfg" AND remove outdated local and remote files



### MEGA Manager Config File Format
(by default lives in \<home\>/.mega_manager/mega_manger.cfg, unless specified otherwise)
Command line arguments override corresponding config values. (ie: --compress via cli will override "COMPRESS_ALL=False" in config file) 

```
[ACTIONS]
COMPRESS_ALL=True
COMPRESS_IMAGES=False
COMPRESS_VIDEOS=False
DOWNLOAD=False
UPLOAD=False
SYNC=True
LOCAL_IS_TRUTH=True

[PROPERTIES]
LOG_LEVEL="DEBUG"
LOG_RETENTION="midnight"
LOG_RETNETION_BACKUP_COUNT=5
MEGA_MANAGER_CONFIG_DIR_PATH="{HOME_DIRECTORY}{sep}.mega_manager"
MEGA_MANAGER_LOG_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}{sep}logs{sep}mega_manager_log.log"
MEGA_MANAGER_CONFIG_DIR_DATA_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}{sep}data"
MEGA_MANAGER_STDOUT_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}{sep}logs{sep}mega_stdout.log"
MEGA_MANAGER_STDERR_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}{sep}logs{sep}mega_stderr.log"
MEGA_MANAGER_OUTPUT_PROFILE_DATA_PATH=""
SLEEP_TIME_BETWEEN_RUNS_SECONDS=300
REMOVE_OLDEST_FILE_VERSION=False
PROCESS_SET_PRIORITY_TIMEOUT=60

[IMAGE_COMPRESSION]
COMPRESSED_IMAGES_FILE_PATH ="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}{sep}compressed_images.npy"
UNABLE_TO_COMPRESS_IMAGES_FILE_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}{sep}unable_to_compress_images.npy"
COMPRESSION_IMAGE_EXTENSIONS=["jpg","jpeg","png"]
IMAGE_TEMP_FILE_EXTENSIONS=["compressimages-backup", "unoptimized", "tmp"]
COMPRESSION_JPEG_QUALITY_PERCENTAGE=60

[VIDEO_COMPRESSION]
COMPRESSED_VIDEOS_FILE_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}{sep}compressed_videos.npy"
UNABLE_TO_COMPRESS_VIDEOS_FILE_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}{sep}unable_to_compress_videos.npy"
COMPRESSION_VIDEO_EXTENSIONS=["avi","flv","m4v","mkv","mp4","mpeg","mpg","wmv"]
COMPRESSION_FFMPEG_VIDEO_PRESET="slow"
FFMPEG_PROCESS_PRIORITY_CLASS="HIGH_PRIORITY_CLASS"
FFMPEG_LOG_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}{sep}logs{sep}ffmpeg.log"
FFMPEG_THREADS=4

[REMOTE]
REMOVED_REMOTE_FILES_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}{sep}removed_remote_files.npy"

[MEGATOOLS]
MEGATOOLS_PROCESS_PRIORITY_CLASS="HIGH_PRIORITY_CLASS"
MEGATOOLS_LOG_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}{sep}logs{sep}mega_tools.log"

[MEGA]
MEGA_DOWNLOAD_SPEED=200
MEGA_UPLOAD_SPEED=200

[PROFILE_0]
profile_name=Pictures - email@email.com
username=email@email.com
password=mypassword
local_path_0=/mnt/sda1/pictures
remote_path_0=/Root/pictures

[PROFILE_1]
profile_name=Videos & Games - email2@email.com
username=email2@email.com
password=mypassword2
local_path_0=/mnt/sda1/videos
remote_path_0=/Root/videos
local_path_1=/mnt/sda1/games
remote_path_1=/Root/games
```

Paths are now operating system agnostic (eg: can process both `\\` and `/`).
Example:

```
[ACTIONS]
COMPRESS_ALL=True
COMPRESS_IMAGES=False
COMPRESS_VIDEOS=False
DOWNLOAD=False
UPLOAD=False
SYNC=True
LOCAL_IS_TRUTH=True

[PROPERTIES]
LOG_LEVEL="DEBUG"
LOG_RETENTION="midnight"
LOG_RETNETION_BACKUP_COUNT=5
MEGA_MANAGER_CONFIG_DIR_PATH="{HOME_DIRECTORY}/.mega_manager"
MEGA_MANAGER_LOG_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}/logs/mega_manager_log.log"
MEGA_MANAGER_CONFIG_DIR_DATA_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}/data"
MEGA_MANAGER_STDOUT_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}/logs/mega_stdout.log"
MEGA_MANAGER_STDERR_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}/logs/mega_stderr.log"
MEGA_MANAGER_OUTPUT_PROFILE_DATA_PATH=""
SLEEP_TIME_BETWEEN_RUNS_SECONDS=300
REMOVE_OLDEST_FILE_VERSION=False
PROCESS_SET_PRIORITY_TIMEOUT=60

[IMAGE_COMPRESSION]
COMPRESSED_IMAGES_FILE_PATH ="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}/compressed_images.npy"
UNABLE_TO_COMPRESS_IMAGES_FILE_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}/unable_to_compress_images.npy"
COMPRESSION_IMAGE_EXTENSIONS=["jpg","jpeg","png"]
IMAGE_TEMP_FILE_EXTENSIONS=["compressimages-backup", "unoptimized", "tmp"]
COMPRESSION_JPEG_QUALITY_PERCENTAGE=60

[VIDEO_COMPRESSION]
COMPRESSED_VIDEOS_FILE_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}/compressed_videos.npy"
UNABLE_TO_COMPRESS_VIDEOS_FILE_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}/unable_to_compress_videos.npy"
COMPRESSION_VIDEO_EXTENSIONS=["avi","flv","m4v","mkv","mp4","mpeg","mpg","wmv"]
COMPRESSION_FFMPEG_VIDEO_PRESET="slow"
FFMPEG_PROCESS_PRIORITY_CLASS="HIGH_PRIORITY_CLASS"
FFMPEG_LOG_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}/logs/ffmpeg.log"
FFMPEG_THREADS=4

[REMOTE]
REMOVED_REMOTE_FILES_PATH="{MEGA_MANAGER_CONFIG_DIR_DATA_PATH}/removed_remote_files.npy"

[MEGATOOLS]
MEGATOOLS_PROCESS_PRIORITY_CLASS="HIGH_PRIORITY_CLASS"
MEGATOOLS_LOG_PATH="{MEGA_MANAGER_CONFIG_DIR_PATH}/logs/mega_tools.log"

[MEGA]
MEGA_DOWNLOAD_SPEED=200
MEGA_UPLOAD_SPEED=200

[PROFILE_0]
profile_name=Pictures - email@email.com
username=email@email.com
password=mypassword
local_path_0=/mnt/sda1/pictures
remote_path_0=/Root/pictures

[PROFILE_1]
profile_name=Videos & Games - email2@email.com
username=email2@email.com
password=mypassword2
local_path_0=/mnt/sda1/videos
remote_path_0=/Root/videos
local_path_1=/mnt/sda1/games
remote_path_1=/Root/games
```



