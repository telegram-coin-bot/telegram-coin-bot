import os
from importlib.machinery import SourceFileLoader

from pkg_resources import parse_requirements
from setuptools import find_packages, setup

module_name = "telegram_coin_bot"

module = SourceFileLoader(
    module_name, os.path.join(module_name, "__init__.py")
).load_module()


def load_requirements(fname: str) -> list:
    requirements = []
    with open(fname, "r") as fp:
        for req in parse_requirements(fp.read()):
            extras = "[{}]".format(",".join(req.extras)) if req.extras else ""
            requirements.append("{}{}{}".format(req.name, extras, req.specifier))
    return requirements


setup(
    name=module_name,
    version=module.__version__,
    author=module.__author__,
    author_email=module.__email__,
    license=module.__license__,
    description=module.__doc__,
    long_description=open("README.md", encoding="utf-8").read(),
    url="https://github.com/telegram-coin-bot/telegram-coin-bot",
    platforms="all",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: Russian",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.5",
    packages=find_packages(),
    install_requires=load_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "{0}_config = {0}.configurator.__main__:main".format(module_name),
            "{0} = {0}.bot_manager.__main__:main".format(module_name),
        ]
    },
    include_package_data=True,
)
