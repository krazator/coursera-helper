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
    no_class_name_flags = ['list_courses', 'version']
    return not any(getattr(args, flag) for flag in no_class_name_flags)


def parse_args(args=None):
    parse_kwargs = {
        "description": 'Download Coursera.org lecture material and resources.'
    }

    conf_file_path = os.path.join(os.getcwd(), LOCAL_CONF_FILE_NAME)
    if os.path.isfile(conf_file_path):
        parse_kwargs["default_config_files"] = [conf_file_path]

    parser = argparse.ArgParser(**parse_kwargs)

    group_basic = parser.add_argument_group('Basic options')

    group_basic.add_argument('class_names', action='store', nargs='*')
    group_basic.add_argument('-u', '--username', dest='username', default=None,
                             help='username (email) that you use to log in to Coursera')
    group_basic.add_argument('-p', '--password', dest='password', default=None,
                             help='Coursera password')
    group_basic.add_argument('--jobs', dest='jobs', default=1, type=int)
    group_basic.add_argument('--download-delay', dest='download_delay', default=60, type=int)
    group_basic.add_argument('-b', '--preview', dest='preview', action='store_true', default=False)
    group_basic.add_argument('--path', dest='path', default='')

    group_basic.add_argument(
        '-sl', '--subtitle-language', dest='subtitle_language', default='all',
        help='Choose subtitle and transcript languages. Use "all" for all available languages.'
    )

    group_material = parser.add_argument_group('Selection of material to download')

    group_material.add_argument('--specialization', dest='specialization', action='store_true', default=False)
    group_material.add_argument('--only-syllabus', dest='only_syllabus', action='store_true', default=False)
    group_material.add_argument('--download-quizzes', dest='download_quizzes', action='store_true', default=False)
    group_material.add_argument(
        '--download-notebooks',
        dest='download_notebooks',
        action='store_true',
        default=False,
        help='download Python Jupyter notebooks. (Default: False)'
    )
    group_material.add_argument('--about', dest='about', action='store_true', default=False)
    group_material.add_argument('-f', '--formats', dest='file_formats', default='all')
    group_material.add_argument('--ignore-formats', dest='ignore_formats', default=None)
    group_material.add_argument('-sf', '--section_filter', dest='section_filter', default=None)
    group_material.add_argument('-lf', '--lecture_filter', dest='lecture_filter', default=None)
    group_material.add_argument('-rf', '--resource_filter', dest='resource_filter', default=None)
    group_material.add_argument('--video-resolution', dest='video_resolution', default='540p')
    group_material.add_argument('--disable-url-skipping', dest='disable_url_skipping', action='store_true', default=False)

    group_external_dl = parser.add_argument_group('External downloaders')
    group_external_dl.add_argument('--wget', dest='wget', nargs='?', const='wget', default=None)
    group_external_dl.add_argument('--curl', dest='curl', nargs='?', const='curl', default=None)
    group_external_dl.add_argument('--aria2', dest='aria2', nargs='?', const='aria2c', default=None)
    group_external_dl.add_argument('--axel', dest='axel', nargs='?', const='axel', default=None)
    group_external_dl.add_argument('--downloader-arguments', dest='downloader_arguments', default='')

    parser.add_argument('--list-courses', dest='list_courses', action='store_true', default=False)
    parser.add_argument('--resume', dest='resume', action='store_true', default=False)
    parser.add_argument('-o', '--overwrite', dest='overwrite', action='store_true', default=False)
    parser.add_argument('--verbose-dirs', dest='verbose_dirs', action='store_true', default=False)
    parser.add_argument('--quiet', dest='quiet', action='store_true', default=False)
    parser.add_argument('-r', '--reverse', dest='reverse', action='store_true', default=False)
    parser.add_argument('--combined-section-lectures-nums', dest='combined_section_lectures_nums', action='store_true', default=False)
    parser.add_argument('--unrestricted-filenames', dest='unrestricted_filenames', action='store_true', default=False)

    group_adv_auth = parser.add_argument_group('Advanced authentication options')
    group_adv_auth.add_argument('-ca', '--cauth', dest='cookies_cauth', default=None)
    group_adv_auth.add_argument('-c', '--cookies_file', dest='cookies_file', default=None)
    group_adv_auth.add_argument('-n', '--netrc', dest='netrc', nargs='?', const=True, default=False)
    group_adv_auth.add_argument('-k', '--keyring', dest='use_keyring', action='store_true', default=False)
    group_adv_auth.add_argument('--clear-cache', dest='clear_cache', action='store_true', default=False)

    group_adv_misc = parser.add_argument_group('Advanced miscellaneous options')
    group_adv_misc.add_argument('--hook', dest='hooks', action='append', default=[])
    group_adv_misc.add_argument('-pl', '--playlist', dest='playlist', action='store_true', default=False)
    group_adv_misc.add_argument('--mathjax-cdn', dest='mathjax_cdn_url', default='https://cdn.mathjax.org/mathjax/latest/MathJax.js')

    group_debug = parser.add_argument_group('Debugging options')
    group_debug.add_argument('--skip-download', dest='skip_download', action='store_true', default=False)
    group_debug.add_argument('--debug', dest='debug', action='store_true', default=False)
    group_debug.add_argument('--cache-syllabus', dest='cache_syllabus', action='store_true', default=False)
    group_debug.add_argument('--version', dest='version', action='store_true', default=False)
    group_debug.add_argument('-l', '--process_local_page', dest='local_page')

    parser.add_argument(
        '--browser-cookie',
        dest='browser_cookie',
        action='store_true',
        default=False,
        help='extract the CAUTH value from browser cookies (default: False)')

    parser.add_argument(
        '--headless',
        dest='headless',
        action='store_true',
        default=False,
        help='run the browser in headless mode (default: False)')

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
        logging.warning('--keyring and --password cannot be specified together')
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
                username=args.username,
                password=args.password,
                netrc=args.netrc,
                use_keyring=args.use_keyring)
        except CredentialsError as e:
            logging.error(e)
            sys.exit(1)

    return args
