from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ai-workflows",
    version="1.0.0",
    description="Claude Code workflows equivalent for Cursor and GitHub Copilot",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="codes1gn",
    url="https://github.com/codes1gn/workflows",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "pyyaml>=6.0",
    ],
    extras_require={
        "anthropic": ["anthropic>=0.30"],
        "openai": ["openai>=1.0"],
        "all": ["anthropic>=0.30", "openai>=1.0"],
    },
    entry_points={
        "console_scripts": [
            "wf=workflow_runner.cli:main",
        ],
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
        "Topic :: Utilities",
    ],
    include_package_data=True,
    package_data={
        "": ["../builtin-workflows/*.yaml", "../builtin-subagents/*.md"],
    },
)
