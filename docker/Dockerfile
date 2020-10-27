# Copyright (c) Bioinformatics Core Facility of the Max Planck Institute for Biology of Ageing.
# Distributed under the terms of the Modified BSD License.

# Debian buster-slim (10.1) image available on 20 Wednesday 2020.
FROM debian@sha256:11253793361a12861562d1d7b15b8b7e25ac30dd631e3d206ed1ca969bf97b7d

LABEL maintainer "jorge.boucas@age.mpg.de"

USER root

ENV DEBIAN_FRONTEND noninteractive

ENV MODS /modules
ENV SOFT $MODS/software
ENV SOUR $MODS/sources/
ENV MODF $MODS/modulefiles
ENV LOGS $MODS/installation_logs

RUN mkdir -p $SOFT $SOUR $MODF $LOGS $MODF/bioinformatics $MODF/general $MODF/libs

RUN echo "deb http://ftp.debian.org/debian buster main non-free contrib" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian buster main non-free contrib" >> /etc/apt/sources.list && \
echo "deb http://ftp.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list && \
echo "deb-src http://ftp.debian.org/debian buster-updates main contrib non-free" >> /etc/apt/sources.list

RUN REPO=http://cdn-fastly.deb.debian.org && \
echo "deb $REPO/debian buster main\ndeb $REPO/debian-security buster/updates main" > /etc/apt/sources.list && \
apt-get update && apt-get -yq dist-upgrade && \
apt-get install -yq --no-install-recommends locales && \
apt-get clean && rm -rf /var/lib/apt/lists/* && \
echo "en_US.UTF-8 UTF-8" > /etc/locale.gen && locale-gen

RUN apt-get update && \
apt-get install -yq --no-install-recommends \
   libreadline-dev \
   xorg-dev \
   apt-utils \
   wget \
   bzip2 \
   ca-certificates \
   sudo \
   jed \
   emacs \
   build-essential \
   python-dev \
   unzip \
   libsm6 \
   pkg-config \
   pigz \
   zlib1g-dev \
   autoconf \
   automake \
   environment-modules \
   gcc && \
   apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
apt-get install -yq --no-install-recommends \
   f2c \   
   git \
   vim \
   texlive-latex-base \
   texlive-latex-extra \
   texlive-fonts-extra \
   texlive-fonts-recommended \
   pandoc \
   texlive-generic-recommended \
   libxrender1 \
   inkscape \
   libxml2-dev \
   libcurl4-gnutls-dev \
   libatlas3-base \
   libopenblas-base \
   libfreetype6-dev \
   libtool \
   libexpat1-dev \
   libxml2-dev \
   libxslt1-dev && \
   apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
apt-get install -yq --no-install-recommends \ 
   ghostscript \
   gfortran \
   libpcre3 \
   libpcre3-dev \
   libssl-dev \
   libsqlite3-dev \
   libssl-dev \
   libfreetype6-dev \
   libpng-dev \
   liblmdb-dev \
   libmariadb-dev \
   libmariadb-client-lgpl-dev-compat \
   libtbb2 \
   libtbb-dev \
   curl \
   libcurl4 \
   libcurl4-openssl-dev \
   libncurses5-dev \
   libcairo2-dev \
   libtool-bin \
   libzmq3-dev \
   zip && \
   apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
apt-get install -yq --no-install-recommends \ 
   tk \
   tcl \
   openssl \
   libssl-dev \
   libssh2-1-dev \
   libtool \
   libffi-dev \
   ruby \
   ruby-dev \
   make \
   libzmq3-dev \
   libczmq-dev \
   apt-transport-https \
   dirmngr \
   cmake \
   libpam0g-dev \
   lsb-release \
   libedit2 \
   libapparmor1 \
   gnupg \
   liblzma-dev \
   psmisc \
   less \
   libclang-dev \
   libcurl4-openssl-dev && \
   apt-get clean && rm -rf /var/lib/apt/lists/*

RUN apt-get update && \
    apt-get install -yq --no-install-recommends \
    xz-utils \
    bzip2 \
    gsl-bin \
    libopenblas-base \
    libopenblas-dev \
    libbz2-dev \
    libpcre2-dev \
    libharfbuzz-dev \
    libfribidi-dev \
    libfreetype6-dev \
    libpng-dev \
    libtiff5-dev \
    libjpeg-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN wget https://github.com/openssl/openssl/archive/OpenSSL_1_1_1h.tar.gz && \
    tar -zxvf OpenSSL_1_1_1h.tar.gz && \
    cd openssl-OpenSSL_1_1_1h/ && \
    ./config && \
    make && \
    make install && \
    cd .. && \
    rm -rf openssl-OpenSSL_1_1_1h

RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys 3FA7E0328081BFF6A14DA29AA6A19B38D3D831EF && \
    echo "deb https://download.mono-project.com/repo/debian stable-buster main" | sudo tee /etc/apt/sources.list.d/mono-official-stable.list && \
    apt update && apt-get -y install mono-devel && apt-get clean && rm -rf /var/lib/apt/lists/*

ENV SHELL /bin/bash
ENV NB_USER py4cy
ENV NB_UID 1000
ENV LC_ALL en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US.UTF-8

RUN useradd -m -s /bin/bash -N -u $NB_UID $NB_USER ; \
echo "root:cyto" | chpasswd ; \
echo "py4cy:cyto" | chpasswd ; \
adduser py4cy sudo

# Install Tini
RUN wget --quiet https://github.com/krallin/tini/releases/download/v0.10.0/tini && \
    echo "1361527f39190a7338a0b434bd8c88ff7233ce7b9a4876f3315c22fce7eca1b0 *tini" | sha256sum -c - && \
    mv tini /usr/local/bin/tini && \
    chmod +x /usr/local/bin/tini

RUN wget https://raw.githubusercontent.com/mpg-age-bioinformatics/draco_pipelines/master/software/newmod.sh \
&& sed -i 's/u\/jboucas\/modules/modules/g' newmod.sh && chmod 777 newmod.sh && mv newmod.sh /usr/bin

ENV MODULEPATH $MODF/bioinformatics:$MODF/general:$MODF/libs

# jre
RUN cd $SOUR && wget -O jre-8.0.271-linux-x64.tar.gz https://javadl.oracle.com/webapps/download/AutoDL?BundleId=243727_61ae65e088624f5aaa0b1d2d801acb16 && \
    tar -zxvf jre-8.0.271-linux-x64.tar.gz && \
    cd jre1.8.0_271 && \
    mkdir -p $SOFT/jre/8.0.271 && \
    cp -r * $SOFT/jre/8.0.271/ && \
    newmod.sh \
    -s jre \
    -p $MODF/general/ \
    -v 8.0.271 \
    -d 8.0.271 && \
    echo "setenv JAVA_HOME $SOFT/jre/8.0.271" >> $MODF/general/jre/8.0.271 && \
    rm -rf $SOUR/*

# jdk
RUN cd $SOUR && wget https://download.java.net/java/GA/jdk15.0.1/51f4f36ad4ef43e39d0dfdbaf6549e32/9/GPL/openjdk-15.0.1_linux-x64_bin.tar.gz && \
    tar -xvzf openjdk-15.0.1_linux-x64_bin.tar.gz && \
    mkdir -p $SOFT/jdk/15.0.1/bin && \
    cd jdk-15.0.1 && \
    cp -r * $SOFT/jdk/15.0.1/ && \
    newmod.sh \
    -s jdk \
    -p $MODF/general/ \
    -v 15.0.1 \
    -d 15.0.1 && \
    echo "setenv JAVA_HOME $SOFT/jdk/15.0.1" >> $MODF/general/jdk/15.0.1 && \
    rm -rf $SOUR/*

# perl/cpanm
RUN mkdir -p $SOFT/perl/5.28.1/bin && \
    cd $SOFT/perl/5.28.1/bin && \
    curl -L https://cpanmin.us/ -o cpanm && \
    chmod +x cpanm && \
    newmod.sh -s perl -p $MODF/general -v 5.28.1 -d 5.28.1 && \
    echo 'set home $::env(HOME)' >> $MODF/general/perl/5.28.1 && \
    echo 'set perluser $home/.software_container/.perl/5.28.1' >> $MODF/general/perl/5.28.1 && \
    echo 'exec /bin/mkdir -p $perluser' >> $MODF/general/perl/5.28.1 && \
    echo 'prepend-path PERL5LIB $perluser/lib/perl5' >> $MODF/general/perl/5.28.1 && \
    echo 'setenv PERLUSER $perluser' >> $MODF/general/perl/5.28.1

# Install R-4.0.3
RUN /bin/bash -c 'source /etc/profile.d/modules.sh && module load jdk && \
    cd $SOUR && wget http://ftp5.gwdg.de/pub/misc/cran/src/base/R-4/R-4.0.3.tar.gz && \
    tar -xzf R-4.0.3.tar.gz && \
    cd R-4.0.3 && \
    mkdir -p $SOFT/rlang/4.0.3/bin && \
    ./configure --prefix=$SOFT/rlang/4.0.3 \
    CFLAGS="-I$SOFT/jdk/15.0.1/include" \
    LDFLAGS="-L$SOFT/jdk/15.0.1/lib" \
    --with-cairo=yes --with-libpng=yes \
    --with-readline --with-tcltk --enable-R-profiling \
    --enable-R-shlib=yes --enable-memory-profiling --with-blas --with-lapack && \
    make && make install && \
    newmod.sh \
    -s rlang \
    -p $MODF/general/ \
    -v 4.0.3 \
    -d 4.0.3 && \
    echo "set home $::env(HOME)" >> $MODF/general/rlang/4.0.3 && \
    echo "exec /bin/mkdir -p \$home/.software_container/.R/4.0.3/R_LIBS_USER/" >> $MODF/general/rlang/4.0.3 && \
    echo "setenv R_LIBS_USER \$home/.software_container/.R/4.0.3/R_LIBS_USER" >> $MODF/general/rlang/4.0.3 && \
    echo "prepend-path LD_LIBRARY_PATH $SOFT/rlang/4.0.3/lib/R/lib" >> $MODF/general/rlang/4.0.3 && \
    echo "prepend-path CPATH $SOFT/rlang/4.0.3/lib/R/include" >> $MODF/general/rlang/4.0.3 && \
    echo "prepend-path C_INCLUDE_PATH $SOFT/rlang/4.0.3/lib/R/include" >> $MODF/general/rlang/4.0.3 && \
    echo "prepend-path CPLUS_INCLUDE_PATH $SOFT/rlang/4.0.3/lib/R/include" >> $MODF/general/rlang/4.0.3 && \
    echo "prepend-path OBJC_INCLUDE_PATH $SOFT/rlang/4.0.3/lib/R/include" >> $MODF/general/rlang/4.0.3 && \
    echo "module load jdk/15.0.1" >> $MODF/general/rlang/4.0.3 && \
    echo "setenv CFLAGS \"-I$SOFT/jdk/15.0.1/include\"" >> $MODF/general/rlang/4.0.3 && \
    echo "setenv LDFLAGS \"-L$SOFT/jdk/15.0.1/lib\"" >> $MODF/general/rlang/4.0.3 && \
    module load rlang && which R' && \
    rm -rf ${SOUR}/*

# python
RUN /bin/bash -c 'source /etc/profile.d/modules.sh && \
    cd $SOUR && \
    wget https://www.python.org/ftp/python/3.9.0/Python-3.9.0.tgz && \
    tar xzf Python-3.9.0.tgz && \
    cd Python-3.9.0 && \
    mkdir -p $SOFT/python/3.9.0/bin && \
    ./configure --prefix=$SOFT/python/3.9.0 --enable-loadable-sqlite-extensions --enable-shared -with-ensurepip=yes && \
    make && make install && \
    newmod.sh \
      -s python \
      -p $MODF/general/ \
      -v 3.9.0 && \
    echo "set home $::env(HOME)" >> $MODF/general/python/3.9.0 && \
    echo "set pythonuser \$home/.software_container/.python/3.9.0/bin" >> $MODF/general/python/3.9.0 && \
    echo "exec /bin/mkdir -p \$pythonuser" >> $MODF/general/python/3.9.0 && \
    echo "prepend-path PATH \$home/.software_container/.python/3.9.0/bin" >> $MODF/general/python/3.9.0 && \
    echo "set jupyter_runtime_dir \$home/.software_container/.python/3.9.0/jupyter/run" >> $MODF/general/python/3.9.0 && \
    echo "exec /bin/mkdir -p \$jupyter_runtime_dir" >> $MODF/general/python/3.9.0 && \
    echo "setenv JUPYTER_RUNTIME_DIR \$home/.software_container/.python/3.9.0/jupyter/run" >> $MODF/general/python/3.9.0 && \
    echo "set jupyter_data_dir \$home/.software_container/.python/3.9.0/jupyter/data" >> $MODF/general/python/3.9.0 && \
    echo "exec /bin/mkdir -p \$jupyter_data_dir" >> $MODF/general/python/3.9.0 && \
    echo "setenv JUPYTER_DATA_DIR \$home/.software_container/.python/3.9.0/jupyter/data" >> $MODF/general/python/3.9.0 && \
    echo "setenv PYTHONHOME $SOFT/python/3.9.0/" >> $MODF/general/python/3.9.0 && \
    echo "setenv PYTHONPATH $SOFT/python/3.9.0/lib/python3.9" >> $MODF/general/python/3.9.0 && \
    echo "setenv PYTHONUSERBASE \$home/.software_container/.python/3.9.0/" >> $MODF/general/python/3.9.0 && \
    echo "exec /bin/mkdir -p \$home/.software_container/.python/3.9.0/pythonpath/site-packages" >> $MODF/general/python/3.9.0 && \
    echo "module load rlang/4.0.3" >> $MODF/general/python/3.9.0 && \
    module load python && \
    pip3 install jupyter' && \
    rm -rf ${SOUR}/*

# R Jupyter-kernel
RUN echo "install.packages('askpass', repos='http://cran.us.r-project.org')" > $SOUR/askpass.install.R && \
    /bin/bash -c 'source /etc/profile.d/modules.sh && \
    module load python && \
    module load rlang && \
    cd $SOUR && \
    $SOFT/rlang/4.0.3/bin/Rscript $SOUR/askpass.install.R && \
    wget -O openssl_1.4.3.tar.gz https://github.com/jeroenooms/openssl/archive/v1.4.3.tar.gz && \
    $SOFT/rlang/4.0.3/bin/R CMD INSTALL -l $SOFT/rlang/4.0.3/lib/R/library openssl_1.4.3.tar.gz && \
    rm -rf $SOUR/*'

RUN echo "install.packages(c('repr', 'IRdisplay', 'evaluate', 'crayon', 'pbdZMQ', 'devtools', 'uuid', 'digest'), lib=c('$SOFT/rlang/4.0.3/lib/R/library')  ,repos=c('http://ftp5.gwdg.de/pub/misc/cran/'), dependencies=TRUE )" > $SOUR/jupyter.install.R && \
    /bin/bash -c 'source /etc/profile.d/modules.sh && \
    module load python && \
    module load rlang && \
    cd $SOUR && \
    git clone https://github.com/ropensci/git2r.git && \
    $SOFT/rlang/4.0.3/bin/R CMD INSTALL -l $SOFT/rlang/4.0.3/lib/R/library git2r && \
    $SOFT/rlang/4.0.3/bin/Rscript $SOUR/jupyter.install.R && \
    rm -rf $SOUR/*'

RUN echo "IRkernel::installspec(name = 'ir403', displayname = 'R 4.0.3')" > $SOUR/.install.jupyter.R.kernel.4.0.3 && \
    /bin/bash -c 'source /etc/profile.d/modules.sh && \
    module load python && \
    module load rlang && \
    cd $SOUR && \
    git clone https://github.com/IRkernel/IRkernel.git && \
    $SOFT/rlang/4.0.3/bin/R CMD INSTALL -l $SOFT/rlang/4.0.3/lib/R/library IRkernel && \
    $SOFT/rlang/4.0.3/bin/Rscript $SOUR/.install.jupyter.R.kernel.4.0.3 && \
    rm -rf $SOUR/*'

## Install rstudio server ##
RUN /bin/bash -c 'source /etc/profile.d/modules.sh && \
    module load python && \
    module load rlang && \
    cd ${SOUR} && \
    wget https://download2.rstudio.org/server/bionic/amd64/rstudio-server-1.3.1093-amd64.deb && \
    dpkg -i rstudio-server-1.3.1093-amd64.deb && \
    echo "rsession-which-r=$(which R)" >> /etc/rstudio/rserver.conf' && \  
    rm -rf ${SOUR}/*

# cytoscape
RUN /bin/bash -c 'source /etc/profile.d/modules.sh && \
  module load jre && \
  mkdir -p $SOFT/cytoscape/3.7.2 && \
  cd $SOFT/cytoscape/3.7.2 && wget  https://github.com/cytoscape/cytoscape/releases/download/3.7.2/Cytoscape_3_7_2_unix.sh && \
  bash Cytoscape_3_7_2_unix.sh -q && \
  newmod.sh \
  -s cytoscape \
  -p $MODF/bioinformatics/ \
  -v 3.7.2 \
  -d 3.7.2 && \
  echo "module load jre" >> $MODF/bioinformatics/cytoscape/3.7.2  && \
  echo "prepend-path PATH /usr/local/Cytoscape_v3.7.2" >> $MODF/bioinformatics/cytoscape/3.7.2' && \
  rm -rf ${SOUR}/*

USER $NB_USER

RUN mkdir /home/$NB_USER/py4cytoscape

# COPY * /home/$NB_USER/py2cytoscape

# RUN /bin/bash -c 'source /etc/profile.d/modules.sh && \
#     module load jupyterhub && \
#     cd py2cytoscape && \
#     python3 setup.py develop --user'

##########################
#### this part to end ####
##########################

# Jupyter port
EXPOSE 8888
# rstudio server port
EXPOSE 8787

COPY .bashrc /home/$NB_USER/.bashrc

RUN echo "options(bitmapType='cairo')" > /home/$NB_USER/.Rprofile
RUN mkdir -p /home/$NB_USER/.software_container/.jupyter
COPY jupyter_notebook_config.py /home/$NB_USER/.software_container/.jupyter/
USER root

# Folders in home folder that should be kept
ENV HOFOL ".bashrc .bash_logout .Rprofile .software_container"

RUN for i in $(ls /home/py4cy/) ; do echo ${i}; done

RUN mkdir -p /home/_py4cy \
&& for f in $HOFOL ; do \
  if [ ! -e /home/py4cy/${f} ] ;\
    then echo 'no ${f}..' ;\
  else cp -rv /home/py4cy/${f} /home/_py4cy/; \
  fi \ 
done

ENTRYPOINT /bin/bash -c '\
for f in $HOFOL ; do \
  if [[ ! -e /home/py4cy/${f} ]] ; \
    then cp -vr /home/_py4cy/${f} /home/py4cy/${f}; \
  fi \
done \
&& source /home/py4cy/.bashrc \
&& /bin/bash'
WORKDIR /home/py4cy
RUN chown -R py4cy: /home/py4cy

RUN mkdir -p /Dockerfiles/
COPY Dockerfile /Dockerfiles/

USER $NB_USER

