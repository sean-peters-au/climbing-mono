# Install OpenMVG dependencies
brew install open-mvg
brew install eigen ceres-solver flann cereal openexr

# Build OpenMVG
git clone --recursive https://github.com/openMVG/openMVG.git
cd openMVG
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=RELEASE -G "Xcode" ../src
xcodebuild -configuration Release

cmake ../src \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_ARCHITECTURES=arm64

make -j$(sysctl -n hw.ncpu)

sudo make install
cd ../..  # Return to poc/board-photogrammetry

# Install OpenMVS dependencies
brew install boost eigen opencv cgal
brew install glew glfw
git clone https://github.com/cnr-isti-vclab/vcglib.git

# Build OpenMVS
git clone https://github.com/cdcseacave/openMVS.git
cd openMVS
mkdir -p build && cd build
VCG_PATH=$(pwd)/../../vcglib
cmake .. -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_OSX_ARCHITECTURES=arm64 \
    -DVCG_ROOT=$VCG_PATH \
    -DOpenMVS_USE_CUDA=OFF

make -j$(sysctl -n hw.ncpu)
sudo make install