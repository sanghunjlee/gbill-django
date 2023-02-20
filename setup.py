from gbill import APP_NAME, VERSION
from setuptools import setup, find_packages

setup(
    name=APP_NAME,
    version=VERSION,
    description='Tkinter gui app for grouping and splitting bills',
    author='Sanghun J Lee',
    author_email='sanghunjlee@gmail.com',
    license='MIT',
    packages=find_packages(),
)