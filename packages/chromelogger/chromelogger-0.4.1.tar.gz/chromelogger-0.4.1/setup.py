from setuptools import setup

# magic
setup(
    name='chromelogger',
    version='0.4.1',
    description='Python library for logging data to Google Chrome console.',
    long_description='Chrome Logger allows you to send server side logs from your application to the Chrome Logger extension.',
    author='Craig Campbell',
    author_email='iamcraigcampbell@gmail.com',
    url='https://github.com/ccampbell/chromelogger-python',
    download_url='https://github.com/ccampbell/chromelogger-python/archive/0.4.1.zip#egg=chromelogger',
    license='Apache 2.0',
    install_requires=['jsonpickle'],
    py_modules=['chromelogger'],
    platforms=["any"]
)
