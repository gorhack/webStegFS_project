from setuptools import setup, find_packages


with open('README.rst', 'r') as f:
    readme = f.read()

setup(
    name='covertFS',
    version='0.9.4b',
    packages=[
        'covertFS',
        'covertFS.Encryption',
        'covertFS.File_System',
        'covertFS.File_System.fs',
        'covertFS.Image_Manipulation',
        'covertFS.Web_Connection',
        'covertFS.Web_Connection.API_Keys',
             ],
    entry_points={'console_scripts': ['covertFS = covertFS.__main__:main']},
    description='It\'s covert and stuff',
    long_description=readme,
    author='Kyle Gorak, David Hart, Adam Sjoholm, and Ryne Flores',
    author_email='kyle.gorak@usma.edu',
    url='https://github.com/gorhack/covertFS',
    license='USMA',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: File System',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Unix',
    ],
    keywords='covert file system steganography',
    package_data={
        'README': ['README.rst'],
    },
    install_requires=[
        "requests",
        "beautifulsoup4",
        "fs",
        "lxml",
        "Pillow",
        "fusepy",
    ],
)
