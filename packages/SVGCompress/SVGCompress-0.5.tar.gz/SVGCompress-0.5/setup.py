from setuptools import setup
setup(
      name         = 'SVGCompress',
      packages     = ['SVGCompress'],
      version      = '0.5',
      description  = 'Compress svg graphics',
      author       = 'Gen Del Raye',
      author_email = 'gdelraye@hawaii.edu',
      url          = '',
      download_url = '',
      keywords     = ['figure', 'vector', 'svg', 'compression'],
      install_requires = ['numpy >= 1.7', 'shapely', 'svg.path', 'rdp', 'lxml', 'scour'],
      package_data = {'SVGCompress': ['test/*.svg']},
      classifiers  = [
                      "Intended Audience :: Science/Research",
                      "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                      "Natural Language :: English",
                      "Operating System :: OS Independent",
                      "Programming Language :: Python",
                      "Topic :: Scientific/Engineering",
                      "Topic :: Scientific/Engineering :: Visualization"],
      )