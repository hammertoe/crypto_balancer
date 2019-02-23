from setuptools import setup

setup(name='crypto_balancer',
      version='0.1',
      packages=['crypto_balancer'],
      entry_points={
          'console_scripts': [
              'crypto_balancer = crypto_balancer.main:main'
          ]
      },
      )
