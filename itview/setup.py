from setuptools import setup, find_packages


setup(
    name="itview",
    version="1.0",
    description="Itview connector for the RPA package",
    author="Sony Pictures Imageworks",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "": ["*.json"]
    },
    install_requires=[],  # Add dependencies if needed
    python_requires=">=3.6",
)
