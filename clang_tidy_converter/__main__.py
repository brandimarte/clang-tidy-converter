#!/usr/bin/env python3

from .formatter import CodeClimateFormatter, HTMLReportFormatter
from .parser import ClangTidyParser
from argparse import ArgumentParser
import os
import sys


def create_argparser():
    p = ArgumentParser(description='Reads Clang-Tidy output from STDIN and prints it in selected format to STDOUT.')
    p.add_argument('-r', '--project_root', default='', help='output file paths relative to PROJECT_ROOT')
    p.add_argument('-f', '--log_file', default='', help='output log file from clang-tidy call')

    sub = p.add_subparsers(title="output format", dest='output_format', metavar="FORMAT", required=True)

    cc = sub.add_parser("cc", help="Code Climate JSON")
    cc.add_argument(
        '-l', '--use_location_lines', action='store_const', const=True, default=False,
        help='use line-based locations instead of position-based as defined in Locations section of Code Climate specification')
    cc.add_argument('-j', '--as_json_array', action='store_const', const=True, default=False,
                    help='output as JSON array instead of ending each issue with \\0')

    html = sub.add_parser("html", help="HTML report")
    html.add_argument('-s', '--software_name', default='', help='software name to display in generated report')
    return p


def main(args):
    parser = ClangTidyParser()
    if args.log_file:
        with open(args.log_file, 'r', encoding='ascii') as f:
            messages = parser.parse(f.readlines())
    else:
        messages = parser.parse(sys.stdin.readlines())

    if len(args.project_root) > 0:
       convert_paths_to_relative(messages, args.project_root)

    if args.output_format == 'cc':
        formatter = CodeClimateFormatter()
    else:
        formatter = HTMLReportFormatter()

    print(formatter.format(messages, args))


def convert_paths_to_relative(messages, root_dir):
    for message in messages:
        message.filepath = os.path.relpath(message.filepath, root_dir)
        convert_paths_to_relative(message.children, root_dir)


if __name__ == "__main__":
    main(create_argparser().parse_args())
