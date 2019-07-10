FROM toolboc/jetson-nano-l4t-cuda

# NVIDIA CUDA Deep Neural Network library (cuDNN)

ENV CUDNN_VERSION 7.3.1.28

ENV CUDNN_PKG_VERSION=${CUDA_VERSION}-1

LABEL com.nvidia.cudnn.version="${CUDNN_VERSION}"

ARG libcudnn7_URL=https://onedrive.live.com/download?cid=54AD8562A32D8752&resid=54AD8562A32D8752%21376196&authkey=ADTDdL0bhMWq4vM
ARG libcudnn7_dev_URL=https://onedrive.live.com/download?cid=54AD8562A32D8752&resid=54AD8562A32D8752%21376197&authkey=APizXm-di7JPR0Y
ARG libcudnn7_doc_URL=https://onedrive.live.com/download?cid=54AD8562A32D8752&resid=54AD8562A32D8752%21376195&authkey=ADqH53K9oRnkO-8

RUN curl -sL $libcudnn7_URL -o libcudnn7_$CUDNN_VERSION-1+cuda10.0_arm64.deb && \
    echo "92867c0a495f84ec11d108f84b776620 libcudnn7_$CUDNN_VERSION-1+cuda10.0_arm64.deb" | md5sum -c - && \
    dpkg -i libcudnn7_$CUDNN_VERSION-1+cuda10.0_arm64.deb && \
    rm libcudnn7_$CUDNN_VERSION-1+cuda10.0_arm64.deb

RUN curl -sL $libcudnn7_dev_URL -o libcudnn7-dev_$CUDNN_VERSION-1+cuda10.0_arm64.deb && \
    echo "dd0fbfa225b2374b946febc98e2cdec4 libcudnn7-dev_$CUDNN_VERSION-1+cuda10.0_arm64.deb" | md5sum -c - && \
    dpkg -i libcudnn7-dev_$CUDNN_VERSION-1+cuda10.0_arm64.deb && \
    rm libcudnn7-dev_$CUDNN_VERSION-1+cuda10.0_arm64.deb

RUN curl -sL $libcudnn7_doc_URL -o libcudnn7-doc_$CUDNN_VERSION-1+cuda10.0_arm64.deb && \
    echo "9478c16ceeaaca937d4d26b982e48bd1 libcudnn7-doc_$CUDNN_VERSION-1+cuda10.0_arm64.deb" | md5sum -c - && \
    dpkg -i libcudnn7-doc_$CUDNN_VERSION-1+cuda10.0_arm64.deb && \
    rm libcudnn7-doc_$CUDNN_VERSION-1+cuda10.0_arm64.deb