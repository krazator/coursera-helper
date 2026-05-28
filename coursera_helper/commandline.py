"""
This module contains code that is related to command-line argument
handling. The primary candidate is argument parser.
"""

import os
import sys
import logging
import configargparse as argparse

from coursera_helper import __version__

from .credentials import get_credentials, CredentialsError, keyring
from .utils import decode_input

LOCAL_CONF_FILE_NAME = 'coursera-dl.conf'


def class_name_arg_required(args):
    """
    Evaluates whether class_name arg is required.

    @param args: Command-line arguments.
    @type args: namedtuple
    """
    no_class_name_flags = ['list_courses', 'version']
    return not any(
        getattr(args, flag)
        for flag in no_class_name_flags
    )


def parse_args(args=None):
    """
    Parse the arguments/options passed to the program on the command line.
    """

    parse_kwargs = {
        "description": 'Download Coursera.org lecture material and resources.'
    }

    conf_file_path = os.path.join(os.getcwd(), LOCAL_CONF_FILE_NAME)
    if os.path.isfile(conf_file_path):
        parse_kwargs["default_config_files"] = [conf_file_path]
    parser = argparse.ArgParser(**parse_kwargs)

    # Basic options
    group_basic = parser.add_argument_group('Basic options')

    group_basic.add_argument(
        'class_names',
        action='store',
        nargs='*',
        help='name(s) of the class(es) (e.g. "ml-005")')

    group_basic.add_argument(
        '-u',
        '--username',
        dest='username',
        action='store',
        default=None,
        help='username (email) that you use to log in to Coursera')

    group_basic.add_argument(
        '-p',
        '--password',
        dest='password',
        action='store',
        default=None,
        help='Coursera password')

    group_basic.add_argument(
        '--jobs',
        dest='jobs',
        action='store',
        default=1,
        type=int,
        help='number of parallel jobs to use for '
        'downloading resources. (Default: 1)')

    group_basic.add_argument(
        '--download-delay',
        dest='download_delay',
        action='store',
        default=60,
        type=int,
        help='number of seconds to wait before downloading '
        'the next course. (Default: 60)')

    group_basic.add_argument(
        '-b',
        '--preview',
        dest='preview',
        action='store_true',
        default=False,
        help='get videos from preview pages. (Default: False)')

    group_basic.add_argument(
        '--path',
        dest='path',
        action='store',
        default='',
        help='path where files should be saved. (Default: current directory)')

    group_basic.add_argument(
        '-sl',
        '--subtitle-language',
        dest='subtitle_language',
        action='store',
        default='all',
        help='Choose subtitle and transcript languages. '
        '(Default: all) Use the special value "all" to download all available languages. '
        'To download multiple languages, use commas without spaces, '
        'for example: "en,zh-CN". '
        'To specify fallback languages, use "|<lang>", '
        'for example: "en|fr,zh-CN|zh-TW|de". '
        'Wrap the parameter in quotes when using "|".'
    )

    group_material = parser.add_argument_group(
        'Selection of material to download')

    group_material.add_argument(
        '--specialization',
        dest='specialization',
        action='store_true',
        default=False,
        help='treat given class names as specialization names and try to '
        'download their courses, if available. Note that there are name '
        'clashes, e.g. "machine-learning" is both a course and a '
        'specialization (Default: False)')

    group_material.add_argument(
        '--only-syllabus',
        dest='only_syllabus',
        action='store_true',
        default=False,
        help='download only the syllabus and skip course content. '
        '(Default: False)')

    group_material.add_argument(
        '--download-quizzes',
        dest='download_quizzes',
        action='store_true',
        default=False,
        help='download quiz and exam questions. (Default: False)')

    group_material.add_argument(
        '--download-notebooks',
        dest='download_notebooks',
        action='store_true',
        default=False,
        help='download Python Jupyter notebooks. (Default: False)')

    group_material.add_argument(
        '--about',
        dest='about',
        action='store_true',
        default=False,
        help='download "about" metadata. (Default: False)')

    group_material.add_argument(
        '-f',
        '--formats',
        dest='file_formats',
        action='store',
        default='all',
        help='file format extensions to download, '
        'for example: "mp4 pdf" '
        '(default: special value "all")')

    group_material.add_argument(
        '--ignore-formats',
        dest='ignore_formats',
        action='store',
        default=None,
        help='file format extensions of resources to ignore '
        '(default: None)')

    group_material.add_argument(
        '-sf',
        '--section_filter',
        dest='section_filter',
        action='store',
        default=None,
        help='only download sections matching this regex '
        '(default: disabled)')

    group_material.add_argument(
        '-lf',
        '--lecture_filter',
        dest='lecture_filter',
        action='store',
        default=None,
        help='only download lectures matching this regex '
        '(default: disabled)')

    group_material.add_argument(
        '-rf',
        '--resource_filter',
        dest='resource_filter',
        action='store',
        default=None,
        help='only download resources matching this regex '
        '(default: disabled)')

    group_material.add_argument(
        '--video-resolution',
        dest='video_resolution',
        action='store',
        default='540p',
        help='video resolution to download (default: 540p); '
        'only valid for on-demand courses; '
        'allowed values: 360p, 540p, 720p')

    group_material.add_argument(
        '--disable-url-skipping',
        dest='disable_url_skipping',
        action='store_true',
        default=False,
        help='disable URL skipping so all URLs are downloaded '
        '(default: False)')

    parser.add_argument(
        '--browser-cookie',
        dest='browser_cookie',
        action='store_true',
        default=False,
        help='extract the CAUTH value from browser cookies '
        '(default: False)')

    parser.add_argument(
        '--headless',
        dest='headless',
        action='store_true',
        default=False,
        help='run the browser in headless mode '
        '(default: False)')

    args = parser.parse_args(args)

    if args.debug:
        logging.basicConfig(level=logging.DEBUG,
                            format='%(name)s[%(funcName)s] %(message)s')
    elif args.quiet:
        logging.basicConfig(level=logging.ERROR,
                            format='%(name)s: %(message)s')
    else:
        logging.basicConfig(level=logging.INFO,
                            format='%(message)s')

    if class_name_arg_required(args) and not args.class_names:
        parser.print_usage()
        logging.error('You must supply at least one class name')
        sys.exit(1)

    if args.version:
        print(__version__)
        sys.exit(0)

    args.downloader_arguments = args.downloader_arguments.split()
    args.file_formats = args.file_formats.split()

    args.path = decode_input(args.path)

    if args.use_keyring and args.password:
        logging.warning(
            '--keyring and --password cannot be specified together')
        args.use_keyring = False

    if args.use_keyring and not keyring:
        logging.warning('The python module `keyring` not found.')
        args.use_keyring = False

    if args.cookies_file and not os.path.exists(args.cookies_file):
        logging.error('Cookies file not found: %s', args.cookies_file)
        sys.exit(1)

    if not args.cookies_file and not args.cookies_cauth and not args.browser_cookie:
        try:
            args.username, args.password = get_credentials(
                username=args.username, password=args.password,
                netrc=args.netrc, use_keyring=args.use_keyring)
        except CredentialsError as e:
            logging.error(e)
            sys.exit(1)

    return args
