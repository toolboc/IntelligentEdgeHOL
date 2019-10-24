FROM jetson-jax-l4t-cuda-cudnn-opencv

RUN apt update && apt install -y libcanberra-gtk-module && \
    rm -rf /var/lib/apt/lists/* 


ENV CUDA_HOME=/usr/local/cuda
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64
ENV PATH=$PATH:$CUDA_HOME/bin

#GET Darknet sources
WORKDIR /usr/local/src
RUN git clone https://github.com/AlexeyAB/darknet.git && \
    cd darknet && \
    sed -i 's/GPU=0/GPU=1/g' Makefile && \
    sed -i 's/CUDNN=0/CUDNN=1/g' Makefile && \
    sed -i 's/CUDNN_HALF=0/CUDNN_HALF=1/g' Makefile && \
    sed -i 's/OPENCV=0/OPENCV=1/g' Makefile && \
    sed -i 's/LIBSO=0/LIBSO=1/g' Makefile && \
    sed -i '/arch=compute_72/s/^#.//g' Makefile && \
    make

RUN cd darknet && LD_LIBRARY_PATH=./:$LD_LIBRARY_PATH     