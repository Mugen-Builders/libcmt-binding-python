from setuptools import setup, Extension
import os

setup(
    name='pycmt',
    version=os.getenv("VERSION", '0.0.0'),
    py_modules=['pycmt'],
    ext_modules = [
        Extension("pycmt",
            sources=["pycmt.pyx"],
            # language="c++",
            extra_objects=['/usr/lib/libcmt.a'],
        )
    ],
    setup_requires=[
        'setuptools>=75.0.0',
        'cython>=3.2.2',
    ],
)
