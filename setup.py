from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="aws-chatbot",
    version="0.1.0",
    author="Weyland Chiang",
    author_email="weyland.chiang@gmail.com",
    description="A natural language chatbot for querying AWS resources using LangChain",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/wey-chiang/aws_chatbot",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "aws-chatbot=aws_chatbot.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)