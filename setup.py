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
    long_description=open("README.md").read(),
    url="https://github.com/telegram-coin-bot/telegram-coin-bot",
    platforms="all",
    classifiers=[
        "Intended Audience :: Developers",
        "Natural Language :: Russian",
        "Operating System :: POSIX",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: CPython",
    ],
    python_requires=">=3.8",
    packages=find_packages(),
    install_requires=load_requirements("requirements.txt"),
    entry_points={
        "console_scripts": [
            "{0}_db = {0}.db.__main__:main".format(module_name),
            "{0}_accounts = {0}.accounts.__main__:main".format(module_name),
            "{0}_visit_sites = {0}.bot_tasks.visit_sites.__main__:main".format(
                module_name
            ),
        ]
    },
    include_package_data=True,
)
