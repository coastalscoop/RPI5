# RPI5

sudo apt install python3-opencv
sudo apt install python3-bleak %Scanner BLE
pip install scikit-build --break-system-packages
sudo apt-get install cmake
sudo pip install TheengsDecoder --break-system-packages


LIVOX:
git clone https://github.com/Livox-SDK/Livox-SDK.git
cd Livox-SDK
cd build && cmake ..
make
# Note for make I had to add #include <memory> on both the /home/picam_blast/Livox-SDK/sdk_core/src/base/thread_base.cpp & /home/picam_blast/Livox-SDK/sdk_core/src/base/thread_base.h files
sudo make install
