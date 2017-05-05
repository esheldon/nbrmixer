import os
import distutils
from distutils.core import setup, Extension, Command
from glob import glob
import numpy

scripts=[
    'nbrmixer-make-scripts',
    'nbrmixer-collate',
    'nbrmixer-fit-m-c',
]

scripts=[os.path.join('bin',s) for s in scripts]


configs = glob('config/*.yaml')

configs = [c for c in configs if '~' not in c]

data_files=[]
for f in configs:
    data_files.append( ('share/nbrmixer-config',[f]) )


setup(
    name="nbrmixer", 
    packages=['nbrmixer'],
    scripts=scripts,
    data_files=data_files,
    version="0.1",
)




