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

import logging
import sys

import gphoto2 as gp

def main():
    # use Python logging
    logging.basicConfig(
        format='%(levelname)s: %(name)s: %(message)s', level=logging.WARNING)
    gp.check_result(gp.use_python_logging())
    # open camera connection
    camera = gp.check_result(gp.gp_camera_new())
    context = gp.gp_context_new()
    gp.check_result(gp.gp_camera_init(camera, context))
    # get configuration tree
    config = gp.check_result(gp.gp_camera_get_config(camera, context))
    # find the date/time setting config item and set it
    sync_config = gp.check_result(
        gp.gp_widget_get_child_by_name(config, 'syncdatetime'))
    gp.check_result(gp.gp_widget_set_value_int(sync_config, 1))
    # apply the changed config
    gp.check_result(gp.gp_camera_set_config(camera, config, context))
    # free allocated data
    gp.check_result(gp.gp_widget_unref(config))
    gp.check_result(gp.gp_camera_exit(camera, context))
    gp.check_result(gp.gp_camera_unref(camera))
    return 0

if __name__ == "__main__":
    sys.exit(main())
