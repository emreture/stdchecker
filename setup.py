import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="stdchecker",
    version="0.1.5",
    author="Metin Emre TÜRE",
    author_email="emreture@gmail.com",
    description="A library for checking the latest revisions of standard methods published by standard bodies.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/emreture/stdchecker",
    packages=setuptools.find_packages(),
    install_requires=[
        "beautifulsoup4",
        "requests",
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.8",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Natural Language :: English",
    ],
    python_requires='>=3.8',
)
