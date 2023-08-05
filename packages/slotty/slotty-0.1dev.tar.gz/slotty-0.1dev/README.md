# Bootstrap

In order to start developement it is a good idea to first create a virtual environment.

1. Your nix like system normally comes pre installed with easy\_install. You may also have pip
   installed. If not do so: 
	Ubuntu:
	sudo apt-get install python-pip
   or an equivalant way of installing it on your machine.
2. Running bootstrap.sh will create a virtual environment,
   install the dependencies and set up your local workspace
   as package resource, so that changes in your source are instantly
   reflected. You don't have to install your packge over and over again

After the bootstrapper created your virtual environment and installed 
all dependencies you are ready to run/develop the app.

# Configuring

The app has severall configuration files

* `server_setup.py` for gunicorn
* the environment variable `SLOTTY_CONFIG_FILE` beeing used as `debug.py` for debug settings
  and defaults to `slotty.config` in production use

# Running

Activate the virtual environment and run the webserver. You can pass in every option gunicorn can handle
	source .slotty/bin/activate && ./start-server.sh

or run the debug server
	source .slotty/bin/activate && ./start-server.sh

Wait some seconds and it will start to generate some fictional random race data.


# Goals

1. Have Fun!
2. Use AngularJS, Bootstrap or some other sophisticated technologi
3. Use socketIO to be backwards compatible to this old browser stuff
4. Use some decent Document Store. Maybe couchdb or redis or mongodb or something completely differnt. 
   For now json files or a one file key-value store is sufficient
5. Create a modular and easily extendible Soltcar Racing Web Management System and create some Community to write plugins
6. Listen to collaborators!
7. Manage the collaboration!
8. Did I mention fun?


# Resources

[flask](http://flask.pocoo.org/docs/)
[setuptools - for plugins](http://pythonhosted.org/setuptools/pkg_resources.html?highlight=load_entry_point#entry-points)
[markdown](http://daringfireball.net/projects/markdown/syntax)
[gunicron](http://docs.gunicorn.org/en/latest/index.html)
[gevent](http://www.gevent.org/) [gevent-socketio](https://gevent-socketio.readthedocs.org/en/latest/)
[gevent-websocket](https://pypi.python.org/pypi/gevent-websocket)
[pyzmq](http://zeromq.github.io/pyzmq/)

## Investigate

[libwebsocket](http://libwebsockets.org/trac/libwebsockets)
[flask-classy](http://pythonhosted.org/Flask-Classy/)
[flask-sqlalchemy](http://pythonhosted.org/Flask-SQLAlchemy/quickstart.html)
[flask-themes](http://pythonhosted.org/Flask-Themes/)
[flask-zen](http://pythonhosted.org/Flask-Zen/)
[flask-babel](http://pythonhosted.org/Flask-Babel/)
[flask-couchdb](http://pythonhosted.org/Flask-CouchDB/)
[flask-oauth](http://pythonhosted.org/Flask-OAuth/)
[flask-openid](http://pythonhosted.org/Flask-OpenID/)
[flask-debugtoolbar](http://flask-debugtoolbar.readthedocs.org/en/latest/)
[three.js](http://threejs.org/)
[shifty](http://jeremyckahn.github.io/shifty/)
[clara.io](http://clara.io/)
[shapesmith](http://shapesmith.net)
[lagoa](http://home.lagoa.com)
[tridiv](http://tridiv.com)
[sculpteo](http://www.sculpteo.com/)
[ipython](http://ipython.org/)
[ipython intro](http://opentechschool.github.io/python-data-intro/core/notebook.html)
[labnotebook](https://github.com/cboettig/labnotebook)
[couchdb notebook manager](https://gist.github.com/zylinqk/4107048)
[rackspace and openspace notebook manager](https://github.com/rgbkrk/bookstore/blob/master/bookstore/swift.py)
[remote notebook](http://ipython.org/ipython-doc/rel-1.1.0/interactive/public_server.html)
[remote notebook 2](http://www.windowsazure.com/en-us/documentation/articles/virtual-machines-python-ipython-notebook/)
[ipython sql](https://github.com/catherinedevlin/ipython-sql)
[import notebooks](http://nbviewer.ipython.org/gist/minrk/6011986)
