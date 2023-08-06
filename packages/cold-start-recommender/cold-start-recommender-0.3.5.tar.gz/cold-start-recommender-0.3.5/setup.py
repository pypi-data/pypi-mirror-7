from distutils.core import setup

setup(name='cold-start-recommender',
      description='In-memory recommender for recommendations produced on-the-fly',
      author='Mario Alemi',
      author_email='mario.alemi@gmail.com',
      version='0.3.5',
      py_modules=['csrec.Recommender'],
      url='https://github.com/malemi/cold-start-recommender',
      licence='LICENSE.txt',
      long_description=open('README.rst').read(),
      scripts=['bin/recommender_api.py'],
      )
