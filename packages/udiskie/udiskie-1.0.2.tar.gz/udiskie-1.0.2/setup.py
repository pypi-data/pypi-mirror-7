# encoding: utf-8
from setuptools import setup
from setuptools.command.install import install
from subprocess import call
import sys
import logging
from os import path

import udiskie

# check availability of runtime dependencies
def check_dependency(package):
    """Issue a warning if the package is not available."""
    try:
        __import__(package)
    except ImportError:
        logging.warn("\n\t".join(["Missing runtime dependencies:",
                                  str(sys.exc_info()[1])]))
    except RuntimeError:
        logging.warn("\n\t".join(["Bad runtime dependency:",
                                  str(sys.exc_info()[1])]))

check_dependency('gi.repository.DBus')
check_dependency('gi.repository.GLib')
check_dependency('gi.repository.Gtk')
check_dependency('gi.repository.Notify')


# read long_description from README.rst
long_description = None
try:
    long_description = open('README.rst').read()
    long_description += '\n' + open('CHANGES.rst').read()
except IOError:
    pass


theme_base = path.join('share', 'icons', 'hicolor')
icon_names = ['mount', 'unmount', 'lock', 'unlock', 'eject', 'detach']

class custom_install(install):
    def run(self):
        install.run(self)
        try:
            # ignore failures since the tray icon is an optional component:
            call(['gtk-update-icon-cache', theme_base])
        except OSError:
            logging.warn(sys.exc_info()[1])

setup(
    name='udiskie',
    version=udiskie.__version__,
    description='Removable disk automounter for udisks',
    long_description=long_description,
    author='Byron Clark',
    author_email='byron@theclarkfamily.name',
    maintainer='Thomas Gläßle',
    maintainer_email='t_glaessle@gmx.de',
    url='https://github.com/coldfix/udiskie',
    license='MIT',
    cmdclass={'install': custom_install},
    packages=[
        'udiskie',
    ],
    data_files=[
        (path.join(theme_base, 'scalable', 'actions'), [
            path.join('icons', 'scalable', 'actions',
                      'udiskie-{0}.svg'.format(icon_name))
            for icon_name in icon_names])
    ],
    entry_points={
        'console_scripts': [
            'udiskie = udiskie.cli:Daemon.main',
            'udiskie-mount = udiskie.cli:Mount.main',
            'udiskie-umount = udiskie.cli:Umount.main',
        ],
    },
    install_requires=[
        'PyYAML',
        'docopt',
        # Currently not building out of the box:
        # 'PyGObject',
    ],
    tests_require=[
    ],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Environment :: X11 Applications',
        'Intended Audience :: Developers',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Desktop Environment',
        'Topic :: Software Development',
        'Topic :: System :: Filesystems',
        'Topic :: System :: Hardware',
        'Topic :: Utilities',
    ],
)
