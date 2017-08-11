
from argparse import ArgumentParser
from megamanager import MegaManager

def get_args():
    """
    Get arguments from command line, and returns them as dictionary.

    Returns:
        Dictionary: Dictionary of arguments for MEGA Manager.
    """

    parser = ArgumentParser(description='MEGA Manager is a MEGA cloud storage management and optimization application.')

    parser.add_argument('--download', dest='download', action='store_true', default=False,
                        help='If true, items will be downloaded from MEGA')

    parser.add_argument('--upload', dest='upload', action='store_true', default=False,
                        help='If true, items will be uploaded to MEGA')

    parser.add_argument('--removeRemote', dest='removeRemote', action='store_true', default=False,
                        help='If true, this will allow for remote files to be removed.')

    parser.add_argument('--removeIncomplete', dest='removeIncomplete', action='store_true', default=False,
                        help='If true, this will allow for local downloaded files that are incomplete to be removed.')

    parser.add_argument('--compressAll', dest='compressAll', action='store_true', default=False,
                        help='If true, this will compressAll local image and video files.')

    parser.add_argument('--compressImages', dest='compressImages', action='store_true', default=False,
                        help='If true, this will compressAll local image files.')

    parser.add_argument('--compressVideos', dest='compressVideos', action='store_true', default=False,
                        help='If true, this will __compressAll local video files.')

    parser.add_argument('--downSpeed', dest='downSpeed', type=int, default=None,
                        help='Total download speed limit.')

    parser.add_argument('--upSpeed', dest='upSpeed', type=int, default=None,
                        help='Total upload speed limit.')

    parser.add_argument('--log', dest='logLevel', default='INFO',
                        help='Set logging level')

    args = parser.parse_args()
    return args.__dict__


def main():

    kwargs = get_args()

    megaObj = MegaManager(**kwargs)

    megaObj.run()


if __name__ == "__main__":

    main()