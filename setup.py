from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="airpy-tool",
    version="1.0.1",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'airpy': ['data/*.csv'],
    },
    install_requires=[
        "pandas",
        "numpy",
        "matplotlib",
    ],
    entry_points={
        "console_scripts": [
            "airpy=airpy.cli:main",
        ],
    },
    description="A tool for cleaning and processing air quality data",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Chandan Kumar",
    author_email="chandankr014@gmail.com", 
    url="https://github.com/chandankr014/airpy-tool", 
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Atmospheric Science",
    ],
    python_requires=">=3.6",
) 