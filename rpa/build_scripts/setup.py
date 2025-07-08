from setuptools import setup, find_packages


setup(
    name="rpa",
    version="0.2.4",
    description="Review Plugin Api",
    author="Sony Pictures Imageworks",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[],  # Add dependencies if needed
    python_requires=">=3.6",
)
