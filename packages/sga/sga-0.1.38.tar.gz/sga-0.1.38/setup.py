from setuptools import setup

setup(
    name="sga",
    version='0.1.38',
    zip_safe=False,
    platforms='any',
    packages=['sga'],
    install_requires=["pyga"],
    scripts=['sga/bin/run_ga_agent.py'],
    url="https://github.com/dantezhu/sga",
    license="BSD",
    author="dantezhu",
    author_email="zny2008@gmail.com",
    description="make it easier to use pyga for web develop. and make pyga compatible with flask and django.",
)
