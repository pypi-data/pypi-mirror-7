================
Gistpy
================

Command line client for gist(API v3).


Installation
------------

pypi::

	$ pip install gistpy
	# or 
	$ easy_install gistpy
	$ gistpy -h

Source code::

	$ python setup.py install
	$ gistpy -h


Usage
------------

Authorization::

	# Get accesstoken
	$ export GISTPY_USER=username
	$ export GISTPY_PASSWORD=password
	$ gistpy register
	# or 
	$ gistpy register -u username -p password
	...
	Your access_token is xxxxxxxxxxx
	
	# Set accesstoken
	$ export GISTPY_TOKEN=xxxxxxxxxxx


Get::

	$ gistpy get <gistid> <destination_directory>


Create::

	$ gistpy create [gistids...]		# public
	$ gistpy create [gistids...] -d "description"
	$ gistpy create [gistids...] -a 	# as anonymous
	$ gistpy create [gistids...] -p 	# private
	
	$ echo "test" | gistpy
	$ echo "test" | gistpy -p # private
	$ echo "test" | gistpy -a # as anonymous


Edit::

	$ gistpy edit <gistid> [files...]
	
	
Delete::

	$ gistpy delete <gistid>
	

Display the help of each command. ::

	$ gistpy <command> -h
	

LICENSE
------------

This software is licensed under the MIT License.

