from distutils.core import setup


setup(
    name='mongowriter',
    description='Adapter to write documents from a queue to mongodb concurrently',
    version='0.1.3',
    author='cloudControl Team',
    author_email='info@cloudcontrol.de',
    url='https://www.cloudcontrol.com',
    license='Apache 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Topic :: Database'
    ],
    packages=['mongowriter'],
    install_requires=['pymongo>=2.5,<2.6'],
)
