from setuptools import setup

setup(
    name='termrule',
    version='0.11',
    py_modules=['termrule'],
    description='Colored Horizontal Rule For Terminal',
    url='http://github.com/itsnauman/termrule',
    author='Nauman Ahmad',
    author_email='nauman-ahmad@outlook.com',
    license='MIT',
    include_package_data=True,
    packages=['tr'],
    install_requires=[
        'termcolor',
    ],
    entry_points='''
        [console_scripts]
        tr=tr.termrule:main
    ''',
)
