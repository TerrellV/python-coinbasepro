import setuptools, runpy


version_meta = runpy.run_path('version.py')
version = version_meta['__version__']


def long_description():
    with open("README.md", "r") as fh:
        return fh.read()


setuptools.setup(
    name="cbp-client",
    version=version,
    author="TerrellV",
    author_email="terrell.vest@gmail.com",
    description="An unofficial python package for interacting with the Coinbase Pro API",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/TerrellV/python-coinbasepro",
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=[
        'requests>=2'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
