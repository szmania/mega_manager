
from argparse import ArgumentParser
from mega_manager import MegaManager
from os import path


HOME_DIRECTORY = path.expanduser("~\\")
MEGA_MANAGER_CONFIG_DIR = HOME_DIRECTORY + ".mega_manager"
MEGA_MANAGER_CONFIG_FILE_PATH = MEGA_MANAGER_CONFIG_DIR + "\\mega_manager.cfg"

def get_args():
    """
    Get arguments from command line, and returns them as dictionary.

    Returns:
        Dictionary: Dictionary of arguments for MEGA Manager.
    """

    parser = ArgumentParser(description='MEGA Manager is a MEGA cloud storage management and optimization application.')

    parser.add_argument('--compress', dest='compress_all', action='store_true', default=False,
                        help='If true, this will compress local image and video files.')

    parser.add_argument('--compress-images', dest='compress_images', action='store_true', default=False,
                        help='If true, this will compress local image files.')

    parser.add_argument('--compress-videos', dest='compress_videos', action='store_true', default=False,
                        help='If true, this will compress local video files.')

    parser.add_argument('--config', dest='config_path', default=MEGA_MANAGER_CONFIG_FILE_PATH,
                        help='Set MEGA Manager config file location. Default: "{}"'.format(MEGA_MANAGER_CONFIG_FILE_PATH))

    parser.add_argument('--download', dest='download', action='store_true', default=False,
                        help='If true, items will be downloaded from MEGA')

    parser.add_argument('--down-speed', dest='down_speed', type=int, default=None,
                        help='Total download speed limit in kilobytes.')

    parser.add_argument('--log', dest='log_level', default='INFO',
                        help='Set logging level')

    parser.add_argument('--output-data', dest='output_profile_data', action='store_true', default=False,
                        help='If true, this will output all profile data to standard output.')

    parser.add_argument('--remove-oldest-file-version', dest='remove_oldest_file_version', action='store_true', default=False,
                        help='If true, this will remove outdated files locally or remotely that are older than their '
                             'local/remote counterpart (syncing action).')

    parser.add_argument('--remove-remote', dest='remove_remote', action='store_true', default=False,
                        help='If true, this will allow for remote files to be removed if no corresponding '
                             'local file exists.')

    parser.add_argument('--sync', dest='sync', action='store_true', default=False,
                        help='If true, local and remote files for accoutns will be synced. Equivalent to '
                             'using arguments "--download", "--removeLocal", "--removeRemote" and "--upload" '
                             'all at once.')

    parser.add_argument('--upload', dest='upload', action='store_true', default=False,
                        help='If true, items will be uploaded to MEGA')

    parser.add_argument('--up-speed', dest='up_speed', type=int, default=None,
                        help='Total upload speed limit in kilobytes.')

    args = parser.parse_args()
    return args.__dict__


def main():

    kwargs = get_args()

    megaObj = MegaManager(**kwargs)

    megaObj.run()


if __name__ == "__main__":

    main()