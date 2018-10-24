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

Set MEGA Manager config file location. Default: "megamanager/megaManager.cfg".

`--download`

Download from MEGA account remote locations to corresponding local locations.

`--down-speed <int>`

Set total download speed limit in Kb.

`--log <loglevel>`

Set log level. ie: "INFO", "WARN", "DEBUG", etc... Default: "INFO".

`--output-data`

This will output all profile/account data to standard output.

`--remove-outdated`

Remove outdated local and remote files.

`--remove-remote`

If set remote files that have no corresponding local file will be removed.

`--sync`

If true, local and remote files for accoutns will be synced. Equivalent to using arguments "--download", "--remove_local",
"--remote-outdated", "--remove_remote" and "--upload" all at once.

`--upload`

If set files will be uploaded to MEGA account.

`--up-speed <int>`

Set total upload speed limit in Kb.


### Examples

Calling the package directly will suffice. Otherwise one could call "megamanger\__main__.py"

`megamanager --upload --up-speed 500`

Upload files AND limit total upload speed to 500kb.

`megamanager\__main__.py --sync --down-speed 750`

Sync files AND limit total download speed to 750kb.

`megamanager --remote-outdated --config "dir\megamanager.cfg"`

Set config file to be "dir\megamanger.cfg" AND remove outdated local and remote files





