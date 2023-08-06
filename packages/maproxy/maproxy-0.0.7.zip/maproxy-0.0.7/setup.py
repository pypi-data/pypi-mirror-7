import os
from setuptools import setup


setup(name='maproxy',

    version = "0.0.7",
    author = "Zvika Ferentz",
    author_email = "zvika dot ferentz at gmail",
    description = ("My first attempt to create a simple and awesome "
                   "TCP proxy using Tornado"),
    


    # For now, let's just build a module, not a package
    packages=['maproxy'],

    keywords = "TCP proxy ssl http https certificates",
    long_description=open('README').read(),

    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Topic :: Internet :: Proxy Servers"]
      )
