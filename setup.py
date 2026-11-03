from pathlib import Path

from setuptools import find_packages, setup

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name="se2404",
    version="0.0.1",
    description="CLI interface for the TollSync application",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Spiros Maggioros, Reidi Pasai, Dimitrios Minagias, Stasinos Ntaveas, Sotirios Kakos",
    maintainer="Spiros Maggioros, Reidi Pasai, Dimitrios Minagias, Stasinos Ntaveas, Sotirios Kakos",
    license="MIT",
    url="https://github.com/ntua/softeng24-04",
    python_requires=">=3.9",
    install_requires=[
        "streamlit",
        "streamlit-folium",
        "pandas",
        "matplotlib",
        "seaborn",
        "pillow",
        "requests_cache",
        "retry_requests",
        "Flask==2.2.5",
        "pymongo[srv]",
        "Flask-PyMongo",
        "requests",
        "flask-mongoengine",
        "pre-commit",
        "mongomock",
        "Werkzeug==2.2.3",
    ],
    entry_points={"console_scripts": ["se2404 = cli_client.__main__:main"]},
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python",
        "Topic :: Scientific/Engineering",
        "Operating System :: Unix",
    ],
    packages=find_packages(exclude=[".github"]),
    include_package_data=True,
    keywords=[
        "Toll Stasions",
        "Toll station management",
    ],
)
