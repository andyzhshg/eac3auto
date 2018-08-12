#!/bin/sh

BASE_ROOT=$(cd "$(dirname "$0")";pwd)

logPrint() {
    DATE_TIME=`date "+%Y-%m-%d %H:%M:%S"`
    echo "[${DATE_TIME}] $1"
}

proccessFile () {
    FILE_PATH=$1
    EXT="${FILE_PATH##*.}"
    EXT=$(echo ${EXT} | tr '[A-Z]' '[a-z]')
    if [ "${EXT}" = "mkv" -o "${EXT}" = "mp4" ]
    then
        logPrint "begin process file: ${FILE_PATH}"
        python ${BASE_ROOT}/convert.py ${FILE_PATH}
        case "$?" in
            0)
                logPrint "${FILE_PATH} convert ok."
                ;;
            1)
                logPrint "${FILE_PATH} no need to convert."
                ;;
            *)
                logPrint "${FILE_PATH} convert fail."    
                ;;
        esac
    fi
}

processDirectory () {
    for CHILD_PATH in `ls $1`
    do
        if [ -d "$1/${CHILD_PATH}" ]
        then
            processDirectory "$1/${CHILD_PATH}"
        else
            proccessFile "$1/${CHILD_PATH}"
        fi
    done
}

watchDirectory () {
    echo "watch $1"
    inotifywait -mrq --format='%w%f' -e moved_to,create $1 | while read INFO_PATH; do
        if test -f ${INFO_PATH}
        then
            proccessFile ${INFO_PATH}
        else
            echo "not file: ${INFO_PATH}"
        fi
    done
}

case "$1" in
    file)
        proccessFile $2
        ;;
    directory)
        processDirectory $2
        ;;
    watch)
        watchDirectory $2
        ;;
    run_watch)
        processDirectory $2
        watchDirectory $2
        ;;
    *)
        watchDirectory /videos
        ;;
    esac
