FROM toolboc/jetson-nano-l4t

#INSTALL CUDA Toolkit for L4T
ARG URL=https://onedrive.live.com/download?cid=54AD8562A32D8752&resid=54AD8562A32D8752%21376191&authkey=APwtvHgdqlgnJzo
ARG CUDA_TOOLKIT_PKG="cuda-repo-l4t-10-0-local-10.0.166_1.0-1_arm64.deb"

RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    curl -sL ${URL} -o ${CUDA_TOOLKIT_PKG} && \
    echo "5e3eedc3707305f9022d41754d6becde ${CUDA_TOOLKIT_PKG}" | md5sum -c - && \
    dpkg --force-all -i ${CUDA_TOOLKIT_PKG} && \
    rm ${CUDA_TOOLKIT_PKG} && \
    apt-key add var/cuda-repo-*-local*/*.pub && \
    apt-get update && \
    apt-get install -y --allow-downgrades cuda-toolkit-10-0 libgomp1 libfreeimage-dev libopenmpi-dev openmpi-bin && \
    dpkg --purge cuda-repo-l4t-10-0-local-10.0.166  && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

ENV CUDA_HOME=/usr/local/cuda
ENV LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/cuda/lib64:/usr/local/cuda/extras/CUPTI/lib64
ENV PATH=$PATH:$CUDA_HOME/bin
