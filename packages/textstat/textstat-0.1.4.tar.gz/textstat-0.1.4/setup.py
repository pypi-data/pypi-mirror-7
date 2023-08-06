from setuptools import setup

setup(
    name='textstat',
    packages=['textstat'],
    version='0.1.4',
    description='Calculate statistics from text',
    author='Shivam Bansal, Chaitaniya Aggarwal',
    author_email='shivam5992@gmail.com, chaitanya.citupes@gmail.com',
    url='https://github.com/shivam5992/textstat',
    long_description=open('README.md').read(),
    package_data={'': ['easy_word_list']},
    include_package_data=True,
    license='MIT',
    classifiers=(
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.5",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        ),
)
