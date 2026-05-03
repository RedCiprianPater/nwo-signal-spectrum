from setuptools import setup, find_packages

setup(
    name='nwo-signal-spectrum',
    version='1.0.0',
    description='NWO Signal Spectrum - Signal analysis for NWO Robotics',
    long_description=open('../README.md').read(),
    long_description_content_type='text/markdown',
    author='NWO Capital',
    author_email='dev@nwo.capital',
    url='https://github.com/nwocapital/nwo-signal-spectrum',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'eth-account>=0.5.0',
        'web3>=5.20.0',
        'numpy>=1.20.0',
        'scipy>=1.7.0',
    ],
    extras_require={
        'dev': [
            'pytest>=6.0',
            'pytest-asyncio>=0.15.0',
            'black>=21.0',
            'flake8>=3.9.0',
        ]
    },
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Topic :: Communications :: Ham Radio',
        'Topic :: Scientific/Engineering :: Signal Processing',
    ],
)
