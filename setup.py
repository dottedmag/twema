#
# © 2020 Mikhail Gusarov <dottedmag@dottedmag.net>
#
# This file is a part of twema and licensed under AGPLv3. See doc/COPYING at the
# root of the repository for the details.
#
from setuptools import setup

setup(
    name="twema",
    version="0.5.1",
    description="Twitter-to-email gateway",
    url="https://github.com/dottedmag/twema",
    author="Mikhail Gusarov",
    author_email="dottedmag@dottedmag.net",
    license="AGPLv3",
    packages=["twema"],
    entry_points={"console_scripts": ["twema=twema.cli:main"]},
    include_package_data=True,
    install_requires=[
        "Jinja2==2.11.0",
        "toml==0.10.0",
        "twitter==1.18.0",
        "xdg==4.0.1",
    ],
)
