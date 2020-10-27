#!/bin/bash

# Tobias Jakobi
# tjakobi@age.mpg.de
# 29/07/2015

# This script creates the directory for the a software module
# together with all neccesary files. If the software already
# exists a new version is file is created and set as default.

USAGE="
USAGE:
  ./$(basename $0) -s SOFTWARE -p MPATH -v VERSION [-d DEFAULT]

OPTIONS:
  -s SOFTWARE : name of software
  -p MPATH    : module path (e.g. /software/Modules/tools or /software/Modules/biotools)
  -v VERSION  : current version of the software
  -d DEFAULT  : set the default version. If unset, the default will NOT be updated.
                If the installed software is the first version, it will be set as default.

NOTE:
  Install software before installing the module,
  \$PATH is set to /software/SOFTWARE/VERSION/bin and
  \$LD_LIDPRARPY_PATH to /software/SOFTWARE/VERSION/lib if folders exist
"
BINDIR=""
DEFAULT=""

while [[ $# > 0 ]]
do
  key="$1"
  case $key in
    -s|--software)
      SOFTWARE="$2"
      shift
      ;;
    -p|--path)
      MPATH="$2"
      shift
      ;;
    -v|--version)
      VERSION="$2"
      shift
      ;;
    -d|--default)
      DEFAULT="$2"
      shift
      ;;
    *)
      echo "unknown option '$key'"
      echo
      echo "$USAGE"
      echo
      exit 65
      ;;
  esac
  shift
done

# set default path to root dir
SOFTDIR="/u/jboucas/modules/software/$SOFTWARE/$VERSION"
BINDIR=$SOFTDIR

# if we find a bin dir...
if [ -d ${BINDIR}/bin ]
then
  BINDIR="${BINDIR}/bin"
fi

# set the default version, if argument is supplied
if [[ -n $DEFAULT ]]
then
  echo "warning: DEFAULT version will be changed"
elif [[ ! -f $MPATH/$SOFTWARE/.version ]]
then
  DEFAULT="$VERSION"
fi

# print out status
echo SOFTWARE  = "${SOFTWARE}"
echo VERSION   = "${VERSION}"
echo PATH      = "${MPATH}"
#echo BIN DIR   = "${BINDIR}"
#echo LIB DIR   = "${LIBDIR}"
#echo MANDIR    = "${MANDIR}"
#echo INFODIR   = "${INFODIR}"

# sanity check
[[ -z $SOFTWARE || -z $MPATH || -z $VERSION ]] && \
  echo "error: provide a SOFTWARE name and VERSION, and a module folder MPATH!" && \
  echo "$USAGE" && \
  exit 65

# create directories with software name and version number
mkdir -vp $MPATH/$SOFTWARE/

# remove old file if exists
rm  $MPATH/$SOFTWARE/$VERSION -f

# touch new file
touch $MPATH/$SOFTWARE/$VERSION

# set LD_LIBRARY_PATH if there is lib dir
if [ -d $SOFTDIR/lib ]
then
  LIBDIR="prepend-path LD_LIBRARY_PATH ${SOFTDIR}/lib"
fi

# set MANPATH/INFOPATH if there is share dir
if [ -d ${SOFTDIR}/share/man ]
then
  MANDIR="prepend-path MANPATH ${SOFTDIR}/share/man"
  INFODIR="prepend-path INFOPATH ${SOFTDIR}/share/man"
fi

# write new version file
cat <<EOT >> $MPATH/$SOFTWARE/$VERSION
#%Module3.2.10#####################################################################
proc ModulesHelp { } {
        global version
        puts stderr "\n\tVersion $VERSION of $SOFTWARE\n"
}

module-whatis   "Version $VERSION of $SOFTWARE"

# for Tcl script use only
set     version      "3.2.10"

conflict $SOFTWARE
prepend-path PATH $BINDIR
EOT

# set LD_LIBRARY_PATH if there is lib dir
if [ -d $SOFTDIR/lib ]
then
cat <<EOT >> $MPATH/$SOFTWARE/$VERSION
prepend-path LD_LIBRARY_PATH ${SOFTDIR}/lib
EOT
fi

# set LD_LIBRARY_PATH if there is lib dir
if [ -d $SOFTDIR/include ]
then
cat <<EOT >> $MPATH/$SOFTWARE/$VERSION
prepend-path CPATH ${SOFTDIR}/include
prepend-path C_INCLUDE_PATH ${SOFTDIR}/include
prepend-path CPLUS_INCLUDE_PATH ${SOFTDIR}/include
prepend-path OBJC_INCLUDE_PATH ${SOFTDIR}/include
EOT
fi

# set MANPATH/INFOPATH if there is share dir
if [ -d ${SOFTDIR}/share/man ]
then
cat <<EOT >> $MPATH/$SOFTWARE/$VERSION
prepend-path MANPATH ${SOFTDIR}/share/man
prepend-path INFODIR ${SOFTDIR}/share/man
EOT
fi

if [ -d ${SOFTDIR}/man ]
then
cat <<EOT >> $MPATH/$SOFTWARE/$VERSION
prepend-path MANPATH ${SOFTDIR}/man
prepend-path INFODIR ${SOFTDIR}/man
EOT
fi

# write .version file to set the default only if enforced
if [[ -n $DEFAULT ]]
then
  # remove old .version file
  rm $MPATH/$SOFTWARE/.version -f
  # touch new file
  touch $MPATH/$SOFTWARE/.version
  # update
  cat <<EOT >> $MPATH/$SOFTWARE/.version
#%Module1.0###########################################################
##
## version file for $SOFTWARE
##
set ModulesVersion      "$DEFAULT"
EOT
fi


echo "
Reminder:

edit /software/Modules/modules.rc for MPATH directories, if created a new one
edit $MPATH/$SOFTWARE/$VERSION for additional shell variables (e.g. PYTHONHOME, etc.)
"
