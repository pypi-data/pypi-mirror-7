/*
 * INotify.h
 *
 *  Created on: 30 Jun 2014
 *      Author: julianporter
 */

#ifndef INOTIFY_H_
#define INOTIFY_H_

#include <python2.7/Python.h>
#include <python2.7/structmember.h>
#include <notifier/Notifier.h>

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif


PyMODINIT_FUNC initnotify();

static const char *ModuleName="pollinotify";
static const char *ErrorName="pollinotify.NotifyError";

static const unsigned int Access		= IN_ACCESS;
static const unsigned int Modify		= IN_MODIFY;
static const unsigned int Attributes	= IN_ATTRIB;
static const unsigned int CloseWrite	= IN_CLOSE_WRITE;
static const unsigned int CloseOther 	= IN_CLOSE_NOWRITE;
static const unsigned int Close			= IN_CLOSE;
static const unsigned int Open			= IN_OPEN;
static const unsigned int MoveFrom		= IN_MOVED_FROM;
static const unsigned int MoveTo		= IN_MOVED_TO;
static const unsigned int Move 			= IN_MOVE;
static const unsigned int Create		= IN_CREATE;
static const unsigned int Delete		= IN_DELETE;
static const unsigned int DeleteSelf 	= IN_DELETE_SELF;
static const unsigned int MoveSelf   	= IN_MOVE_SELF;
static const unsigned int DirEvent		= IN_ISDIR;
static const unsigned int Ignored		= IN_IGNORED;
static const unsigned int AllEvents		= IN_ALL_EVENTS;




static PyObject *INotifyError;

typedef struct {
    PyObject_HEAD
    notify::Notifier *notify;
} Watcher;



static PyObject * Watcher_new(PyTypeObject *type,PyObject *args,PyObject *keywords);
 static void Watcher_dealloc(Watcher *self);
 static int Watcher_init(Watcher *self,PyObject *args,PyObject *keywords);

 static PyObject * Watcher_addPath(Watcher *self,PyObject *args,PyObject *keywords);
 static PyObject * Watcher_poll(Watcher *self,PyObject *args,PyObject *keywords);
 static PyObject * Watcher_events(Watcher *self,PyObject *args,PyObject *keywords);
 static PyObject * Watcher_nPaths(Watcher *self);
 static PyObject * Watcher_nEvents(Watcher *self);

 static Py_ssize_t Watcher_len(Watcher *self);
 static PyObject * Watcher_getiter(Watcher *self);

static PyMethodDef inotify_methods[] = {
		{"addPath",(PyCFunction)Watcher_addPath,METH_KEYWORDS,"Add a path to be watched"},
		{"poll",(PyCFunction)Watcher_poll,METH_KEYWORDS,"Poll for events"},
		{"events",(PyCFunction)Watcher_events,METH_KEYWORDS,"Return all events, optionally matching some mask"},
		{"nPaths",(PyCFunction)Watcher_nPaths,METH_NOARGS,"Number of paths registered to be watched"},
		{"nEvents",(PyCFunction)Watcher_nEvents,METH_NOARGS,"Number of events detected"},
		{NULL}
};

static PyMemberDef inotify_members[] = {
		{(char *)"_notify",T_OBJECT_EX,offsetof(Watcher,notify),READONLY,(char *)"opaque notifier object"},
    {NULL}  /* Sentinel */
};

static PySequenceMethods inotify_sequence = {
		(lenfunc)Watcher_len,			/* sq_length */
		0,								/* sq_concat */
		0,								/* sq_repeat */
		0,								/* sq_item */
		0,								/* sq_slice */
		0,								/* sq_ass_item */
		0,								/* sq_ass_slice */
		0,								/* sq_contains */
		0,								/* sq_inplace_concat */
		0,								/* sq_inplace_repeat */
};

static PyTypeObject inotify_WatcherType = {
    PyObject_HEAD_INIT(NULL)
    0,                         			/*ob_size*/
    "inotify.Watcher",             		/*tp_name*/
    sizeof(Watcher), 					/*tp_basicsize*/
    0,                         			/*tp_itemsize*/
    (destructor)Watcher_dealloc,		/*tp_dealloc*/
    0,                         			/*tp_print*/
	0,                         			/*tp_getattr*/
	0,                         			/*tp_setattr*/
	0,                         			/*tp_compare*/
	0,                         			/*tp_repr*/
	0,                         			/*tp_as_number*/
	&inotify_sequence,                  /*tp_as_sequence*/
	0,                         			/*tp_as_mapping*/
	0,                         			/*tp_hash */
	0,                         			/*tp_call*/
	0,                         			/*tp_str*/
	0,                         			/*tp_getattro*/
	0,                         			/*tp_setattro*/
	0,                         			/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_HAVE_ITER, 				/*tp_flags*/
	"Watcher for inotify service",		/* tp_doc */
	0,   								/* tp_traverse */
	0,           						/* tp_clear */
	0,		               				/* tp_richcompare */
	0,		               				/* tp_weaklistoffset */
	(getiterfunc)Watcher_getiter,		               				/* tp_iter */
	0,		               				/* tp_iternext */
	inotify_methods,             		/* tp_methods */
	inotify_members,             		/* tp_members */
	0,                         			/* tp_getset */
	0,                         			/* tp_base */
	0,                         			/* tp_dict */
	0,                         			/* tp_descr_get */
	0,                         			/* tp_descr_set */
	0,                         			/* tp_dictoffset */
	(initproc)Watcher_init,      		/* tp_init */
	0,                         			/* tp_alloc */
	Watcher_new,                 		/* tp_new */
};

typedef struct {
    PyObject_HEAD
    PyObject *mask;
    PyObject *path;
} FileEvent;

static PyObject * FileEvent_new(PyTypeObject *type,PyObject *args,PyObject *keywords);
 static void FileEvent_dealloc(FileEvent *self);
 static int FileEvent_init(FileEvent *self,PyObject *args,PyObject *keywords);

 static PyObject * FileEvent_decode(FileEvent *self);
 static PyObject * FileEvent_matches(FileEvent *self,PyObject *args);

 static PyObject * FileEvent_str(FileEvent *self);
 static Py_ssize_t FileEvent_len(FileEvent *self);
 static int FileEvent_in(FileEvent *self,PyObject *find);

static PyMethodDef FileEvent_methods[] = {
		{"decode",(PyCFunction)FileEvent_decode,METH_NOARGS,"Decode the mask as a list of strings"},
		{"matches",(PyCFunction)FileEvent_matches,METH_VARARGS,"Does event match a particular mask"},
		{NULL}
};

static PyMemberDef FileEvent_members[] = {
		{(char *)"mask",T_OBJECT_EX,offsetof(FileEvent,mask),READONLY,(char *)"the inotify mask value"},
		{(char *)"path",T_OBJECT_EX,offsetof(FileEvent,path),READONLY,(char *)"the path of the object causing the event"},
    {NULL}  /* Sentinel */
};

static PySequenceMethods FileEvent_sequence = {
		(lenfunc)FileEvent_len,			/* sq_length */
		0,								/* sq_concat */
		0,								/* sq_repeat */
		0,								/* sq_item */
		0,								/* sq_slice */
		0,								/* sq_ass_item */
		0,								/* sq_ass_slice */
		(objobjproc)FileEvent_in,		/* sq_contains */
		0,								/* sq_inplace_concat */
		0,								/* sq_inplace_repeat */
};

static PyTypeObject inotify_FileEventType = {
    PyObject_HEAD_INIT(NULL)
    0,                         			/*ob_size*/
    "inotify.FileEvent",             	/*tp_name*/
    sizeof(FileEvent), 					/*tp_basicsize*/
    0,                         			/*tp_itemsize*/
    (destructor)FileEvent_dealloc,		/*tp_dealloc*/
    0,                         			/*tp_print*/
	0,                         			/*tp_getattr*/
	0,                         			/*tp_setattr*/
	0,                         			/*tp_compare*/
	0,                         			/*tp_repr*/
	0,                         			/*tp_as_number*/
	&FileEvent_sequence,                /*tp_as_sequence*/
	0,                         			/*tp_as_mapping*/
	0,                         			/*tp_hash */
	0,                         			/*tp_call*/
	(reprfunc)FileEvent_str,            /*tp_str*/
	0,                         			/*tp_getattro*/
	0,                         			/*tp_setattro*/
	0,                         			/*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT, 				/*tp_flags*/
	"inotify event mask and path",		/* tp_doc */
	0,   								/* tp_traverse */
	0,           						/* tp_clear */
	0,		               				/* tp_richcompare */
	0,		               				/* tp_weaklistoffset */
	0,		               				/* tp_iter */
	0,		               				/* tp_iternext */
	FileEvent_methods,             		/* tp_methods */
	FileEvent_members,             		/* tp_members */
	0,                         			/* tp_getset */
	0,                         			/* tp_base */
	0,                         			/* tp_dict */
	0,                         			/* tp_descr_get */
	0,                         			/* tp_descr_set */
	0,                         			/* tp_dictoffset */
	(initproc)FileEvent_init,      		/* tp_init */
	0,                         			/* tp_alloc */
	FileEvent_new,                 		/* tp_new */
};

static PyObject *maskAsString(PyObject *args,PyObject *keywords);




#endif /* INOTIFY_H_ */
