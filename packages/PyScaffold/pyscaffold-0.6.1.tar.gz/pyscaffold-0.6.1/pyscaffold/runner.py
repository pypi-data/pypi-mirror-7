# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import sys
import os.path
import argparse

import pyscaffold
from . import structure
from . import repo
from . import info
from . import utils

__author__ = "Florian Wilhelm"
__copyright__ = "Blue Yonder"
__license__ = "new BSD"


def parse_args(args):
    parser = argparse.ArgumentParser(
        description="PyScaffold is a tool for easily putting up the scaffold "
                    "of a Python project.")
    parser.add_argument(
        dest="project",
        help="project name",
        metavar="PROJECT")
    parser.add_argument(
        "-p",
        "--package",
        dest="package",
        required=False,
        default=None,
        help="package name (default: project name)",
        metavar="NAME")
    parser.add_argument(
        "-d",
        "--description",
        dest="description",
        required=False,
        default=None,
        help="package description (default: '')",
        metavar="TEXT")
    parser.add_argument(
        "-u",
        "--url",
        dest="url",
        required=False,
        default=None,
        help="package url (default: '')",
        metavar="URL")
    license_choices = ["new-bsd"]
    parser.add_argument(
        "-l",
        "--license",
        dest="license",
        choices=license_choices,
        required=False,
        default=None,
        help="package license from {choices} (default: {default})".format(
            choices=str(license_choices), default=license_choices[0]),
        metavar="LICENSE")
    parser.add_argument(
        "--update",
        dest="update",
        action="store_true",
        default=False,
        help="update an existing project")
    parser.add_argument(
        "--with-junit-xml",
        dest="junit_xml",
        action="store_true",
        default=None,
        help="generate JUnit xml report")
    parser.add_argument(
        "--with-coverage-xml",
        dest="coverage_xml",
        action="store_true",
        default=None,
        help="generate coverage xml report")
    parser.add_argument(
        "--with-coverage-html",
        dest="coverage_html",
        action="store_true",
        default=None,
        help="generate coverage html report")
    version = pyscaffold.__version__
    parser.add_argument('-v',
                        '--version',
                        action='version',
                        version='PyScaffold {ver}'.format(ver=version))
    opts = parser.parse_args(args)
    license_mapping = {None: None,
                       "new-bsd": "new BSD"}
    opts.license = license_mapping[opts.license]
    if opts.package is None:
        opts.package = utils.make_valid_identifier(opts.project)
    # Strip slash when added accidentally during update
    opts.project = opts.project.rstrip("/")
    return opts


def main(args):
    args = parse_args(args)
    if not info.git_is_installed():
        raise RuntimeError("Make sure git is installed and working.")
    if os.path.exists(args.project) and not args.update:
        raise RuntimeError(
            "Directory {dir} already exists! Use --update to overwrite an "
            "existing project.".format(dir=args.project))
    if args.update:
        try:
            args = info.project(args)
        except (IOError, AttributeError):
            raise RuntimeError("Could not update {project}. Was it generated "
                               "with PyScaffold?".format(project=args.project))
    proj_struct = structure.make_structure(args)
    structure.create_structure(proj_struct, update=args.update)
    if not args.update:
        repo.init_commit_repo(args.project, proj_struct)


@utils.exceptions2exit([RuntimeError])
def run():
    """
    Entry point for setup.py
    """
    main(sys.argv[1:])


if __name__ == '__main__':
    main(sys.argv[1:])
