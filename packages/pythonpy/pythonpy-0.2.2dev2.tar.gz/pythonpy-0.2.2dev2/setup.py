from distutils.core import setup
import os

setup(
    name='pythonpy',
    version='0.2.2dev2',
    description='Command line utility for Python',
    scripts=[os.path.join('bin', 'pythonpy')],
    license='MIT',
    long_description=open('README.txt').read(),
    url='https://github.com/Russell91/pythonpy',
)
