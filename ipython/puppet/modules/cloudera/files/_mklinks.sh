#!/bin/bash
    #
    # Make sure any new files are created with a secure access mask.  Do not use
    # chmod, since that would also change the rights of any existing files, and
    # we are only interested in setting the rights for new files.
    #
    umask 022

    #
    # RPM_INSTALL_PREFIX doesn't seem to be set by "alien" so the following
    # minor kludge allows some functionality on debian-like systems (such
    # a Ubuntu) which don't support packages.
    #
    if [ -z "${RPM_INSTALL_PREFIX}" ]; then
	RPM_INSTALL_PREFIX="/usr/java"
    fi

    #
    # Add the shell function and related variables used by the post-install.
    #
    MOST_DIGITS="[1-9]"
    ALL_DIGITS="[0-9]"
    COUNTING_NUMBER="${MOST_DIGITS}${ALL_DIGITS}*\|0"
    VALID_NON_NUMERIC="[-_.a-zA-Z]"
    VALID_CHARS="[-_.a-zA-Z0-9]"
    MAJOR_RULE="\(${MOST_DIGITS}${ALL_DIGITS}*\)"
    MINOR_RULE="\(${COUNTING_NUMBER}\)"
    MICRO_RULE="\(${COUNTING_NUMBER}\)"
    UPDATE_RULE="\(${MOST_DIGITS}${ALL_DIGITS}\|0${ALL_DIGITS}\)"
    NON_FCS_ID_RULE="\([a-zA-Z0-9]*\)"
    MIN_VERSION_ID_RULE="${MAJOR_RULE}\.${MINOR_RULE}\.${MICRO_RULE}"
    FCS_VERSION_ID_RULE="${MIN_VERSION_ID_RULE}\(_${UPDATE_RULE}\)\?"
    VERSION_ID_RULE="${FCS_VERSION_ID_RULE}\(-${NON_FCS_ID_RULE}\)\?"
    NAME_ID_RULE="${VALID_CHARS}*${VALID_NON_NUMERIC}"
    KNOWN_GOOD_NAME_LIST="java jdk jre j2sdk j2re"
    PRS_ERROR_BAD_PARAMS=2000
    UNKNOWN_NAME_WEIGHT=1000
    HAS_FCS_WEIGHT=0
    HAS_ODD_FCS_WEIGHT=1
    HAS_RC_WEIGHT=100
    HAS_ODD_RC_WEIGHT=101
    HAS_BETA_WEIGHT=300
    HAS_ODD_BETA_WEIGHT=301
    HAS_EA_WEIGHT=500
    HAS_ODD_EA_WEIGHT=501
    HAS_INTRNAL_WEIGHT=2000
    HAS_VERY_ODD_WEIGHT=9999
    LINK_ERROR_FILE_NOT_FOUND=3002

expand_version() {
    status=0
    if [ $# -eq 0 ]; then
        read release remainder
        status=$?
        if [ ${status} -ne 0 ]; then
            printf "Error(${status}: failed to read!\n"         >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        elif [ -z "${release}" ]; then
            printf "Error: usage - function requires input!\n"  >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        elif [ -n "${remainder}" ]; then
            printf "Error: too many words read:\n\n"            >> /dev/stderr
            printf "\t${release} ${remainder}\n"                >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        fi
    elif [ $# -eq 1 ]; then
        release=$1
    else
        printf "Error: usage - function takes 1 parameter:\n\n" >> /dev/stderr
        printf "\t expand_version $*\n"                         >> /dev/stderr
        status=${PRS_ERROR_BAD_PARAMS}
    fi
    if [ ${status} -eq 0 ]; then
        format="%d\t%d\t%d\t%d\n"
        echo ${release} | sed -e "s/_/\./g" | \
          awk -v format="${format}" 'BEGIN { FS = "." } { printf format, $1, $2, $3, $4 }'
    fi
    return ${status}
}
parse_release() {
    status=0
    if [ $# -eq 0 ]; then
        read string remainder
        status=$?
        if [ ${status} -ne 0 ]; then
            printf "Error(${status}: failed to read!\n"         >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        elif [ -z "${string}" ]; then
            printf "Error: usage - function requires input!\n"  >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        elif [ -n "${remainder}" ]; then
            printf "Error: too many words read:\n\n"            >> /dev/stderr
            printf "\t${string} ${remainder}\n"                 >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        fi
    elif [ $# -eq 1 ]; then
        string=$1
    else
        printf "Error: usage - function takes 1 parameter:\n\n" >> /dev/stderr
        printf "\t parse_release $*\n"                          >> /dev/stderr
        status=${PRS_ERROR_BAD_PARAMS}
    fi
    if [ ${status} -eq 0 ]; then
        version_id=`expr "${string}" : "${NAME_ID_RULE}\(${VERSION_ID_RULE}\)\$"`
        if [ -n "${version_id}" ]; then
            name_id=`expr "${string}" : "\(${NAME_ID_RULE}\)${VERSION_ID_RULE}\$"`
            fcs_part=`expr "${string}" : "${NAME_ID_RULE}\(${FCS_VERSION_ID_RULE}\).*\$"`
            non_fcs_part=`expr "${version_id}" : "[^-]*-\(${NON_FCS_ID_RULE}\)\$"`
            printf "${name_id}\t${fcs_part}\t${non_fcs_part}\n"
        fi
    fi
    return ${status}
}
get_name_weight() {
    status=0
    if [ "$1" = "-" ]; then
        read name good_names
        status=$?
        if [ ${status} -ne 0 ]; then
            printf "Error(${status}: failed to read!\n"                >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        else
            shift 1
            if [ $# -gt 0 ]; then
                good_names="$*"
            fi
            if [ -z "${name}" ]; then
                printf "Error: usage - function requires input!\n"     >> /dev/stderr
                status=${PRS_ERROR_BAD_PARAMS}
            fi
        fi
    elif [ $# -gt 1 ]; then
        name=$1
        shift 1
        good_names="$*"
    else
        printf "Error: usage - function takes 2+ parameters:\n\n"      >> /dev/stderr
        printf "\t get_name_weight $*\n"                               >> /dev/stderr
        status=${PRS_ERROR_BAD_PARAMS}
    fi
    if [ ${status} -eq 0 ]; then
        if [ -n "${good_names}" ]; then
            length=`expr length "${good_names}"`
            pos=`expr "${good_names}" : ".*\<${name}\>"`
            if [ ${pos} -gt 0 ]; then
                expr substr "${good_names}" 1 ${pos} | wc -w | tr -d "[:space:]"
            else
                echo ${UNKNOWN_NAME_WEIGHT}
            fi
        else
            echo ${UNKNOWN_NAME_WEIGHT}
        fi
    fi
    return ${status}
}
get_non_fcs_weight() {
    status=0
    if [ $# -eq 0 ]; then
        read non_fcs_part remainder
        status=$?
        if [ ${status} -ne 0 ]; then
            printf "Error(${status}: failed to read!\n"         >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        elif [ -n "${remainder}" ]; then
            printf "Error: too many words read:\n\n"            >> /dev/stderr
            printf "\t${non_fcs_part} ${remainder}\n"           >> /dev/stderr
            status=${PRS_ERROR_BAD_PARAMS}
        fi
    elif [ $# -eq 1 ]; then
        non_fcs_part=$1
    else
        printf "Error: usage - function takes 1 parameter:\n\n" >> /dev/stderr
        printf "\t get_non_fcs_weight $*\n"                     >> /dev/stderr
        status=${PRS_ERROR_BAD_PARAMS}
    fi
    if [ ${status} -eq 0 ]; then
        if [ -z "${non_fcs_part}" ]; then
            echo ${HAS_FCS_WEIGHT}
        else
            case "${non_fcs_part}" in
                fcs)
                    echo ${HAS_ODD_FCS_WEIGHT}
                    ;;
                rc)
                    echo ${HAS_RC_WEIGHT}
                    ;;
                rc[0-9] | rc[0-9][0-9])
                    count=`expr "${non_fcs_part}" : "rc\([0-9]*\)$"`
                    echo `expr ${HAS_RC_WEIGHT} - ${count}`
                    ;;
                rc*)
                    echo ${HAS_ODD_RC_WEIGHT}
                    ;;
                beta)
                    echo ${HAS_BETA_WEIGHT}
                    ;;
                beta[0-9] | beta[0-9][0-9])
                    count=`expr "${non_fcs_part}" : "beta\([0-9]*\)$"`
                    echo `expr ${HAS_BETA_WEIGHT} - ${count}`
                    ;;
                beta*)
                    echo ${HAS_ODD_BETA_WEIGHT}
                    ;;
                ea)
                    echo ${HAS_EA_WEIGHT}
                    ;;
                ea[0-9] | ea[0-9][0-9])
                    count=`expr "${non_fcs_part}" : "ea\([0-9]*\)$"`
                    echo `expr ${HAS_EA_WEIGHT} - ${count}`
                    ;;
                ea*)
                    echo ${HAS_ODD_EA_WEIGHT}
                    ;;
                internal)
                    echo ${HAS_INTRNAL_WEIGHT}
                    ;;
                internal[0-9] | internal[0-9][0-9] | internal[0-9][0-9][0-9])
                    count=`expr "${non_fcs_part}" : "internal\([0-9]*\)$"`
                    echo `expr ${HAS_INTRNAL_WEIGHT} - ${count}`
                    ;;
                b[0-9] | b[0-9][0-9] | b[0-9][0-9][0-9])
                    count=`expr "${non_fcs_part}" : "b\([0-9]*\)$"`
                    echo `expr ${HAS_INTRNAL_WEIGHT} - ${count}`
                    ;;
                *)
                    echo ${HAS_VERY_ODD_WEIGHT}
                    ;;
            esac
        fi
    fi
    return ${status}
}
get_path_weight() {
    good_list="$1"
    path=$2
    release=`basename ${path}`
    parts="`parse_release ${release}`"
    if [ $? -eq 0 ]; then
        name=`echo "${parts}" | cut -f1`
        version=`echo "${parts}" | cut -f2`
        non_fcs=`echo "${parts}" | cut -f3`
        if [ -n "${version}" ]; then
           v_weight=`echo ${version} | expand_version`
           n_weight=`echo ${name} | get_name_weight - "${good_list}"`
           o_weight=`echo ${non_fcs} | get_non_fcs_weight`
           printf "%4d  %4d  %4d  %4d  %4d  %4d  %s\n" \
                  ${v_weight} ${n_weight} ${o_weight} "${path}"
        fi
    fi
}
get_weighted_list() {
    good_list=
    verify=
    stdio=
    status=0
    check=true
    while [ -n "${check}" ]; do
        if [ $# -gt 0 ]; then
            case "$1" in
                -g)
                    good_list="$2"
                    shift 2
                    ;;
                --good-list=*)
                    length=`expr length "$1"`
                    remove=`expr \( length "--good-list=" \) + 1`
                    good_list="`expr substr \"$1\" ${remove} ${length}`"
                    shift 1
                    ;;
                -v | --verify)
                    verify=true
                    shift 1
                    ;;
                --)
                    shift 1
                    check=
                    ;;
                -)
                    shift 1
                    stdio=true
                    ;;
                -*)
                    printf "Error: usage - unknown parameter:\n\n" \
                                                                >> /dev/stderr
                    printf "\t%s : %s\n" "$1" "$*"              >> /dev/stderr
                    status=${PRS_ERROR_BAD_PARAMS}
                    check=
                    ;;
                *)
                    check=
                    ;;
            esac
        else
            check=
        fi
    done
    if [ $# -eq 0 ] || [ -n "${stdio}" ]; then
        read line
        while [ -n "${line}" ]; do
            if [ -z "${verify}" ] || [ -f ${line}/bin/java ]; then
                get_path_weight "${good_list}" ${line}
            fi
            read line
        done
    fi
    while [ $# -gt 0 ]; do
        if [ -z "${verify}" ] || [ -f $1/bin/java ]; then
            get_path_weight "${good_list}" $1
        fi
        shift 1
    done
    return ${status}
}
_compare_java_by_weight() {
    compare=0
    if [ $# -ne 0 ]; then
        if [ $# -eq 1 ]; then
            compare=1
        else
            left=$1
            right=$2
            shift 2
            good="$*"
            list=`get_weighted_list --good-list="${good}" \
                    ${left} ${right} | sort -u -k1n -k2n -k3n -k4n -k5rn -k6rn`
            if [ `echo "${list}" | wc -l | tr -d "[:space:]"` -ne 1 ]; then
                compare=-1
                latest=`echo "${list}" | tail -n 1 | cut -c 37-`
                if [ "${left}" = "${latest}" ]; then
                    compare=1
                fi
            fi
        fi
    fi
    echo ${compare}
}
compare_java_by_release() {
    _compare_java_by_weight $1 $2 ${KNOWN_GOOD_NAME_LIST}
}
find_latest_release() {
    if [ -d /usr/java ]; then
        latest_release=`find /usr/java/* -prune | \
            get_weighted_list -v --good-list="${KNOWN_GOOD_NAME_LIST}" | \
            sort -k1n -k2n -k3n -k4n -k5rn -k6rn | tail -n 1 | cut -c 37-`
    fi
    if [ -d "${RPM_INSTALL_PREFIX}" ] && \
       [ "/usr/java" != "${RPM_INSTALL_PREFIX}" ]
    then
        prefix_release=`find ${RPM_INSTALL_PREFIX}/* -prune | \
            get_weighted_list -v --good-list="${KNOWN_GOOD_NAME_LIST}" | \
            sort -k1n -k2n -k3n -k4n -k5rn -k6rn | tail -n 1 | cut -c 37-`
        if [ `compare_java_by_release ${latest_release} ${prefix_release}` -lt 0 ]; then
            latest_release=${prefix_release}
        fi
    fi
    echo ${latest_release}
}
dereference() {
    status=0
    if [ "$1" = "-f" ] || [ "$1" = "--follow" ]; then
        follow="--follow"
        shift 1
    fi
    if [ $# -ge 1 ]; then
        path="$*"
        if [ -e "${path}" ]; then
            parent="`cd \`dirname \"${path}\"\`; pwd`"
            child="`basename \"${path}\"`"
            if [ "${parent}" != "${child}" ]; then
                path="${parent}/${child}"
            fi
            if [ -h "${path}" ]; then
                path=`ls -l "${path}" | sed -e "s#^.*${path} -> ##"`
                if [ "`expr substr \"${path}\" 1 1`" != "/" ]; then
                    path="${parent}/${path}"
                fi
                if [ -n "${follow}" ]; then
                    path="`dereference ${follow} ${path}`"
                fi
            fi
        else
            status=${LINK_ERROR_FILE_NOT_FOUND}
        fi
    fi
    echo ${path}
    return ${status}
}
setup_latest_link() {
    latest=$1
    link=$2
    if [ -h "${link}" ]; then
        reference="`dereference --follow ${link}`"
        if [ $? -eq 0 ]; then
            update=`compare_java_by_release "${latest}" "${reference}"`
        else
            update=1
        fi
        if [ ${update} -gt 0 ]; then
            rm -f "${link}"
        fi
    fi
    if [ ! -e "${link}" ]; then
        ln -s "${latest}" "${link}"
    fi
}
setup_default_links() {
    if [ $# -ge 2 ]; then
        latest_link="$1"
        default_link="$2"
        if [ ! -e "${default_link}" ]; then
            ln -s "${latest_link}" "${default_link}"
        fi
    fi
}

    #
    # Find out what version of Java is the latest.  Don't do any system
    # integration unless this is the latest version.  Otherwise, we make it
    # difficult for future installers.
    #
    LATEST_JAVA_PATH="`find_latest_release`"

    #
    # Make sure the /usr/java/latest link points to LATEST_JAVA_PATH, and
    # update it if it doesn't.
    #
    setup_latest_link "${LATEST_JAVA_PATH}" "/usr/java/latest"

    #
    # Make sure the /usr/java/default and java javaws jcontrol javac jar javadoc exist.
    # If anything is missing, create it.
    #
    setup_default_links "/usr/java/latest" "/usr/java/default"

