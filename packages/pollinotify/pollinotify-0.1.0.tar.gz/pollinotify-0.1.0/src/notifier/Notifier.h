/*
 * Notifier.h
 *
 *  Created on: 28 Jun 2014
 *      Author: julianporter
 */

#ifndef NOTIFIER_H_
#define NOTIFIER_H_


#include <string>
#include <stdint.h>
#include <list>
#include <map>
#include <sys/inotify.h>
#include <poll.h>
#include <exception>
#include <sstream>
#include <unistd.h>
#include <errno.h>

#include <notifier/Mask.h>

#define INOTIFY_EVENT_SIZE (sizeof(struct inotify_event))
#define INOTIFY_BUFLEN (1024 * (INOTIFY_EVENT_SIZE + 16))


namespace notify {




class NotifyException : public std::exception
{
protected:
	std::string message;
	int error;
public:
	NotifyException(const std::string & msg, int err) : std::exception(), message(msg), error(err) {};
	virtual ~NotifyException() throw() {};
	virtual const char * what() const throw() {
		std::stringstream out;
		out << message << " Error number: " << error;
		return out.str().c_str();
	};
	int errorNumber(){ return error; };
};




struct Event {
public:
	Mask mask;
	std::string path;

	Event(mask_t m,std::string p) : mask(m), path(p) {};
	Event(const Event &m) : mask(m.mask), path(m.path) {};
	Event() : mask(), path() {};

	bool matches(mask_t m) { return mask.matches(m); };
	bool writtenTo() { return mask.matches(Mask::CloseWrite); };
	mask_t code() { return mask.code(); };

	friend std::ostream & operator <<(std::ostream & stream,Event & e);
};

std::ostream & operator <<(std::ostream & stream,Event & e);

typedef uint32_t watch_t;

struct Watch {
public:
	watch_t id;
	mask_t mask;
	std::string path;

	Watch(watch_t w,mask_t m,std::string p) : id(w), mask(m), path(p) {};
	Watch(const Watch &m) : id(m.id), mask(m.mask), path(m.path) {};
	Watch() : id(0), mask(0), path() {};

};


typedef std::list<Event> events_t;
typedef std::map<watch_t,Watch> watches_t;
typedef std::list<Watch> watchset_t;

class Notifier {
private:
	int fd;
	std::size_t nevents;
	watches_t watches;
	events_t events;
public:

	Notifier();
	virtual ~Notifier() { Close(); };

	void addPath(std::string path,mask_t mode=Mask::AllEvents);
	std::size_t nPaths() { return watches.size(); };
	events_t getEvents() { return events_t(events); };
	std::size_t nEvents() { return nevents; };
	bool waitForEvent(unsigned int timeout=0);
	void Close() { close(fd); };



};

} /* namespace inotify */

#endif /* NOTIFIER_H_ */
