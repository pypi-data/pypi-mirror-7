PLATFORM_OPTS = -Wl,--export-dynamic
PYTHON = /usr/include/python2.7
CXXFLAGS = -fPIC
# -g3 -O0
BOOST_INC = /usr/include
BOOST_LIB = /usr/lib
TARGET = pyserpent
COMMON_OBJS = bignum.o util.o tokenize.o lllparser.o parser.o rewriter.o compiler.o funcs.o
HEADERS = bignum.h util.h tokenize.h lllparser.h parser.h rewriter.h compiler.h funcs.h
PYTHON_VERSION = 2.7

all: serpent $(TARGET).so

serpent : serpentc lib 

lib:
	ar rvs libserpent.a $(COMMON_OBJS) 

serpentc: $(COMMON_OBJS) cmdline.o
	rm -rf serpent
	g++ -Wall $(COMMON_OBJS) cmdline.o -o serpent

bignum.o : bignum.cpp bignum.h

util.o : util.cpp util.h bignum.o

tokenize.o : tokenize.cpp tokenize.h util.o

lllparser.o : lllparser.cpp lllparser.h tokenize.o util.o

parser.o : parser.cpp parser.h tokenize.o util.o

rewriter.o : rewriter.cpp rewriter.h lllparser.o util.o

compiler.o : compiler.cpp compiler.h util.o

funcs.o : funcs.cpp funcs.h

cmdline.o: cmdline.cpp

clean:
	rm -f serpent *\.o $(TARGET).so libserpent.a

$(TARGET).so: $(TARGET).o
	g++ $(CXXFLAGS) -shared $(PLATFORM_OPTS) $(TARGET).o -L$(BOOST_LIB) -lboost_python -L/usr/lib/python$(PYTHON_VERSION)/config -lpython$(PYTHON_VERSION) $(COMMON_OBJS) -o $(TARGET).so
 
$(TARGET).o: $(TARGET).cpp $(COMMON_OBJS)
	g++ $(CXXFLAGS) -I$(PYTHON) -I$(BOOST_INC) -c $(TARGET).cpp

install:
	cp serpent /usr/local/bin
	cp libserpent.a /usr/local/lib
	rm -r /usr/local/include/libserpent
	mkdir -p /usr/local/include/libserpent
	cp $(HEADERS) /usr/local/include/libserpent
	cp pyserpent.so /usr/lib/python2.7/lib-dynload/
