import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    version="0.0.1",
    name="Reverse Proxy POC",
    author="Dermot Bruce-Agbeko",
    author_email="dermotag@hotmail.com",
    description="Reverse proxy POC as part system design",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=["Programming Language :: Python :: 3",
                 "License :: OSI Approved :: MIT License",
                 "Operating System :: OS Independent"])
