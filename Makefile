CXX=g++
CFLAGS=-fPIC
INC=-Isrc/gco_cpp -Isrc/gco

all: libcgco.so test_wrapper

libcgco.so: \
    src/gco_cpp/LinkedBlockList.o src/gco_cpp/graph.o src/gco_cpp/maxflow.o \
        src/gco_cpp/GCoptimization.o cgco.o
	$(CXX) -shared $(CFLAGS) \
	    src/gco_cpp/LinkedBlockList.o \
	    src/gco_cpp/graph.o \
	    src/gco_cpp/maxflow.o \
	    src/gco_cpp/GCoptimization.o \
	    cgco.o \
	    -o libcgco.so

gco.so: \
    src/gco_cpp/LinkedBlockList.o src/gco_cpp/graph.o src/gco_cpp/maxflow.o \
        src/gco_cpp/GCoptimization.o
	$(CXX) -shared $(CFLAGS) src/gco_cpp/LinkedBlockList.o \
	    src/gco_cpp/graph.o \
	    src/gco_cpp/maxflow.o \
	    src/gco_cpp/GCoptimization.o -o gco.so

src/gco_cpp/LinkedBlockList.o: \
    src/gco_cpp/LinkedBlockList.cpp \
        src/gco_cpp/LinkedBlockList.h
	$(CXX) $(CFLAGS) $(INC) \
	    -c src/gco_cpp/LinkedBlockList.cpp \
	    -o src/gco_cpp/LinkedBlockList.o

src/gco_cpp/graph.o: \
    src/gco_cpp/graph.cpp src/gco_cpp/graph.h src/gco_cpp/block.h
	$(CXX) $(CFLAGS) $(INC) \
	    -c -x c++ src/gco_cpp/graph.cpp \
	    -o src/gco_cpp/graph.o

src/gco_cpp/maxflow.o: \
    src/gco_cpp/block.h src/gco_cpp/graph.h src/gco_cpp/maxflow.cpp
	$(CXX) $(CFLAGS) $(INC) \
	    -c -x c++ src/gco_cpp/maxflow.cpp \
	    -o src/gco_cpp/maxflow.o

src/gco_cpp/GCoptimization.o: \
    src/gco_cpp/GCoptimization.cpp src/gco_cpp/GCoptimization.h \
        src/gco_cpp/LinkedBlockList.h src/gco_cpp/energy.h src/gco_cpp/graph.h \
        src/gco_cpp/graph.o src/gco_cpp/maxflow.o
	$(CXX) $(CFLAGS) $(INC) \
	    -c src/gco_cpp/GCoptimization.cpp \
	    -o src/gco_cpp/GCoptimization.o

cgco.o: \
    src/gco/cgco.cpp src/gco_cpp/GCoptimization.h
	$(CXX) $(CFLAGS) $(INC) \
	    -c src/gco/cgco.cpp \
	    -o cgco.o

test_wrapper: \
    tests/test_wrapper.cpp
	$(CXX) $(INC) -L. tests/test_wrapper.cpp \
	    -o test_wrapper -Wl,-rpath,. -lcgco

clean:
	rm -f *.o src/gco_cpp/*.o test_wrapper

rm:
	rm -f *.o *.so src/gco_cpp/*.o *.zip test_wrapper

download:
	wget -N -O gco-v3.0.zip http://vision.csd.uwo.ca/code/gco-v3.0.zip
	unzip -o gco-v3.0.zip -d  ./src/gco_cpp
