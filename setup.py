import setuptools
from version import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="python2latex",
    version=version,
    author="Jean-Samuel Leboeuf",
    author_email="jean-samuel.leboeuf.1@ulaval.ca",
    description="A Python to LaTeX converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsleb333/python2latex",
    packages=setuptools.find_packages(),
    install_requires=['numpy'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
