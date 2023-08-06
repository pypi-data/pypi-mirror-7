XAPIAN_INCLUDE = /usr/local/xapian/include
XAPIAN_LIB = /usr/local/xapian/lib
XAPIAN_SRC_BINDING = /data0/sources/xapian-bindings
XAPIAN_CORE_BINDING = /data0/sources/xapian-core
PATHON_INCLUDE = /usr/include/python2.6

all:
	/usr/local/bin/swig -python -c++ -I./include -I/usr/local/include -I$(XAPIAN_INCLUDE) -I$(XAPIAN_CORE_BINDING) -I$(XAPIAN_SRC_BINDING) -I$(XAPIAN_SRC_BINDING)/python swig/distanceKeyMaker.i
	g++ -o swig/distanceKeyMaker_wrap.o -c swig/distanceKeyMaker_wrap.cxx -I$(PATHON_INCLUDE) -I./include -I/usr/local/include -I$(XAPIAN_INCLUDE) -I$(XAPIAN_CORE_BINDING) -fPIC 
	g++ -o src/distanceKeyMaker.o -c src/distanceKeyMaker.cpp -I$(PATHON_INCLUDE) -I./include -I/usr/local/include -I$(XAPIAN_INCLUDE) -I$(XAPIAN_CORE_BINDING) -fPIC 
	g++ -shared swig/distanceKeyMaker_wrap.o src/distanceKeyMaker.o -L/usr/lib -L/usr/local/lib -L$(XAPIAN_LIB) -lxapian -o swig/_distanceKeyMaker.so

clean:
	rm -rf swig/_distanceKeyMaker.so src/*.o swig/*.o
