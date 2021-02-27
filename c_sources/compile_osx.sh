#!/bin/bash

pyenv shell 3.9.1

LDFLAGS=-L./openmp/lib CPPFLAGS=-I./openmp/include python3 ./setup_osx.py build_ext --inplace
