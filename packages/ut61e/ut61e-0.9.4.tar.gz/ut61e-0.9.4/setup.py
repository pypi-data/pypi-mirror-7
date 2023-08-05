from setuptools import setup
try:
    import pypandoc
    LDESC = pypandoc.convert('README.md', 'rst')
except (IOError, ImportError, RuntimeError):
    LDESC = ''

setup(
    name = 'ut61e',
    version = '0.9.4',
    description = 'Captures and Interprets Data from your Digital Multimeter Uni-T UT61E.',
    author = 'Philipp Klaus',
    author_email = 'philipp.l.klaus@web.de',
    packages = ['ut61e'],
    scripts = ['ut61e/es51922.py', 'ut61e/he2325u_hidapi.py', 'ut61e/he2325u_pyusb.py',],
    url = 'https://github.com/pklaus/ut61e_python',
    license = 'GPL',
    long_description = LDESC,
    install_requires = [],
    extras_require = {
        'access to he2325u_hidapi.py': ["hidapi >= 0.7.0-1"],
        'access to he2325u_pyusb.py': ["pyusb >= 1.0.0"],
    },
    keywords = 'UNI-T UT61E DMM digital multimeter',
    classifiers = [
        'Development Status :: 4 - Beta',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: System :: Hardware :: Hardware Drivers',
        'Topic :: Scientific/Engineering',
    ]
)


