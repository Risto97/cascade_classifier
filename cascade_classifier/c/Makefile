CC = g++
CFLAGS = --std=gnu++11 -Ofast
SRCS = cascade_utils.cpp image_utils.cpp
HDRS = cascade.hpp cascade_utils.hpp image_utils.hpp sqrt.hpp
SHROBJ = cascade.so

$(SHROBJ):$(SRCS)
	python dump_headers.py
	$(CC) -shared -o $(SHROBJ) -fPIC $(SRCS) $(HDRS) $(CFLAGS) -o $(SHROBJ)
clean:
	rm -rf main *.o *.gch *.so
