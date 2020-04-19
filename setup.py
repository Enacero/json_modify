from setuptools import setup

with open("README.rst", "r") as f:
    long_description = f.read()

setup(
    name="json-modify",
    version="0.0.1",
    py_modules=["json_modify"],
    install_requires=["PyYAML>=5.3.1"],
    author="Oleksii Petrenko",
    author_email="oleksiiypetrenko@gmail.com",
    description="Simple to use json/yaml modifier",
    long_description=long_description,
    keywords="json yaml",
    project_urls={
        "Website": "https://github.com/Enacero/json_modify",
        "PyPi": "https://pypi.python.org/pypi/json_modify"
    },
    license="MIT",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
    ],
    python_requires=">3.5"
)
