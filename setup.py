from setuptools import find_packages, setup

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="blood-on-the-clocktower",
    install_requires=requirements,
    packages=find_packages(),
    version="1.0",
)
