import setuptools

setuptools.setup(
    name="commodplot",
    version="1.0.17",
    author="aeorxc",
    author_email="author@example.com",
    description="common commodity plotting including seasonal charts",
    url="https://github.com/aeorxc/commodplot",
    project_urls={
        'Source': 'https://github.com/aeorxc/commodplot',
    },
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pandas', 'cufflinks', 'plotly', 'commodutil'],
    python_requires='>=3.6',
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
)

