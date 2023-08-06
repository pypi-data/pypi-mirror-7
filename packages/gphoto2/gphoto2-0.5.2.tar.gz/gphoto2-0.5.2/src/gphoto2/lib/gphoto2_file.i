// python-gphoto2 - Python interface to libgphoto2
// http://github.com/jim-easterbrook/python-gphoto2
// Copyright (C) 2014  Jim Easterbrook  jim@jim-easterbrook.me.uk
//
// This program is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.
//
// This program is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.
//
// You should have received a copy of the GNU General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.

%module(package="gphoto2.lib") gphoto2_file

%{
#include "gphoto2/gphoto2.h"
%}

%feature("autodoc", "2");

%include "typemaps.i"

%include "macros.i"

// gp_file_new() returns a pointer in an output parameter
%typemap(in, numinputs=0) CameraFile ** (CameraFile *temp) {
  $1 = &temp;
}
%typemap(argout) CameraFile ** {
  RESULT_APPEND(
    SWIG_NewPointerObj(*$1, SWIGTYPE_p__CameraFile, SWIG_POINTER_NEW))
}

// Mark gp_file_unref as destructor and add default destructor
%delobject gp_file_unref;
struct _CameraFile {};
%extend _CameraFile {
  ~_CameraFile() {
    gp_file_unref($self);
  }
};
%ignore _CameraFile;

// These structures are private
%ignore _CameraFileHandler;

%include "gphoto2/gphoto2-file.h"
