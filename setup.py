from setuptools import setup, Extension
import os

setup(
    name='pycmt',
    version=os.getenv("VERSION", '0.0.0'),
    py_modules=['pycmt'],
    ext_modules = [
        Extension("pycmt",
            sources=["pycmt.pyx"],
            extra_objects=['/usr/lib/libcmt.a'],
            extra_compile_args=["-fpic","-fstack-protector-strong"],
            library_dirs=["/usr/local/lib/","/usr/lib"],
        )
    ],
    setup_requires=[
        'setuptools>=75.0.0',
        'cython>=3.2.2',
    ],
)
