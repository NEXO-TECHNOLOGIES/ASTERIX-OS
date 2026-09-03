# =====================================================================
# ASTERIX OS - Native C++ Utilities Makefile
# =====================================================================

CXX    ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra -pthread -D_GNU_SOURCE
DESTDIR  ?= /usr/local/bin

all: bin/asterix-packetcraft bin/asterix-vulnscan bin/asterix-logwatch

bin/asterix-packetcraft: src/asterix-packetcraft.cpp
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) $< -o $@

bin/asterix-vulnscan: src/asterix-vulnscan.cpp
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) $< -o $@

bin/asterix-logwatch: src/asterix-logwatch.cpp
	@mkdir -p bin
	$(CXX) $(CXXFLAGS) $< -o $@

install: all
	@mkdir -p $(DESTDIR)
	cp -f bin/* $(DESTDIR)/
	chmod 755 $(DESTDIR)/asterix-packetcraft \
	          $(DESTDIR)/asterix-vulnscan \
	          $(DESTDIR)/asterix-logwatch
	@echo "[✔] C++ utilities installed to $(DESTDIR)"

clean:
	rm -rf bin
