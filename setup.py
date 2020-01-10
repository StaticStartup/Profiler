# coding: utf-8


# Standard Library
import setuptools

setuptools.setup(
    ### Metadata
    name="profiler"
    version="1.0.0"
    description="Monitors CPU and Memory usage of an application.",
    url="",

    author="Jeremiah Liou, Tarun Verma",
    author_email="jeremiahjliou@gmail.com, tarun.verma25d@gmail.com",

    maintainer="Jeremiah Liou, Tarun Verma",
    maintainer_email="jeremiahjliou@gmail.com, tarun.verma25d@gmail.com",

    packages=['profiler'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers and Data Scientists",
        "License :: MIT License",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Lanugae :: Python :: 3",
    ],

    # Dependencies
    install_requires=[
        'psutil>=5.6.7',
        'matplotlib>=3.1.2',
        'numpy>=1.18.1',
    ],
)
