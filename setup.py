from setuptools import setup, find_packages

requires = [
    'numpy',
    'openrouteservice',
    'pandas',
    'matplotlib',
    'scikit-mobility',
  'geopandas',
  'geopy',
  #'gdal',
  'fiona',
  'notebook',
  'jupyter',
  'ipython',
  'geotiff',
  'rasterio',
  'geojson',
   'rasterio',
   'rasterstats'
]

with open('README.md') as f:
    readme = f.read()

with open('LICENSE.md') as f:
    license = f.read()

setup(
    name='SatMobFusion',
    version='0.0.0',
    description='--add description here--',
    long_description=readme,
    author1='Ekin Ugurel',
    author1_email='ugurel@uw.com',
  author2='Steffen Coenen',
  author2_email='scoenen@uw.edu',
    license=license,
    packages=find_packages(),
    #package_data=package_data,
    install_requires=requires
)
