all: main
	./main

main:main.o image_utils.o cascade_utils.o
	g++ -o main main.o image_utils.o cascade_utils.o

main.o:main.cpp slika.hpp image_utils.hpp cascade.hpp cascade_utils.hpp
	g++ -c main.cpp slika.hpp image_utils.hpp cascade.hpp cascade_utils.hpp

cascade_utils.o:cascade_utils.cpp cascade_utils.hpp image_utils.hpp cascade.hpp
	g++ -c cascade_utils.cpp cascade_utils.hpp image_utils.hpp cascade.hpp

image_utils.o:image_utils.cpp image_utils.hpp slika.hpp
	g++ -c image_utils.cpp image_utils.hpp slika.hpp

clean:
	rm -rf main *.o *.gch

# 	./main
