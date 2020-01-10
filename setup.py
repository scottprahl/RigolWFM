from setuptools import setup

setup(
	name='RigolWFM',
	packages=['RigolWFM'],
	version='0.1.2',
	description='Read and parse Rigol Oscilloscope WFM files',
	url='https://github.com/scottprahl/RigolWFM.git',  
	author='Scott Prahl',
	author_email='scott.prahl@oit.edu',
	license='MIT',
	classifiers=[
		'Development Status :: 1 - Alpha',
		'License :: OSI Approved :: MIT License',
		'Intended Audience :: Science/Research',
		'Programming Language :: Python',
		'Topic :: Scientific/Engineering :: Physics',
	],
	keywords=['rigol', 'wfm', 'DS1052E', 'DS1102E'],
	install_requires=['numpy','matplotlib'],
	long_description=
	"""
	A basic package for working with Rigol waveform (.wfm) files.
	""",
)