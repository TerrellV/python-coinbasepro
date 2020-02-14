import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="coinbasepro", # Replace with your own username
    version="0.0.1",
    author="TerrellV",
    author_email="terrell.vest@gmail.com",
    description="A python package for interacting with the Coinbase Pro API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/TerrellV/python-coinbasepro-api.git",
    packages=setuptools.find_packages(exclude=['tests']),
    install_requires=['pandas', 'numpy', 'requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
