CC = g++
CFLAGS = --std=gnu++11 -Ofast
SRCS = main.cpp cascade_utils.cpp image_utils.cpp
HDRS = cascade.hpp cascade_utils.hpp image_utils.hpp
PROG = main

OPENCV = `pkg-config opencv --cflags --libs`
LIBS = $(OPENCV)

all: $(PROG)
	./$(PROG)

$(PROG):$(SRCS)
	$(CC) $(CFLAGS) -o $(PROG) $(SRCS) $(LIBS)

clean:
	rm -rf main *.o *.gch
