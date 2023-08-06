from setuptools import setup, find_packages

import mosaik_csv


setup(
    name='mosaik-csv',
    version=mosaik_csv.__version__,
    author='Stefan Scherfke',
    author_email='stefan.scherfke at offis.de',
    description=('Presents CSV datasets to mosaik as models.'),
    long_description=(open('README.txt').read() + '\n\n' +
                      open('CHANGES.txt').read() + '\n\n' +
                      open('AUTHORS.txt').read()),
    url='https://bitbucket.org/mosaik/mosaik-csv',
    install_requires=[
        'arrow>=0.4.2',
        'mosaik-api>=2.0a1',
    ],
    packages=find_packages(),
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'mosaik-csv = mosaik_csv.mosaik:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Topic :: Scientific/Engineering',
    ],
)
