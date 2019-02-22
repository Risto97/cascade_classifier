CC = g++
SRCS = detect.c
# HDRS = cascade.hpp cascade_utils.hpp image_utils.hpp sqrt.hpp
SHROBJ = detect.so

$(SHROBJ):$(SRCS)
	$(CC) -shared -o $(SHROBJ) -fPIC $(SRCS) -o $(SHROBJ)
clean:
	rm -rf main *.o *.gch *.so
