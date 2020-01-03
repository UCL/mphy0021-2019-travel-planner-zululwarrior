from setuptools import setup, find_packages

setup(
    name="travelplanner",
    version="1.0.0",
    packages=find_packages(exclude=['*test']),
    install_requires=['numpy', 'matplotlib'],
    entry_points={
        'console_scripts': [
            'bussimula = travelplanner.command:process'
        ]
    }
)
