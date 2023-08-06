%module distanceKeyMaker 
%{

	#include "distanceKeyMaker.h"
	#include <string>
	#include "xapian.h"
	#include "config.h"
%}
%include stl.i
%include "xapian.i"
%include "distanceKeyMaker.h"
%include "config.h"

