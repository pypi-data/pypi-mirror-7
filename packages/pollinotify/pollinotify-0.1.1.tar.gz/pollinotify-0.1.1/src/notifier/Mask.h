/*
 * Mask.h
 *
 *  Created on: 29 Jun 2014
 *      Author: julianporter
 */

#ifndef MASK_H_
#define MASK_H_

#include <sys/inotify.h>
#include <iostream>
#include <map>
#include <list>

namespace notify {

typedef unsigned int mask_t;
typedef std::map<mask_t,std::string> maskset_t;
typedef std::pair<mask_t,std::string> maskval_t;

class Mask {
	public:
		const static mask_t Access		= IN_ACCESS;
		const static mask_t Modify		= IN_MODIFY;
		const static mask_t Attributes	= IN_ATTRIB;
		const static mask_t CloseWrite	= IN_CLOSE_WRITE;
		const static mask_t CloseOther 	= IN_CLOSE_NOWRITE;
		const static mask_t Close		= IN_CLOSE;
		const static mask_t Open		= IN_OPEN;
		const static mask_t MoveFrom	= IN_MOVED_FROM;
		const static mask_t MoveTo		= IN_MOVED_TO;
		const static mask_t Move 		= IN_MOVE;
		const static mask_t Create		= IN_CREATE;
		const static mask_t Delete		= IN_DELETE;
		const static mask_t DeleteSelf 	= IN_DELETE_SELF;
		const static mask_t MoveSelf   	= IN_MOVE_SELF;
		const static mask_t DirEvent	= IN_ISDIR;
		const static mask_t AllEvents	= IN_ALL_EVENTS;

		const static mask_t Unmounted	= IN_UNMOUNT;
		const static mask_t Overflow	= IN_Q_OVERFLOW;
		const static mask_t Ignored		= IN_IGNORED;


		Mask(mask_t m) : mask(m) {};
		Mask(const Mask &other) : mask(other.mask) {};
		Mask() : mask(0) {};
		virtual ~Mask() {};

		std::list<std::string> decode();
		bool matches(mask_t match) { return ((match & mask) != 0);};
		mask_t code() { return mask; };

		friend std::ostream & operator <<(std::ostream & stream,Mask & m);

	private:


		mask_t mask;

		static bool initialised;
		static maskset_t names;
		static void init();

	};

std::ostream & operator <<(std::ostream & stream,Mask & m);

} /* namespace inotify */

#endif /* MASK_H_ */
