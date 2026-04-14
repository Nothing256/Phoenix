# Base image: CUDA 12.4.1 + Ubuntu 22.04
FROM nvidia/cuda:12.4.1-cudnn-devel-ubuntu22.04 AS base

ENV TZ=Etc/UTC \
    DEBIAN_FRONTEND=noninteractive \
    CONDA_DIR=/opt/conda \
    SHELL=/bin/bash \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US.UTF-8

RUN usermod -s /bin/bash root

# Install system dependencies (including git for pip source installs)
RUN apt-get update && \
    ln -fs /usr/share/zoneinfo/$TZ /etc/localtime && \
    echo $TZ > /etc/timezone && \
    apt-get install -y tzdata software-properties-common && \
    add-apt-repository -y ppa:ubuntu-toolchain-r/test && \
    apt-get update && \
    apt-get install --only-upgrade -y libstdc++6 && \
    apt-get install -y python3-dev python3-pip wget vim curl net-tools lsof \
        libsm6 libxrender1 libxext-dev unzip git && \
    apt-get install -y libglib2.0-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

FROM base AS build

# Install Miniconda (downloaded at build time)
RUN wget -q https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
        -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p /opt/conda && \
    rm /tmp/miniconda.sh && \
    ln -s /opt/conda/etc/profile.d/conda.sh /etc/profile.d/conda.sh && \
    echo ". /opt/conda/etc/profile.d/conda.sh" >> /opt/conda/etc/profile && \
    echo "conda activate phoenix" >> /opt/conda/etc/profile && \
    echo ". /opt/conda/etc/profile" >> /etc/profile

ENV PATH=$PATH:/opt/conda/bin

RUN conda init bash

# Accept Anaconda Terms of Service (non-interactive)
RUN conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/main && \
    conda tos accept --override-channels --channel https://repo.anaconda.com/pkgs/r

# Create the phoenix conda environment
COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml && \
    conda clean -i -t -y

FROM build AS run

WORKDIR /workspace

# Mount your code and models into /workspace at runtime:
#   docker run --gpus all -v $(pwd):/workspace -v /path/to/models:/workspace/models phoenix
CMD ["/bin/bash", "--login"]
