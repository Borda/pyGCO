CXX=g++
CFLAGS=-fPIC
INC=-Igco_source -Igco

all: libcgco.so test_wrapper

libcgco.so: \
    gco_source/LinkedBlockList.o gco_source/graph.o gco_source/maxflow.o \
        gco_source/GCoptimization.o cgco.o
	$(CXX) -shared $(CFLAGS) \
	    gco_source/LinkedBlockList.o \
	    gco_source/graph.o \
	    gco_source/maxflow.o \
	    gco_source/GCoptimization.o \
	    cgco.o \
	    -o libcgco.so

gco.so: \
    gco_source/LinkedBlockList.o gco_source/graph.o gco_source/maxflow.o \
        gco_source/GCoptimization.o
	$(CXX) -shared $(CFLAGS) gco_source/LinkedBlockList.o \
	    gco_source/graph.o \
	    gco_source/maxflow.o \
	    gco_source/GCoptimization.o -o gco.so

gco_source/LinkedBlockList.o: \
    gco_source/LinkedBlockList.cpp \
        gco_source/LinkedBlockList.h
	$(CXX) $(CFLAGS) $(INC) \
	    -c gco_source/LinkedBlockList.cpp \
	    -o gco_source/LinkedBlockList.o

gco_source/graph.o: \
    gco_source/graph.cpp gco_source/graph.h gco_source/block.h
	$(CXX) $(CFLAGS) $(INC) \
	    -c -x c++ gco_source/graph.cpp \
	    -o gco_source/graph.o

gco_source/maxflow.o: \
    gco_source/block.h gco_source/graph.h gco_source/maxflow.cpp
	$(CXX) $(CFLAGS) $(INC) \
	    -c -x c++ gco_source/maxflow.cpp \
	    -o gco_source/maxflow.o

gco_source/GCoptimization.o: \
    gco_source/GCoptimization.cpp gco_source/GCoptimization.h \
        gco_source/LinkedBlockList.h gco_source/energy.h gco_source/graph.h \
        gco_source/graph.o gco_source/maxflow.o
	$(CXX) $(CFLAGS) $(INC) \
	    -c gco_source/GCoptimization.cpp \
	    -o gco_source/GCoptimization.o

cgco.o: \
    gco/cgco.cpp gco_source/GCoptimization.h
	$(CXX) $(CFLAGS) $(INC) \
	    -c gco/cgco.cpp \
	    -o cgco.o

test_wrapper: \
    test_wrapper.cpp
	$(CXX) $(INC) -L. tests/test_wrapper.cpp \
	    -o test_wrapper -Wl,-rpath,. -lcgco

clean:
	rm -f *.o gco_source/*.o test_wrapper

rm:
	rm -f *.o *.so gco_source/*.o *.zip test_wrapper

download:
	wget -N -O gco-v3.0.zip http://vision.csd.uwo.ca/code/gco-v3.0.zip
	unzip -o gco-v3.0.zip -d  ./gco_source
