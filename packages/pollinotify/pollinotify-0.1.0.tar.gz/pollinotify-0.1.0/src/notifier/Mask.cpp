/*
 * Mask.cpp
 *
 *  Created on: 29 Jun 2014
 *      Author: julianporter
 */

#include <notifier/Mask.h>
#include <iomanip>

namespace notify {

bool Mask::initialised=false;
maskset_t Mask::names;



void Mask::init() {
	names=maskset_t();

	names[Access]="Access";
	names[Modify]="Modify";
	names[Attributes]="Attributes";
	names[CloseWrite]="CloseWrite";
	names[CloseOther]="CloseOther";
	names[Open]="Open";
	names[MoveFrom]="MoveFrom";
	names[MoveTo]="MoveTo";
	names[Create]="Create";
	names[Delete]="Delete";
	names[DirEvent]="DirEvent";
	names[Overflow]="Overflow";
	names[Ignored]="Ignored";

	initialised=true;
}

std::list<std::string> Mask::decode() {
	if(!Mask::initialised) Mask::init();

	std::list<std::string> out;
	for(maskset_t::iterator it=names.begin();it!=names.end();it++) {
		maskval_t value=*it;
		if(matches(value.first)) {
			out.push_back(value.second);
		}
	}
	return out;
}

std::ostream & operator <<(std::ostream & stream,Mask & m) {
	stream << std::hex << std::setfill('0') << std::setw(8) << m.mask << std::setfill(' ') << std::setw(0) << std::dec;
	return stream;
}

} /* namespace inotify */
