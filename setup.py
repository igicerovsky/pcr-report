from setuptools import setup, find_packages

VERSION = '0.1.0'
DESCRIPTION = 'PCR report generation'
LONG_DESCRIPTION = 'Genrate report for PCR'

# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="pcrep",
    version=VERSION,
    author="Igor Cerovsky",
    author_email="<igor.cerovsky@takeda.com>",
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],  # add any additional packages that
    # needs to be installed along with your package.

    keywords=['python', 'pcr', 'report'],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Analysts",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ]
)
