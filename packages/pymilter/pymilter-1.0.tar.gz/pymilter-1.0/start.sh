#!/bin/sh
appname="$1"
script="${2:-${appname}}"
datadir="/var/lib/milter"
logdir="/var/log/milter"
piddir="/var/run/milter"
libdir="/usr/lib/pymilter"
python="python2.4"
exec >>${logdir}/${appname}.log 2>&1
if test -s ${datadir}/${script}.py; then
  cd ${datadir} # use version in data dir if it exists for debugging
elif test -s ${logdir}/${script}.py; then
  cd ${logdir} # use version in log dir if it exists for debugging
else
  cd ${libdir}
fi

${python} ${script}.py &
echo $! >${piddir}/${appname}.pid
