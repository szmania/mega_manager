# MEGA Manager
Cloud syncing manager for multiple <a href="https://mega.nz/">MEGA</a> cloud storage accounts with syncing, data gathering, compresssion and optimization capabilities. 

MEGA Manager allows MEGA users to manage and maintain multiple MEGA accounts all at one place! MEGA Manager is the only app that allows syncing capabilities on multiple MEGA accounts. Included in MEGA Manager are in-depth syncing capabilities, file optimization and compression, remote and local account data output, Command Line Interface, and the ability to sync multiple remote locations to local locations in the same account.

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
`--compressAll`

Compresses all images AND video files in local account locations.

`--compressImages`

Compresses all images in local account locations.

`--compressVideos`

Compresses all videos in local account locations.

`--configPath <path>`

Set MEGA Manager config file location. Default: "megamanager/megaManager.cfg".

`--download`

Download from MEGA account remote locations to corresponding local locations.

`--downSpeed <int>`

Set total download speed limit in Kb.

`--log <loglevel>`

Set log level. ie: "INFO", "WARN", "DEBUG", etc... Default: "INFO".

`--removeIncomplete`

Remove incomplete local files that were not downloaded completely.

`--removeRemote`

If set remote files that have no corresponding local file will be removed.

`--sync`

If true, local and remote files for accoutns will be synced. Equivalent to using arguments "--download", "--removeLocal", "--removeRemote" and "--upload" all at once.

`--upload`

If set files will be uploaded to MEGA account.

`--upSpeed <int>`

Set total upload speed limit in Kb.


## Examples





