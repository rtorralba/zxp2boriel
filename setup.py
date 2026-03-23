import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zxp2boriel",
    version="0.1.13",
    author="Raül Torralba",
    author_email="raul.torralba@gmail.com",
    description="Convert ZX-Paintbrush (.zxp) files to Boriel Basic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rtorralba/zxp2boriel",
    py_modules=["zxp2boriel", "tile_exporter"],
    classifiers=[
        "Programming Language :: Python :: 3",
        # License classifier removed in favor of SPDX license expression
        "Operating System :: OS Independent",
    ],
    # Use SPDX license expression instead of Trove classifier
    license_expression="AGPL-3.0-or-later",
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'zxp2boriel=zxp2boriel:main',
        ],
    },
)
