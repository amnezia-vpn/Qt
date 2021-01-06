import argparse
import os
import shutil
import subprocess
import sys
import multiprocessing
import time
import psutil

# Set the minimum macOS target environment. Applies to prereqs and to BS code.
# If the min target changes, update CMakeLists.txt too.
if sys.platform == "darwin":
   os.environ['MACOSX_DEPLOYMENT_TARGET'] = '10.12'

sys.path.insert(0, 'build_scripts')

from settings               import Settings
from jom_settings           import JomSettings
from qt_settings            import QtSettings
from openssl_settings       import OpenSslSettings

def generate_project(qt_release, qt_version, build_mode, link_mode, build_production, hide_warnings, cmake_flags):
   project_settings = Settings(build_mode, link_mode)

   print('Build mode        : {} ( {} )'.format(project_settings.get_build_mode(), ('Production' if build_production else 'Development')))
   print('Build mode        : ' + project_settings.get_build_mode())
   print('Link mode         : ' + project_settings.get_link_mode())
   print('CMake generator   : ' + project_settings.get_cmake_generator())
   print('Download path     : ' + os.path.abspath(project_settings.get_downloads_dir()))
   print('Install dir       : ' + os.path.abspath(project_settings.get_common_build_dir()))

   required_3rdparty = []
   if project_settings._is_windows:
      required_3rdparty.append(JomSettings(project_settings))

   required_3rdparty.append(OpenSslSettings(project_settings))
   required_3rdparty.append(QtSettings(project_settings, qt_release, qt_version))

   for component in required_3rdparty:
      if not component.config_component():
         print('FAILED to build ' + component.get_package_name() + '. Cancel project generation')
         return 1

   print('3rd party components ready')
   return 0


if __name__ == '__main__':

   input_parser = argparse.ArgumentParser()
   input_parser.add_argument('qt_release',
                             action='store',
                             type=str,
                             help='Qt release: 5.12')
   input_parser.add_argument('qt_version',
                             action='store',
                             type=str,
                             help='Qt version: 5 (release + version = 5.12.5)')
   input_parser.add_argument('build_mode',
                             help='Build mode to be used by the project generator [ debug | release ]',
                             nargs='?',
                             action='store',
                             default='release',
                             choices=['debug', 'release'])
   input_parser.add_argument('-production',
                             help='Make production build',
                             action='store_true',
                             dest='build_production',
                             default=False)
   input_parser.add_argument('link_mode',
                             help='Linking library type used by the project generator [ static | shared ]',
                             nargs='?',
                             action='store',
                             default='static',
                             choices=['static', 'shared'])
   input_parser.add_argument('-hide-warnings',
                             help='Hide warnings in external sources',
                             action='store_true',
                             dest='hide_warnings',
                             default=False)
   input_parser.add_argument('-cmake-flags',
                             action='store',
                             type=str,
                             help='Additional CMake flags. Example: "-DCMAKE_CXX_COMPILER_LAUNCHER=ccache -DCMAKE_CXX_FLAGS=-fuse-ld=gold"')

   args = input_parser.parse_args()

   # Start foo as a process
   p = multiprocessing.Process(target=generate_project, name="generate_project", args=(args.qt_release, args.qt_version, args.build_mode, args.link_mode, args.build_production, args.hide_warnings, args.cmake_flags))
   p.start()

   # Wait a maximum of xx minutes. assume preinstall took less then 8 min
   p.join(1800)

   sys.exit(0)
