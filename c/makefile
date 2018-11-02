all: main
	./main


# main:main.cpp
# 	g++ main.cpp -o main --std=c++11 -Ofast
main:main.o image_utils.o cascade_utils.o
	g++ -pthread main.o image_utils.o cascade_utils.o -o main --std=gnu++11 -Ofast

main.o:main.cpp slika.hpp image_utils.hpp cascade.hpp cascade_utils.hpp
	g++ -c main.cpp slika.hpp image_utils.hpp cascade.hpp cascade_utils.hpp --std=gnu++11 -Ofast

cascade_utils.o:cascade_utils.cpp cascade_utils.hpp image_utils.hpp cascade.hpp
	g++ -c cascade_utils.cpp cascade_utils.hpp image_utils.hpp cascade.hpp --std=gnu++11 -Ofast

image_utils.o:image_utils.cpp image_utils.hpp slika.hpp
	g++ -c image_utils.cpp image_utils.hpp slika.hpp --std=gnu++11 -Ofast

clean:
	rm -rf main *.o *.gch

# 	./main
