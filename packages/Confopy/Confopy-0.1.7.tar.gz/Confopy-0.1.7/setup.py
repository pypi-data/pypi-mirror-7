try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name="Confopy",
    version="0.1.7",
    url="https://github.com/ooz/confopy",
    author="Oliver Zscheyge",
    author_email="oliverzscheyge@gmail.com",
    packages=["confopy", "confopy.analysis", "confopy.localization", "confopy.model", "confopy.pdfextract", "confopy.localization.de", "confopy.localization.de.corpus_de"],
    license="MIT License",
    description="Evaluates the linguistic and structural quality of scientific texts.",
    long_description=open("README.md").read(),
    package_data={"": ["README.md", "bin/confopy"]},
    include_package_data=True,
    scripts=["bin/confopy"],
    data_files = ["README.md"],
    install_requires=[
        "lxml == 2.3.2",
        "numpy == 1.6.2",
        "nltk == 2.0.2",
        "pyenchant == 1.6.5",
    ],
)
# pyenchant is for spell checking
# other maybe deps:
#"pyyaml ==",
#"pattern ==",
