/*
 * Notifier.cpp
 *
 *  Created on: 28 Jun 2014
 *      Author: julianporter
 */

#include "Notifier.h"


namespace notify {




std::ostream & operator <<(std::ostream & stream,Event & e) {
	std::list<std::string> out=e.mask.decode();
	for(std::list<std::string>::iterator it=out.begin();it!=out.end();it++) {
		stream << *it << " ";
	}
	return stream;
}


Notifier::Notifier() {
	fd=inotify_init1(IN_NONBLOCK);
	if(fd<0) {
		throw NotifyException("Cannot start service",errno);
	}
	events=events_t();
	watches=watches_t();
	nevents=0;
}




void Notifier::addPath(std::string path,mask_t mode) {
	int n=path.length()-1;
	if(n>=0 && path[n]=='/') {
		path.resize(n);
	}
	int32_t watch=inotify_add_watch(fd,path.c_str(),mode);
	if(watch<0) {
		throw NotifyException("Cannot add path",errno);
	}
	Watch newWatch(watch,mode,path);
	watches[watch]=newWatch;
}

bool Notifier::waitForEvent(unsigned int timeout) {


	struct pollfd pfd = {fd,POLLIN | POLLPRI,0};
	struct pollfd p[]={pfd};
	nevents=poll(p,1,timeout);
	if(p[0].revents & POLLIN) {
		unsigned char buffer[8192];
		unsigned int get=8192;
		unsigned int size=0;
		while(get>0) {
			int got=read(fd,buffer+size,get);
			//std::cout << "Got " << got << " Get " << get << " Size " << size << " N " << nevents << " ERRNO " << errno << std::endl;
			//std::cout.flush();

			if(got<0 && errno!=11) {
				throw NotifyException("Problem reading events",errno);
			}
			get-=got;
			size+=got;
			if(got==0 || errno==11) break;
		}
		events.clear();
		unsigned int pos=0;
		while(pos<size) {
			//std::cout << "Pos " << pos << " Size " << size << std::endl;
			struct inotify_event* event = (struct inotify_event*) &buffer[pos];
			//std::cout << "WD " << event->wd << " NAME " << std::string(event->name,event->len) << " MASK " << event->mask << std::endl;
			Watch watch=watches[event->wd];
			std::stringstream out;
			out << watch.path << "/" << std::string(event->name,event->len);
			Event e(event->mask,out.str());
			events.push_back(e);
			//std::cout << "EVENT " << e << std::endl;
			pos+=sizeof(inotify_event)+event->len;
		}
		return true;
	}
	else return false;
}


} /* namespace inotify */
