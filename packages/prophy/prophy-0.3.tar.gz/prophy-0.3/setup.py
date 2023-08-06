from setuptools import setup, find_packages

long_description = open('README.rst').read()

setup(name = 'prophy',
      packages = find_packages(),
      entry_points = {
          'console_scripts': [
              'prophyc = prophyc:main'
          ]
      },
      version = '0.3',
      description = 'prophy: fast data interchange format toolchain',
      long_description = long_description,
      author = 'Krzysztof Laskowski',
      author_email = 'krzysztof.laskowski@nsn.com',
      url = "https://github.com/aurzenligl/prophy",
      license = 'MIT license',
      keywords = "IDL codec binary data",
      classifiers = [
            "Development Status :: 4 - Beta",
            "Intended Audience :: Developers",
            "Intended Audience :: Telecommunications Industry",
            "License :: OSI Approved :: MIT License",
            "Operating System :: Unix",
            "Operating System :: Microsoft :: Windows",
            "Programming Language :: Python :: 2.7",
            "Programming Language :: C++",
            "Topic :: Utilities",
            "Topic :: Software Development :: Libraries",
            "Topic :: Scientific/Engineering :: Interface Engine/Protocol Translator",
      ],
      zip_safe = False
)
