from setuptools import setup, find_packages

setup(
    name='gemini-repo-cli',
    version='0.1.0',
    packages=find_packages(),
    install_requires=[
        'huggingface_hub'
    ],
    entry_points={
        'console_scripts': [
            'gemini-repo-cli=gemini_repo_cli.gemini_repo_cli:main',
        ],
    },
    author='Denis Kropp',
    author_email='dok@directfb1.org',
    description='Repo-level tool using Gemini',
    url='https://github.com/deniskropp/gemini-repo-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.8',
)
