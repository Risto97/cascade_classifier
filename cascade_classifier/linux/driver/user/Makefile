CC = gcc
SRCS = detect.c
SHROBJ = detect.so

$(SHROBJ):$(SRCS)
	$(CC) -shared -o $(SHROBJ) -fPIC $(SRCS) -o $(SHROBJ)
clean:
	rm -rf main *.o *.gch *.so
