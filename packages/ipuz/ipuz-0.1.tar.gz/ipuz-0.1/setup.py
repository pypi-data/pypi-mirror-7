from setuptools import setup


with open('README.md') as readme_file:
    long_description = readme_file.read()


setup(
    name="ipuz",
    version="0.1",
    description="Python library for reading and writing ipuz puzzle files",
    long_description=long_description,
    author="Simeon Visser",
    author_email="simeonvisser@gmail.com",
    url="https://github.com/svisser/ipuz",
    install_requires=[
        'six==1.6.1'
    ],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "Topic :: Games/Entertainment :: Puzzle Games",
    ]
)
