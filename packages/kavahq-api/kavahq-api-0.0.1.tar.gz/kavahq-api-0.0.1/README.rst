=====================
KavaHQ.com API client
=====================



Usage
=====

.. code-block:: python

	import kavahq
	import keyring
	import getpass

	SERVICE = 'kavahq-api'
	username = 'imposeren'
	password = keyring.get_password(SERVICE, username)
	if password is None:
	    password = getpass.getpass()
	    keyring.set_password(SERVICE, username, password)

	api = kavahq.KavaApi(username=username, password=password)

	print api.get_projects(company='42-coffee-cups')
	print api.get_project('kavyarnya')

	cc = api.get_company('42-coffee-cups')
	# print cc.add_project({'name': 'new test'})
	print cc.projects()
	print cc.project('kavyarnya')