#!/usr/bin/env python

# python-gphoto2 - Python interface to libgphoto2
# http://github.com/jim-easterbrook/python-gphoto2
# Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

from __future__ import print_function

from datetime import datetime
import logging
import os
import sys

import gphoto2 as gp

def list_files(camera, context, path='/'):
    result = []
    gp_list = gp.check_result(gp.gp_list_new())
    # get files
    gp.check_result(
        gp.gp_camera_folder_list_files(camera, path, gp_list, context))
    for n in range(gp.gp_list_count(gp_list)):
        result.append(os.path.join(
            path, gp.check_result(gp.gp_list_get_name(gp_list, n))))
    # read folders
    folders = []
    gp.check_result(gp.gp_list_reset(gp_list))
    gp.check_result(
        gp.gp_camera_folder_list_folders(camera, path, gp_list, context))
    for n in range(gp.gp_list_count(gp_list)):
        folders.append(gp.check_result(gp.gp_list_get_name(gp_list, n)))
    gp.gp_list_unref(gp_list)
    # recurse over subfolders
    for name in folders:
        result.extend(list_files(camera, context, os.path.join(path, name)))
    return result

def get_file_info(camera, context, path):
    folder, name = os.path.split(path)
    info = gp.CameraFileInfo()
    gp.check_result(
        gp.gp_camera_file_get_info(camera, folder, name, info, context))
    return info

def main():
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    camera = gp.check_result(gp.gp_camera_new())
    context = gp.gp_context_new()
    gp.check_result(gp.gp_camera_init(camera, context))
    files = list_files(camera, context)
    if not files:
        print('No files found')
        return 1
    print('File list')
    print('=========')
    for path in files[:10]:
        print(path)
    print('...')
    for path in files[-10:]:
        print(path)
    info = get_file_info(camera, context, files[-1])
    print
    print('File info')
    print('=========')
    print('image dimensions:', info.file.width, info.file.height)
    print('image type:', info.file.type)
    print('file mtime:', datetime.fromtimestamp(info.file.mtime).isoformat(' '))
    gp.check_result(gp.gp_camera_exit(camera, context))
    gp.check_result(gp.gp_camera_unref(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
