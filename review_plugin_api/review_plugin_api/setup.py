from setuptools import setup, find_packages

setup(
    name='review_plugin_api',
    version='0.1',
    packages=find_packages(include=['review_plugin_api', 'review_plugin_api.*']),
    install_requires=[
        # List your module's dependencies here
    ],
    author='Sony Pictures Imageworks',
    description='Common plugin API and widget library for review/playback systems',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    #url='https://github.com/yourusername/my_module',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.9',
)
