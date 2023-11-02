mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE='Release' -DCMAKE_OSX_ARCHITECTURES='x86_64;arm64;arm64e' -DCMAKE_INSTALL_PREFIX='../install' -DLIBOMP_ENABLE_SHARED=OFF ..
make -j8 install
