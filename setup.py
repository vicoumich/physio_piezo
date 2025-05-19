from setuptools import setup, find_packages

setup(
    name="physio_piezo",
    version="0.1.0",
    description="Fork de physio avec détection de cycles par extrema pour ceinture piezo",
    author="",
    packages=find_packages(),     
    install_requires=[
        "numpy",
        "scipy",
        "pandas",
        "mne",
        "neo",
        "tqdm"
    ],
)
