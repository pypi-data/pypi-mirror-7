/*
 * INotify.cpp
 *
 *  Created on: 30 Jun 2014
 *      Author: julianporter
 */

#include <python/INotify.h>
#include <stdexcept>
#include <sstream>

template<class T>
PyObject *listToPy(typename std::list<T> in,PyObject *(*transformer)(T))
{
	PyObject *out=PyList_New((Py_ssize_t)0);
	if(out==NULL) {
		PyErr_SetString(PyExc_SystemError,"Internal error allocating FileEvent list");
		return NULL;
	};

	for(typename std::list<T>::iterator it=in.begin();it!=in.end();it++) {
		PyObject *item=transformer(*it);

		int r=PyList_Append(out,item);
		if(r<0) {
			PyErr_SetString(PyExc_SystemError,"Internal error building FileEvent list");
			return NULL;
		}
	}
	return out;
}

static PyMethodDef ModuleMethods[]={
		{"maskAsString",maskAsString,METH_VARARGS,"String representation of a mask"},
		{NULL,NULL,0,NULL}
};

PyMODINIT_FUNC initnotify() {

	inotify_WatcherType.tp_new = PyType_GenericNew;
	if (PyType_Ready(&inotify_WatcherType) < 0) return;

	inotify_FileEventType.tp_new = PyType_GenericNew;
		if (PyType_Ready(&inotify_FileEventType) < 0) return;

	PyObject *m=Py_InitModule3(ModuleName,ModuleMethods,"Library providing interface to file system notification service");
	if(!m) return;

	Py_INCREF(&inotify_WatcherType);
	PyModule_AddObject(m,"Watcher",(PyObject *)&inotify_WatcherType);

	Py_INCREF(&inotify_FileEventType);
	PyModule_AddObject(m,"FileEvent",(PyObject *)&inotify_FileEventType);

	INotifyError = PyErr_NewException((char *)ErrorName,NULL,NULL);
	PyModule_AddObject(m,"NotifyError",INotifyError);

	PyModule_AddIntConstant(m,"Access",Access);
	PyModule_AddIntConstant(m,"Modify",Modify);
	PyModule_AddIntConstant(m,"Attributes",Attributes);
	PyModule_AddIntConstant(m,"CloseWrite",CloseWrite);
	PyModule_AddIntConstant(m,"CloseOther",CloseOther);
	PyModule_AddIntConstant(m,"MoveFrom",MoveFrom);
	PyModule_AddIntConstant(m,"MoveTo",MoveTo);
	PyModule_AddIntConstant(m,"Create",Create);
	PyModule_AddIntConstant(m,"Delete",Delete);
	PyModule_AddIntConstant(m,"DirEvent",DirEvent);
	PyModule_AddIntConstant(m,"Ignored",Ignored);
	PyModule_AddIntConstant(m,"AllEvents",AllEvents);

};






/* Class methods */

// Creation

 PyObject *Watcher_new(PyTypeObject *type,PyObject *args,PyObject *keywords) {
	Watcher *self;

	 self = (Watcher *)type->tp_alloc(type, 0);
	 if (self != NULL) {
		 self->notify = NULL;
	 }
	 return (PyObject *)self;
}

// Release

 void Watcher_dealloc(Watcher *self) {
	if(self->notify) {
		delete self->notify;
	}
    self->ob_type->tp_free((PyObject*)self);
}

// Initialisation


 int Watcher_init(Watcher *self,PyObject *args,PyObject *keywords) {
	notify::Notifier *notifier = new notify::Notifier();
	if(notifier==NULL) {
		PyErr_SetString(PyExc_OSError,"Cannot initialise iNotify service");
		return -1;
	}
	self->notify=notifier;
	return 0;
}

// Add path

static const char *arg_mode="mode";
static char *pathKeywords[]={(char *)arg_mode,NULL};

 PyObject * Watcher_addPath(Watcher *self,PyObject *args,PyObject *keywords) {

	const char *path;
	unsigned int mode=notify::Mask::AllEvents;
	if(!PyArg_ParseTupleAndKeywords(args,keywords,"s|I",pathKeywords,&path,&mode)) {
		PyErr_SetString(PyExc_ValueError,"Cannot find path argument");
		return NULL;
	}
	try {
		self->notify->addPath(std::string(path),mode);
	}
	catch(...) {
		PyErr_SetString(PyExc_OSError,"Cannot add path to iNotify service");
		return NULL;
	}
	Py_RETURN_NONE;
}

// Poll

static const char *arg_timeout="timeout";
static char *pollKeywords[]={(char *)arg_timeout,NULL};


 PyObject * Watcher_poll(Watcher *self,PyObject *args,PyObject *keywords) {

	unsigned int timeout=0;
	PyArg_ParseTupleAndKeywords(args,keywords,"|I",pollKeywords,&timeout);
	try {
		bool out=self->notify->waitForEvent(timeout);
		if(out) Py_RETURN_TRUE;
		else Py_RETURN_FALSE;
	}
	catch(std::exception & e) {
		PyErr_SetString(PyExc_OSError,"Error polling iNotify service");
		return NULL;
	}
}

// get the events



static const char *arg_match="match";
static char *eventsKeywords[]={(char *)arg_match,NULL};

 PyObject * Watcher_events(Watcher *self,PyObject *args,PyObject *keywords) {

	try {
		unsigned int match=notify::Mask::AllEvents;
		PyArg_ParseTupleAndKeywords(args,keywords,"|I",eventsKeywords,&match);
		std::list<notify::Event> events=self->notify->getEvents();
		PyObject *out=PyList_New((Py_ssize_t)0);
		if(out==NULL) {
			PyErr_SetString(PyExc_SystemError,"Internal error allocating FileEvent list");
			return NULL;
		}

		for(std::list<notify::Event>::iterator it=events.begin();it!=events.end();it++) {
			if(it->matches(match)) {
				FileEvent *event=(FileEvent *)_PyObject_New(&inotify_FileEventType);
				if(event==NULL) {
					PyErr_SetString(PyExc_SystemError,"Internal error allocating FileEvent");
					Py_XDECREF(out);
					return NULL;
				}

				PyObject *path=PyString_FromString(it->path.c_str());
				PyObject *mask=PyInt_FromLong((long)(it->mask.code()));
				if(!path||!mask) {
					PyErr_SetString(PyExc_SystemError,"Internal error allocating FileEvent data");
					Py_XDECREF(out);
					Py_XDECREF(event);
					Py_XDECREF(path);
					Py_XDECREF(mask);
					return NULL;
				}

				event->mask=mask;
				event->path=path;

				int r=PyList_Append(out,(PyObject *)event);
				if(r<0) {
					PyErr_SetString(PyExc_SystemError,"Internal error building FileEvent list");
					Py_XDECREF(out);
					Py_XDECREF(event);
					Py_XDECREF(path);
					Py_XDECREF(mask);
					return NULL;
				}
			}
		}
		return out;
	}
	catch(std::exception & e) {
		PyErr_SetString(PyExc_RuntimeError,e.what());
		return NULL;
	}
}

// Number of paths

 PyObject * Watcher_nPaths(Watcher *self) {
	 try {
		 return PyInt_FromSize_t(self->notify->nPaths());
	 }
	 catch(...) {
		 PyErr_SetString(PyExc_SystemError,"Cannot obtain iNotify service");
		 return  NULL;
	 }
}

// Number of events

 PyObject * Watcher_nEvents(Watcher *self) {
	 try {
		 return PyInt_FromSize_t(self->notify->nEvents());
	 }
	 catch(...) {
		 PyErr_SetString(PyExc_SystemError,"Cannot obtain iNotify service");
		 return NULL;
	 }
}

Py_ssize_t Watcher_len(Watcher *self) {
	try {
			 return (Py_ssize_t)self->notify->nEvents();
		 }
		 catch(...) {
			 PyErr_SetString(PyExc_SystemError,"Cannot obtain iNotify service");
			 return -1;
		 }
}

PyObject * Watcher_getiter(Watcher *self) {
	PyObject *tmp=PyTuple_New(0);
	PyObject *list=Watcher_events(self,tmp,NULL);
	Py_XDECREF(tmp);
	if(list==NULL) {
		return NULL;
	}
	return PyObject_GetIter(list);
}



// Creation

 PyObject *FileEvent_new(PyTypeObject *type,PyObject *args,PyObject *keywords) {

 	FileEvent *self = (FileEvent *)type->tp_alloc(type, 0);
 	if (self==NULL) {
 		PyErr_SetString(PyExc_MemoryError,"Cannot allocate FileEvent object");
 		return NULL;
 	}
 	self->mask=NULL;
 	self->path=NULL;
 	return (PyObject *)self;
 }

 // Release

 void FileEvent_dealloc(FileEvent *self) {
	 Py_XDECREF(self->mask);
	 Py_XDECREF(self->path);
     self->ob_type->tp_free((PyObject*)self);
 }

 // Initialisation


 int FileEvent_init(FileEvent *self,PyObject *args,PyObject *keywords) {
	 PyObject *mask=NULL;
	 PyObject *path=NULL;
	 PyObject *tmp;

	 if(!PyArg_ParseTuple(args,"iS",&mask,&path)) {
		 PyErr_SetString(PyExc_ValueError,"Cannot parse arguments");
		 return -1;
	 }

	 tmp=self->mask;
	 Py_XINCREF(mask);
	 self->mask=mask;
	 Py_XDECREF(tmp);

	 tmp=self->path;
	 Py_XINCREF(path);
	 self->path=path;
	 Py_XDECREF(tmp);

	 return 0;
}

int FileEvent_in(FileEvent *self,PyObject *find) {
	try {
		int match=PyInt_AsLong(find);
		if(match==-1 && PyErr_Occurred()) {
			PyErr_SetString(PyExc_ValueError,"Invalid argument");
			return -1;
		}
		int mask=PyInt_AsLong(self->mask);
		return((match&mask)!=0) ? 1 : 0;
	}
	catch(std::exception &e) {
		std::cout << e.what() << std::endl;
		PyErr_SetString(PyExc_RuntimeError,e.what());
		return -1;
	}
}


PyObject *FileEvent_matches(FileEvent *self,PyObject *args) {
	try {

		PyObject *obj=NULL;
		if(!PyArg_ParseTuple(args,"o",obj)) {
			PyErr_SetString(PyExc_ValueError,"Cannot parse arguments");
			return NULL;
		}

		int matched=FileEvent_in(self,obj);
		Py_XDECREF(obj);
		if(matched<0) return NULL;
		else if(matched>0) Py_RETURN_TRUE;
		else Py_RETURN_FALSE;
	}
	catch(std::exception &e) {
		std::cout << e.what() << std::endl;
		PyErr_SetString(PyExc_RuntimeError,e.what());
		return NULL;
	}
}

std::list<std::string> decode(FileEvent *self) {
	int value=PyInt_AsLong((PyObject *)self->mask);
	notify::Mask mask(value);
	std::list<std::string> decoded=mask.decode();
	return decoded;
}



PyObject *string_transformer(std::string in)
{
	return PyString_FromString(in.c_str());
}

inline PyObject *FileEvent_decode(FileEvent *self) {
	std::list<std::string> decoded=decode(self);
	return listToPy<std::string>(decoded,string_transformer);
}

PyObject *FileEvent_str(FileEvent *self) {
	std::list<std::string> decoded=decode(self);

	std::stringstream out;
	for(std::list<std::string>::iterator it=decoded.begin();it!=decoded.end();it++) {
		if(it!=decoded.begin()) {
			out << " ";
		}
		out << *it;
	}
	PyObject *str=PyString_FromString(out.str().c_str());
	if(str==NULL) {
		PyErr_SetString(PyExc_SystemError,"Cannot allocate string value");
		return NULL;
	}
	return str;
}

Py_ssize_t FileEvent_len(FileEvent *self) {
	std::list<std::string> decoded=decode(self);
	return (Py_ssize_t)decoded.size();
}


/**
 * Functions
 */

PyObject *maskAsString(PyObject *args,PyObject *keywords) {
	int mask;
	if(!PyArg_ParseTuple(args,"I",&mask)) {
		PyErr_SetString(PyExc_ValueError,"Cannot parse arguments");
		return NULL;
	}
	notify::Event e(mask,"");
	std::stringstream stream;
	stream << e;
	PyObject *str=PyString_FromString(stream.str().c_str());
	if(str==NULL) {
		PyErr_SetString(PyExc_SystemError,"Cannot allocate string value");
		return NULL;
	}
	return str;
}








