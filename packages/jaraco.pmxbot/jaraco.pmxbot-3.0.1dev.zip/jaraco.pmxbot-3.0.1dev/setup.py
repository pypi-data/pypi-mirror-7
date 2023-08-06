#!/usr/bin/env python
import setuptools

with open('README.txt') as readme_stream:
	readme = readme_stream.read()
with open('CHANGES.txt') as changes_stream:
	changes = changes_stream.read()

setup_params = dict(
	name='jaraco.pmxbot',
	use_hg_version=True,
	author="Jason R. Coombs",
	author_email="jaraco@jaraco.com",
	url="https://bitbucket.org/jaraco/jaraco.pmxbot",
	description="pmxbot commands by jaraco",
	long_description = readme + '\n\n' + changes,
	packages=setuptools.find_packages(),
	namespace_packages=['jaraco'],
	zip_safe=False,
	setup_requires=[
		'hgtools',
	],
	entry_points = dict(
		pmxbot_handlers=[
			'jaraco.pmxbot = jaraco.pmxbot',
			'http API = jaraco.pmxbot.http',
			'notification = jaraco.pmxbot.notification',
		],
	),
)
if __name__ == '__main__':
	setuptools.setup(**setup_params)
