FROM l4t:32.2-jax-jetpack-4.2.1-devel

#Required for libjasper-dev
RUN echo "deb http://ports.ubuntu.com/ubuntu-ports/ xenial-security main restricted" | sudo tee -a /etc/apt/sources.list

#INSTALL OPENCV dependencies
RUN apt update && apt purge *libopencv* -y && apt install -y build-essential cmake git libgtk2.0-dev pkg-config libavcodec-dev libavformat-dev libswscale-dev \
    libgstreamer1.0-dev libgstreamer-plugins-base1.0-dev \
    python2.7-dev python3.6-dev python-dev python-numpy python3-numpy \
    libtbb2 libtbb-dev libjpeg-dev libpng-dev libtiff-dev libjasper-dev libdc1394-22-dev \
    libv4l-dev v4l-utils qv4l2 v4l2ucp \
    curl unzip && \
    rm -rf /var/lib/apt/lists/*

#GET OPENCV sources
WORKDIR /usr/local/src
RUN curl -L https://github.com/opencv/opencv/archive/4.1.0.zip -o opencv-4.1.0.zip && \
    curl -L https://github.com/opencv/opencv_contrib/archive/4.1.0.zip -o opencv_contrib-4.1.0.zip && \
    unzip opencv-4.1.0.zip && \
    unzip opencv_contrib-4.1.0.zip && \
    rm -rf opencv*.zip

#INSTALL OPENCV
RUN cd opencv-4.1.0/ && mkdir release && cd release/ && \
    cmake -D OPENCV_GENERATE_PKGCONFIG=ON -D OPENCV_PC_FILE_NAME=opencv.pc -D WITH_CUDA=ON -D CUDA_ARCH_BIN="5.3" -D CUDA_ARCH_PTX="" -D OPENCV_EXTRA_MODULES_PATH=../../opencv_contrib-4.1.0/modules -D WITH_GSTREAMER=ON -D WITH_LIBV4L=ON -D BUILD_opencv_python2=ON -D BUILD_opencv_python3=ON -D BUILD_TESTS=OFF -D BUILD_PERF_TESTS=OFF -D BUILD_EXAMPLES=OFF -D CMAKE_BUILD_TYPE=RELEASE -D CMAKE_INSTALL_PREFIX=/usr/local .. && \
    make -j3 && \
    make install && \
    cp unix-install/opencv.pc /usr/local/lib/pkgconfig && \
    rm -rf /usr/local/src/opencv-4.1.0

RUN ldconfig
