from setuptools import setup, find_packages

setup(
    name="inflightpayment",
    version="1.0.0",
    description="CLI tool for reading and sending customer and purchase data.",
    author="Paula Pawlowski",
    author_email="ppwlwski@gmail.com",
    packages=["cli_paymentdata"],
    install_requires=[
        "argparse",
        "jsonschema",
        "pytest",
        "requests",
        "requests-mock",
    ],
    entry_points={
        "console_scripts": [
            "inflightpayment=cli_paymentdata.cli_read_csv:run",
        ],
    },
)
