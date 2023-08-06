============
Contributing
============

Report a Bug or Make a Feature Request
--------------------------------------
Please go to the GitHub Issues page: https://github.com/SuperCowPowers/workbench/issues.

Look at the Code
----------------

.. raw:: html

	<img src="http://raw.github.com/supercowpowers/workbench/master/images/warning.jpg" 
		alt="robot"  width="60px" align="left" style="margin-right:10px;"/>

.. warning:: Caution!: The repository contains malcious data samples, be careful, exclude the workbench directory from AV, etc...

::

	git clone https://github.com/supercowpowers/workbench.git


Become a Developer
------------------
Workbench uses the 'GitHub Flow' model: `GitHub Flow <http://scottchacon.com/2011/08/31/github-flow.html>`_ 

- To work on something new, create a descriptively named branch off of master (ie: my-awesome)
- Commit to that branch locally and regularly push your work to the same named branch on the server
- When you need feedback or help, or you think the branch is ready for merging, open a pull request
- After someone else has reviewed and signed off on the feature, you can merge it into master

Getting Started
~~~~~~~~~~~~~~~
	- Fork the repo on GitHub
	- git clone git@github.com:your_name_here/workbench.git
	
New Feature or Bug
~~~~~~~~~~~~~~~~~~

	::
	
		$ git checkout -b my-awesome
		$ git push -u origin my-awesome
		$ <code for a bit>; git push
		$ <code for a bit>; git push
		$ tox (this will run all the tests)
	
	- Go to github and hit 'New pull request'
	- Someone reviews it and says 'AOK'
	- Merge the pull request (green button)

Tips
----
- Any questions/issue please join us on either the Email Forums or Gitter :)


PyPI Checklist (Senior Dev Stuff)
---------------------------------
- Spin up a fresh Python Virtual Environment
- Make a git branch called 'v0.2.2-alpha' or whatever

.. warning:: Make sure workbench/data/memory_images/exemplar4.vmem isn’t there, remove if necessary!

::

	$ pip install -e .
	$ python setup.py sdist
	$ cd dist
	$ tar xzvf workbench-0.x.y.tar.gz
	$ cd workbench-0.x.y/
	$ python setup.py install
	$ workbench

- look at output, make sure EVERYTHING comes up okay
- quit workbench (ctrl-c in the server window)

::

	$ pip install tox
	$ tox (pass all tests)

- change version in workbench/__init__.py
- change version in setup.py
- Update HISTORY.rst

::

	$ python setup.py publish

- Spin up another fresh Python Virtual Environment

::

	$ pip install workbench
	$ workbench (in one terminal)
	$ pip install pytest-cov
	$ cd workbench/workers
	$ ./runtests (in another terminal)

- Push the version branch
- Go to git do a PR
- Wait for green build and merge
- Create a new release with the same version (v0.2.2-alpha or whatever)
- Claim success!
