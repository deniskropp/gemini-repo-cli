from setuptools import setup, find_packages

setup(
    name='gemini-repo-cli',
    version='0.2.0',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'google-generativeai',
    ],
    entry_points={
        'console_scripts': [
            'gemini-repo-cli=gemini_repo_cli.gemini_repo_cli:main',
        ],
    },
    author='Denis Kropp',
    author_email='dok@directfb1.org',
    description='Repo-level tool using Gemini',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/deniskropp/gemini-repo-cli',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Code Generators',
    ],
    keywords='gemini ai code generation repository',
    python_requires='>=3.8',
    project_urls={
        'Bug Reports': 'https://github.com/deniskropp/gemini-repo-cli/issues',
        'Source': 'https://github.com/deniskropp/gemini-repo-cli',
    },
)
