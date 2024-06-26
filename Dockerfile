ARG BASE_IMG='ubuntu:22.04'

FROM ${BASE_IMG}
SHELL ["/bin/bash", "-ci"]

# Timezone Configuration
ENV TZ=Europe/Moscow
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone
ENV DEBIAN_FRONTEND=noninteractive

RUN apt update && apt upgrade -y
RUN apt install -y git tmux python3 python3-dev xorg-dev libx11-dev openbox xauth curl libusb-1.0-0-dev -y

RUN git config --global http.postBuffer 157286400
RUN git clone https://github.com/IntelRealSense/librealsense.git
WORKDIR librealsense
RUN apt install cmake make build-essential -y
RUN apt install libssl-dev -y
RUN apt install libglfw3-dev libgl1-mesa-dev libglu1-mesa-dev -y
RUN mkdir build && cd build && \ 
    cmake ../ -DFORCE_RSUSB_BACKEND=ON \
    -DBUILD_PYTHON_BINDINGS:bool=true \
    -DPYTHON_EXECUTABLE=/usr/bin/python3 \
    -DCMAKE_BUILD_TYPE=release \
    -DBUILD_EXAMPLES=true \
    -DBUILD_GRAPHICAL_EXAMPLES=true  \
    && make -j2 && make install
ENV PYTHONPATH=$PYTHONPATH:/librealsense/build/release
RUN mkdir -p /etc/udev/rules.d/ \
    && cp config/99-realsense-libusb.rules /etc/udev/rules.d/ \
    && cp config/99-realsense-d4xx-mipi-dfu.rules /etc/udev/rules.d/

RUN apt update && apt install -y \
    git vim curl nano tmux curl wget lsb-release \
    net-tools build-essential gcc g++ \
    cmake clang make \
    gnupg2 ca-certificates software-properties-common \
    libboost-dev libeigen3-dev libcppunit-dev \
    python3 python3-dev libpython3-dev python3-pip \
    python3-distutils python3-psutil python3-future \
    freeglut3-dev mesa-utils libusb-1.0-0-dev libopencv-dev libcanberra-gtk-module && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /workspace

RUN git clone --branch v1.5.1 https://github.com/orocos/orocos_kinematics_dynamics.git && \
    cd orocos_kinematics_dynamics && git submodule update --init && \
    cd /workspace/orocos_kinematics_dynamics/orocos_kdl && mkdir build && cd build && \
    cmake .. && make && make install && \
    cd /workspace/orocos_kinematics_dynamics/python_orocos_kdl && mkdir build && cd build && \
    cmake .. && make && make install && \
    export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib && \
    echo "export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/lib" >> ~/.bashrc && \
    ldconfig


WORKDIR /workspace/painter_reborn
COPY . /workspace/painter_reborn

RUN pip3 install -r requirements.txt
RUN pip3 install -i https://test.pypi.org/simple/ UDriver
RUN pip3 install -e .

ENV LD_LIBRARY_PATH=/usr/local/lib
