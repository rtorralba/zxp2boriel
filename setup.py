import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zxp2boriel",
    version="0.1.0",
    author="Raül Torralba",
    author_email="raul.torralba@gmail.com",
    description="Convert ZX-Paintbrush (.zxp) files to Boriel Basic",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rtorralba/zxp2boriel",
    py_modules=["zxp2boriel"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    entry_points={
        'console_scripts': [
            'zxp2boriel=zxp2boriel:main',
        ],
    },
)
