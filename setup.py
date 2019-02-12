import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py2tex-jsleb333",
    version="0.0.1",
    author="Jean-Samuel Leboeuf",
    author_email="jean-samuel.leboeuf.1@ulaval.ca",
    description="A Python to LaTeX converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jsleb333/py2tex",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
