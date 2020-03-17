from setuptools import setup

# use README as the long description
# make sure to use the syntax that works in both ReST and markdown
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='RigolWFM',
    packages=['RigolWFM'],
    version='0.5.0',
    description='Read and parse Rigol Oscilloscope WFM files',
    url='https://github.com/scottprahl/RigolWFM.git',  
    author='Scott Prahl',
    author_email='scott.prahl@oit.edu',
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Intended Audience :: Science/Research',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Topic :: Scientific/Engineering',
    ],
    scripts=['wfmconvert'] ,
    keywords=['Rigol', 'wfm', 'DS1000C','DS1000CD','DS1000C','DS1000MD',
    'DS1000M','DS1302CA','DS1202CA','DS1102CA','DS1062CA','DS1000E',
    'DS1000D','DS1102E','DS1052E','DS1102D','DS1052D','DS1000Z','DS1202Z',
    'DS1074Z','DS1104Z','DS1074Z-S','DS1104Z-S','MSO1054Z','DS1054Z',
    'MSO1074Z','MSO1104Z','DS1104Z','DS2000','DS2102A','MSO2102A',
    'MSO2102A-S','DS2202A','MSO2202A','MSO2202A-S','DS2302A','MSO2302A',
    'MSO2302A-S','DS4000','DS4054','DS4052','DS4034','DS4032','DS4024',
    'DS4022','DS4014','DS4012','MSO4054','MSO4052','MSO4034','MSO4032',
    'MSO4024','MSO4022','MSO4014','MSO4012','DS6000','DS6062','DS6064',
    'DS6102','DS6104'],
    install_requires=['kaitaistruct', 'numpy','matplotlib'],
    long_description=long_description,
    long_description_content_type='text/markdown'
)