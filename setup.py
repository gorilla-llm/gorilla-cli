# Copyright 2023 https://github.com/ShishirPatil/gorilla
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from setuptools import setup, find_packages

setup(
    name="gorilla-cli",
    version="0.0.11",
    url="https://github.com/gorilla-llm/gorilla-cli",
    author="Shishir Patil, Tianjun Zhang",
    author_email="sgp@berkeley.edu, tianjunz@berkeley.edu",
    description="LLMs for CLI",
    long_description=open("README.md", "r", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    py_modules=["go_cli"],
    packages=find_packages(include=["*", "go_questionary.*"]),
    install_requires=[
        "requests",
        "halo",
        "prompt-toolkit",
    ],
    entry_points={
        "console_scripts": [
            "gorilla=go_cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
    license="Apache 2.0",
    python_requires=">=3.6",
)
