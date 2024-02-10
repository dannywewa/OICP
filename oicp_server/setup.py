import sys
import codecs
import os
import os.path
from setuptools import setup, find_packages

HERE = os.path.abspath(os.path.dirname(__file__))

VERSION = "0.1"
DISTNAME = "oicp_server"
LICENSE = "Apache 2.0"
AUTHOR = "Opentrons"
EMAIL = "engineering@opentrons.com"
URL = "https://github.com/Opentrons/opentrons"
DOWNLOAD_URL = ""
CLASSIFIERS = [
    "Development Status :: 5 - Production/Stable",
    "Environment :: Console",
    "Operating System :: OS Independent",
    "Intended Audience :: Science/Research",
    "Programming Language :: Python",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Topic :: Scientific/Engineering",
]
KEYWORDS = ["robots", "protocols", "synbio", "pcr", "automation", "lab"]
DESCRIPTION = "A server providing access to the Opentrons API"
PACKAGES = find_packages(where=".", exclude=["tests.*", "tests"])
INSTALL_REQUIRES = [
    # f"opentrons=={VERSION}",
    # f"opentrons-shared-data=={VERSION}",
    # f"server-utils=={VERSION}",
    "anyio",
    "fastapi",
    "python-dotenv",
    "python-multipart",
    "pydantic",
    "pydantic-settings",
    "typing-extensions",
    "uvicorn",
    "wsproto",
    "systemd-python==235; sys_platform=='linux'",
    "sqlalchemy",
    "aiosqlite",
    "paho-mqtt",
]


def read(*parts):
    """
    Build an absolute path from *parts* and and return the contents of the
    resulting file.  Assume UTF-8 encoding.
    """
    with codecs.open(os.path.join(HERE, *parts), "rb", "utf-8") as f:
        return f.read()


if __name__ == "__main__":
    setup(
        # python_requires="~=3.10",
        name=DISTNAME,
        description=DESCRIPTION,
        license=LICENSE,
        url=URL,
        version=VERSION,
        author=AUTHOR,
        author_email=EMAIL,
        maintainer=AUTHOR,
        maintainer_email=EMAIL,
        keywords=KEYWORDS,
        long_description=__doc__,
        packages=PACKAGES,
        zip_safe=False,
        classifiers=CLASSIFIERS,
        install_requires=INSTALL_REQUIRES,
        include_package_data=True,
    )
