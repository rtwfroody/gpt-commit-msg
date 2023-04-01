from setuptools import setup

setup(
    name="gpt_commit_msg",
    version="0.1.2",
    py_modules=['gpt_commit_msg'],
    install_requires=[
        "openai",
        "tiktoken"
    ],
    entry_points={
        'console_scripts': [
            'gpt-commit-msg=gpt_commit_msg:main'
        ]
    },
    author="Tim Newsome",
    author_email="tim@casualhacker.net",
    description="A package for generating commit messages using GPT",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/rtwfroody/gpt-commit-msg",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.6",
)

