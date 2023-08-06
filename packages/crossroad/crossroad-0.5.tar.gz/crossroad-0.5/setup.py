#!/usr/bin/python3
# -*- coding: utf-8 -*-

import distutils.command.build
import distutils.command.build_scripts
import distutils.command.install_data
import distutils.command.install_scripts
import gzip
import sys
import os
import stat
import subprocess
import shutil

version = '0.5'

use_setuptools = False

if 'USE_SETUPTOOLS' in os.environ or 'setuptools' in sys.modules:
    # I don't like to unreference modules out of their namespaces.
    # Unfortunately it seems pip would need setuptools instead of the
    # core distutils. Thus I import setup and install from setuptools
    # when it is requested or already loaded (ex: in pip).
    use_setuptools = True
    try:
        from setuptools import setup
        from setuptools.command.install import install
    except ImportError:
        use_setuptools = False

if not use_setuptools:
    from distutils.core import setup
    from distutils.command.install import install

class build_man(distutils.core.Command):
    '''
    Build the man page.
    '''

    description = 'build the man page'
    user_options = []

    def run(self):
        self.check_dep()
        self.create_build_tree()
        self.build()
        self.compress_man()
        self.clean()

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def check_dep(self):
        '''
        Check build dependencies.
        '''
        if shutil.which('rst2man') is None:
            sys.stderr.write('`rst2man` is a mandatory building dependency. You will probably find it in a `python3-docutils` package.')
            sys.exit(os.EX_CANTCREAT)

    def create_build_tree(self):
        '''
        Create a build tree.
        '''
        try:
            os.makedirs('build/man/man1', exist_ok=True)
            os.makedirs('build/doc', exist_ok=True)
        except os.error:
            sys.stderr.write('Build error: failure to create the build/ tree. Please check your permissions.\n')
            sys.exit(os.EX_CANTCREAT)

    def build(self):
        '''
        Create the manual.
        '''
        try:
            shutil.copyfile('doc/crossroad.rst', 'build/doc/crossroad.rst')
            update_scripts('build/doc')
            subprocess.check_call(["rst2man", "build/doc/crossroad.rst", "build/man/man1/crossroad.1"])
        except subprocess.CalledProcessError:
            sys.stderr.write('Build error: `rst2man` failed to build the man page.')
            sys.exit(os.EX_CANTCREAT)

    def compress_man(self):
        '''
        Compress the man.
        '''
        with open('build/man/man1/crossroad.1', 'rb') as manual:
            with gzip.open('build/man/man1/crossroad.1.gz', 'wb') as compressed:
                compressed.writelines(manual)

    def clean(self):
        os.unlink('build/man/man1/crossroad.1')

class my_build(distutils.command.build.build):
    '''
    Override the build to have some additional pre-processing.
    '''

    def run(self):
        # Add manual generation in build.
        self.run_command('man')
        # Move files without modification at build time
        # This allows renaming mostly.
        try:
            os.makedirs('build/bin', exist_ok = True)
            os.makedirs('build/platforms', exist_ok = True)
            os.makedirs('build/share/crossroad/scripts/bash', exist_ok = True)
            os.makedirs('build/share/crossroad/scripts/zsh.w32', exist_ok = True)
            os.makedirs('build/share/crossroad/scripts/zsh.w64', exist_ok = True)
            os.makedirs('build/share/crossroad/scripts/cmake', exist_ok = True)
        except os.error:
            sys.stderr.write('Build error: failure to create the build/ tree. Please check your permissions.\n')
            sys.exit(os.EX_CANTCREAT)
        shutil.copyfile('src/crossroad.py', 'build/bin/crossroad')
        shutil.copyfile('src/in-crossroad.py', 'build/share/crossroad/scripts/in-crossroad.py')
        shutil.copyfile('scripts/environment-32.sh', 'build/share/crossroad/scripts/environment-32.sh')
        shutil.copyfile('scripts/environment-64.sh', 'build/share/crossroad/scripts/environment-64.sh')
        # Bash startup files.
        for f in os.listdir('scripts/bash'):
            if f[:7] == 'bashrc.':
                shutil.copyfile(os.path.join('scripts/bash/', f), os.path.join('build/share/crossroad/scripts/bash/', f))
        # Zsh startup files.
        for f in os.listdir('scripts/zsh'):
            if f[:6] == 'zshrc.':
                platform = f[6:]
                shutil.copyfile(os.path.join('scripts/zsh/', f), os.path.join('build/share/crossroad/scripts/zsh.' + platform, '.zshrc'))
                shutil.copyfile('scripts/zsh/zshenv', os.path.join('build/share/crossroad/scripts/zsh.' + platform, '.zshenv'))
        # CMake files.
        shutil.copyfile('scripts/cmake/toolchain-w32.cmake', 'build/share/crossroad/scripts/cmake/toolchain-w32.cmake')
        shutil.copyfile('scripts/cmake/toolchain-w64.cmake', 'build/share/crossroad/scripts/cmake/toolchain-w64.cmake')
        for f in os.listdir('platforms'):
            if f[-3:] == '.py':
                shutil.copyfile(os.path.join('platforms', f), os.path.join('build/platforms', f))
        distutils.command.build.build.run(self)

class my_install(install):
    '''
    Override the install to modify updating scripts before installing.
    '''

    def run(self):
        try:
            os.makedirs('build/', exist_ok=True)
        except os.error:
            sys.stderr.write('Build error: failure to create the build/ tree. Please check your permissions.\n')
            sys.exit(os.EX_CANTCREAT)
        # Install is the only time we know the actual data directory.
        # We save this information in a temporary build file for replacement in scripts.
        script = open('build/data_dir', 'w')
        script.truncate(0)
        script.write(os.path.abspath(self.install_data))
        script.close()
        # Go on with normal install.
        install.run(self)

def update_scripts(build_dir):
    '''
    Convenience function to update any file in `build_dir`:
    - replace @DATADIR@ by `datadir` as set on the setup.py call.
    '''
    datadir = '/usr/local'
    try:
        data_dir_file = open('build/data_dir', 'r')
        datadir = data_dir_file.readline().rstrip(' \n\r\t')
        data_dir_file.close()
    except IOError:
        sys.stderr.write('Warning: no build/data_dir file. You should run the `install` command. Defaulting to {}.\n'.format(datadir))

    for dirpath, dirnames, filenames in os.walk(build_dir):
        for f in filenames:
            try:
                script = open(os.path.join(dirpath, f), 'r+')
                contents = script.read()
                # Make the necessary replacements.
                contents = contents.replace('@DATADIR@', datadir)
                contents = contents.replace('@VERSION@', version)
                script.truncate(0)
                script.seek(0)
                script.write(contents)
                script.flush()
                script.close()
            except IOError:
                sys.stderr.write('The script {} failed to update. Check your permissions.'.format(f))
                sys.exit(os.EX_CANTCREAT)

class my_install_data(distutils.command.install_data.install_data):
    '''
    Override the install to build the manual first.
    '''

    def run(self):
        update_scripts('build/platforms')
        update_scripts('build/share/crossroad/scripts')
        distutils.command.install_data.install_data.run(self)
        datadir = '/usr/local'
        try:
            data_dir_file = open('build/data_dir', 'r')
            datadir = data_dir_file.readline().rstrip(' \n\r\t')
            data_dir_file.close()
        except IOError:
            sys.stderr.write('Warning: no build/data_dir file. You should run the `install` command. Defaulting to {}.\n'.format(datadir))
        os.chmod(os.path.join(datadir, 'share/crossroad/scripts/in-crossroad.py'),
                              stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IXOTH)
        os.chmod(os.path.join(datadir, 'share/crossroad/scripts/config.guess'),
                              stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IXOTH)
        os.chmod(os.path.join(datadir, 'share/crossroad/scripts/crossroad-mingw-install.py'),
                              stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IXOTH)
        os.chmod(os.path.join(datadir, 'share/crossroad/scripts/crossroad-gcc'),
                              stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IXOTH)
        os.chmod(os.path.join(datadir, 'share/crossroad/scripts/crossroad-cpp'),
                              stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IXOTH)
        os.chmod(os.path.join(datadir, 'share/crossroad/scripts/crossroad-pkg-config'),
                              stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR |
                              stat.S_IRGRP | stat.S_IXGRP |
                              stat.S_IROTH | stat.S_IXOTH)
        os.makedirs(os.path.join(datadir, 'share/crossroad/bin/'), exist_ok=True)
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-pkg-config'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-pkg-config'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-gcc'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-gcc'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-g++'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-g++'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-cpp'))
        except OSError:
            pass
        try:
            os.unlink(os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-cpp'))
        except OSError:
            pass
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-pkg-config'),
                   os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-pkg-config'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-pkg-config'),
                   os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-pkg-config'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-gcc'),
                   os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-gcc'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-gcc'),
                   os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-gcc'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-gcc'),
                   os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-g++'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-gcc'),
                   os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-g++'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-cpp'),
                   os.path.join(datadir, 'share/crossroad/bin/x86_64-w64-mingw32-cpp'))
        os.symlink(os.path.join(datadir, 'share/crossroad/scripts/crossroad-cpp'),
                   os.path.join(datadir, 'share/crossroad/bin/i686-w64-mingw32-cpp'))

class my_install_scripts(distutils.command.install_scripts.install_scripts):
    '''
    Override the install to build the manual first.
    '''

    def run(self):
        update_scripts(self.build_dir)
        distutils.command.install_scripts.install_scripts.run(self)


platform_list = os.listdir('platforms')
platform_list = [os.path.join('build/platforms/', f) for f in platform_list if f[-3:] == '.py']

bash_env = [os.path.join('build/share/crossroad/scripts/bash/', f) for f in os.listdir('scripts/bash/') if f[:7] == 'bashrc.']

setup(
    name = 'crossroad',
    cmdclass = {'man': build_man, 'build': my_build, 'install': my_install,
        'install_data': my_install_data, 'install_scripts': my_install_scripts},
    version = version,
    description = 'Cross-Compilation Environment Toolkit.',
    long_description = open('README').read(),
    author = 'Jehan',
    author_email = 'jehan at girinstud.io',
    url = 'http://girinstud.io',
    license = 'AGPLv3+',
    classifiers = [
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3.3',
        'Topic :: Software Development :: Build Tools',
    ],
    requires = [],
    scripts = ['build/bin/crossroad'],
    data_files = [('man/man1/', ['build/man/man1/crossroad.1.gz']),
        ('share/crossroad/scripts/', ['scripts/crossroad-mingw-install.py', 'scripts/config.guess',
                                      'build/share/crossroad/scripts/in-crossroad.py',
                                      'build/share/crossroad/scripts/environment-32.sh',
                                      'build/share/crossroad/scripts/environment-64.sh',
                                      'scripts/pre-bash-env.sh',
                                      'scripts/pre-zsh-env.sh',
                                      'scripts/post-env.sh',
                                      'scripts/crossroad-gcc', 'scripts/crossroad-pkg-config',
                                      'scripts/crossroad-cpp',
                                      ]),
        ('share/crossroad/scripts/bash', bash_env),
        ('share/crossroad/scripts/zsh.w32', ['build/share/crossroad/scripts/zsh.w32/.zshenv',
                                             'build/share/crossroad/scripts/zsh.w32/.zshrc']),
        ('share/crossroad/scripts/zsh.w64', ['build/share/crossroad/scripts/zsh.w64/.zshenv',
                                             'build/share/crossroad/scripts/zsh.w64/.zshrc']),
        ('share/crossroad/scripts/cmake', ['build/share/crossroad/scripts/cmake/toolchain-w32.cmake',
                                            'build/share/crossroad/scripts/cmake/toolchain-w64.cmake']),
        ('share/crossroad/platforms/', platform_list),
        #('crossroad/projects/', ['projects']),
        ],
    )

