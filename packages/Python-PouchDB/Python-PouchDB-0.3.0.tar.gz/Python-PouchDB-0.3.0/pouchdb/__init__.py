#	Copyright 2013-2014, Marten de Vries
#
#	Licensed under the Apache License, Version 2.0 (the "License");
#	you may not use this file except in compliance with the License.
#	You may obtain a copy of the License at
#
#	http://www.apache.org/licenses/LICENSE-2.0
#
#	Unless required by applicable law or agreed to in writing, software
#	distributed under the License is distributed on an "AS IS" BASIS,
#	WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#	See the License for the specific language governing permissions and
#	limitations under the License.

"""`Python-PouchDB <http://python-pouchdb.marten-de-vries.nl>`_ is a
Python wrapper for the `PouchDB JavaScript library
<http://pouchdb.com/>`_. This module mostly mirrors `its API
<http://pouchdb.com/api.html>`_.

Python-PouchDB uses Qt to wrap PouchDB. This means you need one of its
Python bindings: PySide, PyQt4 or PyQt5. When multiple are installed,
it uses the one which is already imported at the time the
:py:mod:`pouchdb` module is imported (or chooses one itself when none
are).

There are two API's: one asynchronous one, which almost directly maps
functions to their JavaScript equivalents and supports both promises and
callbacks in most cases, and a synchronous one, which doesn't have a
JavaScript equivalent, but might be easier to use in at least scripts.

API examples
============

Synchronous:

	>>> environment = pouchdb.setup()
	>>> db = environment.PouchDB('example')
	>>> doc = db.get('my_example_doc')

Asynchronous:

	>>> def callback(err, resp):
	...     print("inside callback:", resp)
	... 
	>>> db = pouchdb.PouchDB('example')
	>>> db.post({}, callback)
	>>> #or db.post({}).then(callback), with the 'err' argument removed from the callback function.
	... #QtGui.QApplication.instance().processEvents()
	... #a few more times... Alternatively, you could run the event loop
	... #blocking using the `QtGui.QApplication.exec_` method.
	>>> QtGui.QApplication.instance().processEvents()
	('inside callback:', {u'ok': True, u'rev': u'1-a7ee7ce33fc13fcd4070fe30a2b19df2', u'id': u'79D24A39-C78A-4F6B-BDF3-AD0928B67D00'})

Since the asynchronous and synchronous api have the same methods, those
methods are documented in abstract base classes:
:py:class:`AbstractEnvironment` and :py:class:`AbstractPouchDB`. Their
subclasses (:py:class:`AsyncEnvironment`, :py:class:`SyncEnvironment`,
:py:class:`AsyncPouchDB` and :py:class:`SyncPouchDB`) are the ones
actually available in the API.

Unsupported PouchDB APIs
========================

The wrapper that wraps Python-PouchDB isn't advanced enough to get a
return value of a Python function called from JavaScript. In most cases
this is no problem, but this prevents three things that you might expect
to work.

- It's not possible to pass a Python function reference as argument in
  the :py:meth:`AbstractPouchDB.query`. JavaScript functions and design
  doc paths are of course fine.
- It's not possible to pass database objects into the replicate
  functions. :py:meth:`AbstractPouchDB.replicate_from` and
  :py:meth:`AbstractPouchDB.replicate_to` allow you to use at least one
  :py:class:`AbstractPouchDB` object though, so you shouldn't have any
  problems because of this.
- It's not possible to write a PouchDB plugin in Python. In other words,
  ``PouchDB.plugin`` isn't implemented. But seriously, why would you
  ever want to do that anyway?

It's not impossible to fix this restriction, it's just not something
that has a very high priority. Patches welcome!

Other unsupported things:

- Accessing ``PouchDB.prefix`` - Python-PouchDB is run in an isolated
  environment, accessing/changing it makes no sense. The value for the
  property is set by Python-PouchDB to be an empty string. (No _pouch_!)

"""

from . import context
from . import utils
from .info import __author__, __version__, __copyright__

import itertools
import functools
import os
import abc
import contextlib

_IGNORED_ERRORS = [
	"ArrayBuffer values are deprecated in Blob Constructor.",
]

def _to_blob(bytes):
	return {
		"type": "_py_blob",
		"data": bytes,
	}

def _getPromiseResponse(ctx, promise):
	returned = {}
	def success(resp):
		returned["resp"] = resp
	def fail(err):
		returned["err"] = err

	promise.then(success, fail)
	ctx.waitUntilCalled([success, fail])

	if returned.get("err"):
		raise PouchDBError(returned["err"])
	return returned["resp"]

@contextlib.contextmanager
def _getting_callback_result(ctx):
	returning = {}
	def callback(err=None, resp=None):
		returning["err"] = err
		returning["resp"] = resp
	info = {"callback": callback}
	yield info
	ctx.waitUntilCalled(callback)
	if returning.get("err"):
		raise PouchDBError(returning["err"])
	info["resp"] = returning["resp"]

def _filterNone(args):
	return [a for a in args if a is not None]

class AbstractPouchDB(object):
	"""**Never** instantiate this class or one of its subclasses
	yourself. Create an environment using the :py:func:`setup` function
	instead, and then use its :py:attr:`AbstractEnvironment.PouchDB`
	attribute, with the arguments specified at :py:meth:`__init__`.

	Extra (optional) options for all ``AbstractPouchDB.validating*``
	methods compared to their normal ``AbstractPouchDB.*`` counterparts
	are:

	- ``secObj``: e.g.::

		{
			"admins": {
				"names": [],
				"roles": []
			},
			"members": {
				"names": [],
				"roles": []
			}
		}

	- ``userCtx``: e.g.::

		{
			"db": "test_db",
			"name": "username",
			"roles": [
				"_admin"
			]
		}

	"""
	__metaclass__ = abc.ABCMeta

	_idCounter = itertools.count()

	def __init__(self, _ctx, name=None, **options):
		"""This method creates a database or opens an existing one. If
		you use a URL like http://domain.com/dbname then Python-PouchDB
		will work as a client to an online CouchDB instance. Otherwise
		it will create a local database using the WebSQL backend.

		"""
		self._ctx = _ctx
		self._id = next(self._idCounter)

		self._ctx.newObject(self._id, name, options)

	def _asyncCall(self, methodName, *args):
		return self._ctx.call(self._id, methodName, *_filterNone(args))

	@abc.abstractmethod #pragma: no branch
	def destroy(self):
		"""Delete database."""

	@abc.abstractmethod #pragma: no branch
	def put(self, doc, id=None, rev=None, **options):
		"""Create a new document or update an existing document. If the
		document already exists, you must specify its revision ``_rev``,
		otherwise a conflict will occur.

		"""

	@abc.abstractmethod #pragma: no branch
	def post(self, doc, **options):
		"""Create a new document and let PouchDB generate an ``_id`` for
		it.

		"""

	@abc.abstractmethod #pragma: no branch
	def get(self, docid, **options):
		"""Retrieves a document, specified by ``docid``."""

	@abc.abstractmethod #pragma: no branch
	def remove(self, doc, **options):
		"""Deletes the document. doc is required to be a document with
		at least an ``_id`` and a ``_rev`` property. Sending the full
		document will work as well.

		"""

	@abc.abstractmethod #pragma: no branch
	def bulkDocs(self, docs, **options):
		"""Modify, create or delete multiple documents. The docs
		argument is an object with property docs which is an array of
		documents. You can also specify a new_edits property on the
		docs object that when set to false allows you to post existing
		documents.

		If you omit an ``_id`` parameter on a given document, the
		database will create a new document and assign the ID for you.
		To update a document, you must include both an ``_id`` parameter
		and a ``_rev`` parameter, which should match the ID and revision
		of the document on which to base your updates. Finally, to
		delete a document, include a ``_deleted`` parameter with the
		value ``True``.

		"""

	@abc.abstractmethod #pragma: no branch
	def allDocs(self, **options):
		"""Fetch multiple documents. Deleted documents are only included
		if ``keys`` is specified.

		"""

	@abc.abstractmethod #pragma: no branch
	def changes(self, **options):
		"""A list of changes made to documents in the database, in the
		order they were made. It returns an object with one method
		cancel, which you call if you don't want to listen to new
		changes anymore. ``onChange`` will be be called for each change
		that is encountered.

		"""

	@abc.abstractmethod #pragma: no branch
	def replicate_to(self, remoteDB, **options):
		"""A shorthand for :py:meth:`AbstractEnvironment.replicate`"""

	@abc.abstractmethod #pragma: no branch
	def replicate_from(self, remoteDB, **options):
		"""A shorthand for :py:meth:`AbstractEnvironment.replicate`"""

	@abc.abstractmethod #pragma: no branch
	def sync(self, remoteDB, **options):
		"""A shorthand for :py:meth:`AbstractEnvironment.sync`"""

	@abc.abstractmethod #pragma: no branch
	def putAttachment(self, docId, attachmentId, doc, type, rev=None):
		"""Attaches a binary object to a document. Most of
		Python-PouchDB's API deals with JSON, but if you're dealing
		with large binary data (such as PNGs), you may incur a
		performance or storage penalty if you simply include them as
		base64- or hex-encoded strings. In these cases, you can store
		the binary data as an attachment.

		Be aware that the argument order is different than in PouchDB
		due to the ``rev`` argument being optional. Byte strings replace
		blobs in Python-PouchDB. (e.g. b"Hello World!")

		"""

	@abc.abstractmethod #pragma: no branch
	def getAttachment(self, docId, attachmentId, **options):
		"""Get attachment data. Returns a dictionary with the following
		format::

			{
				"data": b"Bytes as byte string",
				"type": "text/plain"
			}

		"""

	@abc.abstractmethod #pragma: no branch
	def removeAttachment(self, docId, attachmentId, rev):
		"""Delete an attachment from a doc."""

	@abc.abstractmethod #pragma: no branch
	def query(self, fun, **options):
		"""Retrieves a view, which allows you to perform more complex
		queries on Python-PouchDB. The CouchDB documentation for map/
		reduce applies to Python-PouchDB.

		Since views perform a full scan of all documents, this method
		may be slow, unless you first save your view in a design
		document.

		"""

	@abc.abstractmethod #pragma: no branch
	def info(self):
		"""Get information about a database."""

	@abc.abstractmethod #pragma: no branch
	def compact(self):
		"""Runs compaction of the database. Fires callback when
		compaction is done. If you use the http adapter and have
		specified a callback, Pouch will ping the remote database in
		regular intervals unless the compaction is finished.

		"""

	@abc.abstractmethod #pragma: no branch
	def revsDiff(self, diff):
		"""Given a set of document/revision IDs, returns the subset of
		those that do not correspond to revisions stored in the
		database. Primarily used in replication.

		"""

	#gql plugin
	@abc.abstractmethod #pragma: no branch
	def gql(self, query, **options):
		"""	Uses the GQL PouchDB plugin. Check out `its documentation
		<http://pouchdb.com/gql.html>`_.

		The Google Query Language (GQL) interface provides an
		alternative method for accessing data. The version of GQL
		implemented here is based on the `Google Visualization API Query
		Language
		<https://developers.google.com/chart/interactive/docs/querylanguage>`_.

		The syntax of GQL queries should be familiar to those who have
		used SQL, but the capabilities of GQL are much more limited.

		"""

	#geopouch plugin
	@abc.abstractmethod #pragma: no branch
	def spatial(self, fun, **options):
		"""Same as requesting ``_spatial`` in CouchDB when GeoCouch is
		installed. Wraps the geopouch plugin.

		"""

	#search plugin
	@abc.abstractmethod #pragma: no branch
	def search(self, func, **options):
		"""Wraps the pouchdb-search plugin"""

	#validation plugin
	@abc.abstractmethod #pragma: no branch
	def validatingPut(self, doc, id=None, rev=None, **options):
		"""Same as :py:meth:`put`, but validates like in CouchDB. Wraps
		the validation PouchDB plugin.
		"""

	@abc.abstractmethod #pragma: no branch
	def validatingPost(self, doc, **options):
		"""Same as :py:meth:`post`, but validates like in CouchDB. Wraps
		the validation PouchDB plugin.

		"""

	@abc.abstractmethod #pragma: no branch
	def validatingRemove(self, doc, **options):
		"""Same as :py:meth:`remove`, but validates like in CouchDB.
		Wraps the validation PouchDB plugin.

		"""

	@abc.abstractmethod #pragma: no branch
	def validatingBulkDocs(self, docs, **options):
		"""Same as :py:meth:`bulkDocs`, but validates like in CouchDB.
		Wraps the validation PouchDB plugin.

		"""

	@abc.abstractmethod #pragma: no branch
	def validatingPutAttachment(self, docId, attachmentId, doc, type, rev=None, **options):
		"""Same as :py:meth:`putAttachment`, but validates like in
		CouchDB. Wraps the validation PouchDB plugin.

		"""

	@abc.abstractmethod #pragma: no branch
	def validatingRemoveAttachment(self, docId, attachmentId, rev, **options):
		"""Same as :py:meth:`removeAttachment`, but validates like in
		CouchDB. Wraps the validation PouchDB plugin.

		"""

	#show plugin - experimental so private for now
	@abc.abstractmethod #pragma: no branch
	def show(self, showPath, **options):
		"""Same as requesting ``_show`` in CouchDB. Wraps the show
		PouchDB plugin.

		"""

	#list plugin - experimental so private for now
	@abc.abstractmethod #pragma: no branch
	def list(self, listPath, **options):
		"""Same as requesting ``_list`` in CouchDB. Wraps the list
		PouchDB plugin.

		"""

	#update plugin - experimental so private for now
	@abc.abstractmethod #pragma: no branch
	def _updatingPut(self, query, **options):
		"""Same as sending a PUT to ``_update`` in CouchDB. Wraps the
		update PouchDB plugin.

		"""

	@abc.abstractmethod #pragma: no branch
	def _updatingPost(self, query, **options):
		"""Same as sending a POST to ``_update`` in CouchDB. Wraps the
		update PouchDB plugin.

		"""

class SyncPouchDB(AbstractPouchDB):
	def _syncCall(self, methodName, *args):
		promise = self._ctx.call(self._id, methodName, *_filterNone(args))
		return _getPromiseResponse(self._ctx, promise)

	def destroy(self):
		return self._syncCall("destroy")

	def put(self, doc, id=None, rev=None, **options):
		return self._syncCall("put", doc, id, rev, options)

	def post(self, doc, **options):
		return self._syncCall("post", doc, options)

	def get(self, docid, **options):
		return self._syncCall("get", docid, options)

	def remove(self, doc, **options):
		return self._syncCall("remove", doc, options)

	def bulkDocs(self, docs, **options):
		return self._syncCall("bulkDocs", docs, options)

	def allDocs(self, **options):
		return self._syncCall("allDocs", options)

	def changes(self, **options):
		"""When the ``live`` or ``continuous`` option is active, this
		method acts like its asynchronous equivalent.

		"""
		return self._callFunc(options)("changes", options)

	def _callFunc(self, options):
		if options.get("live", False) or options.get("continuous", False):
			return self._asyncCall
		return self._syncCall

	def replicate_to(self, remoteDB, **options):
		"""When the ``live`` or ``continuous`` option is active, this
		method acts like its asynchronous equivalent.

		"""
		return self._callFunc(options)("replicate.to", remoteDB, options)

	def replicate_from(self, remoteDB, **options):
		"""When the ``live`` or ``continuous`` option is active, this
		method acts like its asynchronous equivalent.

		"""
		return self._callFunc(options)("replicate.from", remoteDB, options)

	def sync(self, remoteDB, **options):
		"""When the ``live`` or ``continuous`` option is active, this
		method acts like its asynchronous equivalent.

		"""
		return self._callFunc(options)("replicate.sync", remoteDB, options)

	def putAttachment(self, docId, attachmentId, doc, type, rev=None):
		return self._syncCall("putAttachment", docId, attachmentId, rev, _to_blob(doc), type)

	def getAttachment(self, docId, attachmentId, **options):
		return self._syncCall("getAttachment", docId, attachmentId, options)

	def removeAttachment(self, docId, attachmentId, rev):
		return self._syncCall("removeAttachment", docId, attachmentId, rev)

	def query(self, fun, **options):
		return self._syncCall("query", fun, options)

	def info(self):
		return self._syncCall("info")

	def compact(self, **options):
		return self._syncCall("compact", options)

	def revsDiff(self, diff):
		return self._syncCall("revsDiff", diff)

	#gql plugin
	def gql(self, query, **options):
		with _getting_callback_result(self._ctx) as info:
			self._ctx.call(self._id, "gql", query, options, info["callback"])
		return info["resp"]

	#spatial plugin
	def spatial(self, fun, **options):
		return self._syncCall("spatial", fun, options)

	#search plugin
	def search(self, func, **options):
		return self._syncCall("search", func, options)

	#validation plugin
	def validatingPut(self, doc, id=None, rev=None, **options):
		return self._syncCall("validatingPut", doc, id, rev, options)

	def validatingPost(self, doc, **options):
		return self._syncCall("validatingPost", doc, options)

	def validatingRemove(self, doc, **options):
		return self._syncCall("validatingRemove", doc, options)

	def validatingBulkDocs(self, docs, **options):
		return self._syncCall("validatingBulkDocs", docs, options)

	def validatingPutAttachment(self, docId, attachmentId, doc, type, rev=None, **options):
		return self._syncCall("validatingPutAttachment", docId, attachmentId, rev, _to_blob(doc), type, options)

	def validatingRemoveAttachment(self, docId, attachmentId, rev, **options):
		return self._syncCall("validatingRemoveAttachment", docId, attachmentId, rev, options)

	#show plugin
	def show(self, showPath, **options):
		return self._syncCall("show", showPath, options)

	#list plugin
	def list(self, listPath, **options):
		return self._syncCall("list", listPath, options)

	#update plugin
	def _updatingPut(self, query, **options):
		return self._syncCall("updatingPut", query, options)

	def _updatingPost(self, query, **options):
		return self._syncCall("updatingPost", query, options)

class BaseError(Exception):
	"""The base class for all errors this module should raise.

	"""

class EnvironmentError(BaseError):
	"""Raised when something is wrong relating to the environment in
	which Python-PouchDB runs.

	"""

class PouchDBError(BaseError):
	"""All error responses PouchDB would normally give you get raised
	in the form of this error class in Python-PouchDB. You can use get
	item syntax to access properties set on the error object. E.g.:

		>>> try:
		...     ...
		... except pouchdb.PouchDBError as e:
		...    if e["status"] == 404:
		...        print("Not found")
		...    else:
		...        print("Unknown error")

	"""
	def __init__(self, message, *args, **kwargs):
		super(PouchDBError, self).__init__(message, *args, **kwargs)

		self.message = message

	def __getitem__(self, key):
		return self.message[key]

	def __str__(self):
		with utils.suppress(KeyError):
			return self.message["toString"]()
		return str(self.message)

class AsyncPouchDB(AbstractPouchDB):
	"""The GQL plug-in only supports the callback interface, it doesn't
	provide a promise.

	"""
	def destroy(self, callback=None):
		return self._asyncCall("destroy", callback)

	def _handlePutArgs(self, doc, id, rev, callback, options):
		if callable(id):
			callback = id
			id = None
		if callable(rev):
			callback = rev
			rev = None
		return doc, id, rev, options, callback

	def put(self, doc, id=None, rev=None, callback=None, **options):
		return self._asyncCall("put", *self._handlePutArgs(doc, id, rev, callback, options))

	def post(self, doc, callback=None, **options):
		return self._asyncCall("post", doc, options, callback)

	def get(self, docid, callback=None, **options):
		return self._asyncCall("get", docid, options, callback)

	def remove(self, doc, callback=None, **options):
		return self._asyncCall("remove", doc, options, callback)

	def bulkDocs(self, docs, callback=None, **options):
		return self._asyncCall("bulkDocs", docs, options, callback)

	def allDocs(self, callback=None, **options):
		return self._asyncCall("allDocs", options, callback)

	def changes(self, **options):
		return self._asyncCall("changes", options)

	def replicate_to(self, remoteDB, callback=None, **options):
		return self._asyncCall("replicate.to", remoteDB, options, callback)

	def replicate_from(self, remoteDB, callback=None, **options):
		return self._asyncCall("replicate.from", remoteDB, options, callback)

	def sync(self, remoteDB, callback=None, **options):
		return self._asyncCall("replicate.sync", remoteDB, options, callback)

	def putAttachment(self, docId, attachmentId, doc, type, rev=None, callback=None):
		return self._asyncCall("putAttachment", docId, attachmentId, rev, _to_blob(doc), type, callback)

	def getAttachment(self, docId, attachmentId, callback=None, **options):
		return self._asyncCall("getAttachment", docId, attachmentId, options, callback)

	def removeAttachment(self, docId, attachmentId, rev, callback=None):
		return self._asyncCall("removeAttachment", docId, attachmentId, rev, callback)

	def query(self, fun, callback=None, **options):
		return self._asyncCall("query", fun, options, callback)

	def info(self, callback=None):
		return self._asyncCall("info", callback)

	def compact(self, callback=None, **options):
		return self._asyncCall("compact", options, callback)

	def revsDiff(self, diff, callback=None):
		return self._asyncCall("revsDiff", diff, callback)

	#gql plugin
	def gql(self, query, callback=None, **options):
		return self._asyncCall("gql", query, options, callback)

	#spatial plugin
	def spatial(self, fun, callback=None, **options):
		return self._asyncCall("spatial", fun, options, callback)

	#search plugin
	def search(self, func, callback=None, **options):
		return self._asyncCall("search", func, options, callback)

	#validation functions
	def validatingPut(self, doc, id=None, rev=None, callback=None, **options):
		return self._asyncCall("validatingPut", *self._handlePutArgs(doc, id, rev, callback, options))

	def validatingPost(self, doc, callback=None, **options):
		return self._asyncCall("validatingPost", doc, options, callback)

	def validatingRemove(self, doc, callback=None, **options):
		return self._asyncCall("validatingRemove", doc, options, callback)

	def validatingBulkDocs(self, docs, callback=None, **options):
		return self._asyncCall("validatingBulkDocs", docs, options, callback)

	def validatingPutAttachment(self, docId, attachmentId, doc, type, rev=None, callback=None, **options):
		return self._asyncCall("validatingPutAttachment", docId, attachmentId, _to_blob(doc), type, rev, options, callback)

	def validatingRemoveAttachment(self, docId, attachmentId, rev, callback=None, **options):
		return self._asyncCall("validatingRemoveAttachment", docId, attachmentId, rev, options, callback)

	#show plugin
	def show(self, showPath, callback=None, **options):
		return self._asyncCall("show", showPath, options, callback)

	#list plugin
	def list(self, listPath, callback=None, **options):
		return self._asyncCall("list", listPath, options, callback)

	#update plugin
	def _updatingPut(self, query, callback=None, **options):
		return self._asyncCall("updatingPut", query, options, callback)

	def _updatingPost(self, query, callback=None, **options):
		return self._asyncCall("updatingPost", query, options, callback)

class AbstractEnvironment(object):
	"""The environment is `an event emitter
	<http://nodejs.org/api/events.html#events_class_events_eventemitter>`_
	and will emit a 'created' event when a database is created. A
	'destroy' event is emited when a database is destroyed.

	**Don't** instantiate this class or one of its subclasses
	yourself, use the :py:func:`setup` function instead.
	"""
	__metaclass__ = abc.ABCMeta

	#A placeholder value when uninstantiated for sphinxdoc.
	PouchDB = "<subclass of AbstractPouchDB (approximately)>"

	@abc.abstractmethod #pragma: no branch
	def __init__(self, PouchDB, ctx, *args, **kwargs):
		super(AbstractEnvironment, self).__init__(*args, **kwargs)

		self._ctx = ctx

		#:The PouchDB class that you can use to make a new database
		#:instance. You should always use this: **never** instantiate
		#::py:class:`SyncPouchDB` or :py:class:`AsyncPouchDB` manually.
		self.PouchDB = functools.partial(PouchDB, self._ctx)

	def _asyncCall(self, methodName, *args):
		return self._ctx.callStatic(methodName, *_filterNone(args))

	@property
	def POUCHDB_VERSION(self):
		"""The value of what is ``PouchDB.version`` in JavaScript, in
		other words, the version of PouchDB that Python-PouchDB wraps.

		"""
		return self._ctx.staticProperty("version")

	@abc.abstractmethod #pragma: no branch
	def destroy(self, name_=None, **options):
		"""Allows you to destroy a database without creating a new 
		PouchDB instance first.

		The ``name`` argument in PouchDB is called `name_` in
		Python-PouchDB, to prevent a clash with the ``options["name"]``
		argument. In JavaScript where there are no keyword arguments the
		problem doesn't exist, in Python it does, hence the change.

		"""

	@abc.abstractmethod #pragma: no branch
	def replicate(self, source, target, **options):
		"""Replicate data from source to target. Both the source and
		target can be a string representing a CouchDB database url or
		the name a local PouchDB database. If ``live`` is true, then
		this will track future changes and also replicate them
		automatically.

		"""

	@abc.abstractmethod #pragma: no branch
	def sync(self, source, target, **options):
		"""Sync data from ``source`` to ``target`` and ``target`` to
		``source``. This is a convience method for bidirectional data
		replication.

		"""

	@property
	def context(self):
		"""Allows access to the internals of Python-Pouch; only useful
		for debugging purposes. E.g. :py:attr:`context`.inspect() and
		:py:attr:`context`.waitUntilCalled(). The last is used by the
		test suite.

		"""
		return self._ctx

	#event emitter methods
	def addListener(self, event, listener):
		"""Adds a listener to the end of the listeners array for the
		specified event.

		"""
		return self._ctx.callStatic("addListener", event, listener)

	def emit(self, event, *args):
		"""Execute each of the listeners in order with the supplied
		``args``. Returns ``True`` if event had listeners, ``False``
		otherwise.

		"""
		return self._asyncCall("emit", event, *args)

	def listeners(self, event):
		"""Returns an array of listeners for the specified event."""

		return self._asyncCall("listeners", event)

	on = addListener

	def once(self, event, listener):
		"""Adds a one time listener for the event. This listener is
		invoked only the next time the event is fired, after which it
		is removed.

		"""
		return self._asyncCall("once", event, listener)

	def removeListener(self, event, listener):
		"""Remove a listener from the listener array for the specified
		event. Caution: changes array indices in the listener array
		behind the listener.

		"""
		return self._asyncCall("removeListener", event, listener)

	def removeAllListeners(self, event=None):
		"""Removes all listeners, or those of the specified event."""

		return self._asyncCall("removeAllListeners", event)

	def setMaxListeners(self, n):
		"""By default EventEmitters will print a warning if more than 10
		listeners are added for a particular event. This is a useful
		default which helps finding memory leaks. Obviously not all
		Emitters should be limited to 10. This function allows that
		to be increased. Set to zero for unlimited.

		"""
		return self._asyncCall("setMaxListeners", n)

class AsyncEnvironment(AbstractEnvironment):
	def __init__(self, *args, **kwargs):
		super(AsyncEnvironment, self).__init__(AsyncPouchDB, *args, **kwargs)		

	def destroy(self, name_=None, callback=None, **options):
		if callable(name_):
			callback = name_
			name_ = None
		return self._asyncCall("destroy", name_, options, callback)

	def replicate(self, source, target, **options):
		return self._asyncCall("replicate", source, target, options)

	def sync(self, source, target, **options):
		return self._asyncCall("sync", source, target, options)

class SyncEnvironment(AbstractEnvironment):
	def __init__(self, *args, **kwargs):
		super(SyncEnvironment, self).__init__(SyncPouchDB, *args, **kwargs)		

	def _syncCall(self, methodName, *args):
		promise = self._ctx.callStatic(methodName, *_filterNone(args))
		return _getPromiseResponse(self._ctx, promise)

	def _callFunc(self, options):
		if options.get("live", False) or options.get("continuous", False):
			return self._asyncCall
		return self._syncCall

	def destroy(self, name_=None, **options):
		self._syncCall("destroy", name_, options)

	def replicate(self, source, target, **options):
		"""When the ``live`` or ``continuous`` option is active, this
		method acts like its asynchronous equivalent.

		"""
		return self._callFunc(options)("replicate", source, target, options)

	def sync(self, source, target, **options):
		"""When the ``live`` or ``continuous`` option is active, this
		method acts like its asynchronous equivalent.

		"""
		return self._callFunc(options)("sync", source, target, options)

#Caching prevents identical environments from being created which saves
#quite a bit of memory and CPU. On top of that, a reference to every
#environment needs to be kept anyway to prevent segfaulting.
_envs = {}
def setup(storageDir="dbs", async=False, baseUrl="file:///"):
	"""Sets up an environment which allows access to the rest of the
	API, which mostly consists out of wrappers around PouchDB's
	functions. This environment is then returned to the user.

	Depending on the ``async`` parameter, this is either an instance of
	:py:class:`SyncEnvironment` or :py:class:`AsyncEnvironment`. Can
	raise an :py:exc:`EnvironmentError` when a ``storageDir`` other than
	one used earlier is passed in as a parameter. (That's a Qt
	restriction, unfortunately.)

	The ``storageDir`` is created automatically if it doesn't already
	exist. It can be relative, and should be a directory (not a file).
	It's where databases are saved (or more specific: WebKit's backend
	database files).

	In older versions of QtWebKit, the same-origin policy is a little
	too strict which makes it impossible to replicate with databases
	that aren't on the same domain as ``baseUrl``. In newer versions, as
	long as ``baseUrl`` is file:///, this problem doesn't exist. When
	you need to support the older version, you can set this to a domain
	so you can at least replicate to one site.

	"""
	if not (storageDir, async, baseUrl) in _envs:
		js = _getJs()
		try:
			ctx = context.JSContext(js, "PouchDB", _IGNORED_ERRORS, storageDir, baseUrl)
		except ValueError, e:
			if "offlineStoragePath" in str(e): #pragma: no branch
				raise EnvironmentError("Can't use the value '%s' for storageDir. It has already been set to something else and, because of a backend restriction, can't be changed." % storageDir)
			#this shouldn't happen, it's just there so if it does happen
			#during development sometime in the future, the error is
			#shown in a nicer way.
			raise #pragma: no cover

		Environment = AsyncEnvironment if async else SyncEnvironment
		_envs[(storageDir, async, baseUrl)] = Environment(ctx)
	return _envs[(storageDir, async, baseUrl)]

def _getJs(_cache={}):
	if not "js" in _cache:
		jsPath = os.path.join(os.path.dirname(__file__), "bundle.js")
		with open(jsPath) as f:
			_cache["js"] = f.read()
	return _cache["js"]
