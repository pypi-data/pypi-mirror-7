#! /usr/bin/env bash
# Copyright 2014 Dan Kilman
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


export PYSOURCE_PYTHON=${PYSOURCE_PYTHON="$(command \which python)"}

pysource()
{
    case "$1" in
        daemon|list-registered|run|run-piped|update-env)
            __pysource_main "$@"
            ;;
        source|source-registered|source-named|source-def|source-inline)
            __pysource_source "$@"
            ;;
        *)
            __pysource_source source "$@"
            ;;
    esac
}

def()
{
    __pysource_source source-def "$@"
}

__pysource_main()
{
    ${PYSOURCE_PYTHON} -m pysource.main "$@"
}

__pysource_source()
{
    local output=$(__pysource_main "$@")
    if [[ $output == \#GENERATED_BY_PYSOURCE* ]]
    then
        if [[ $output == \#GENERATED_BY_PYSOURCE_VERBOSE* ]]
        then
            echo "Sourcing:"
            printf "$output"
            echo
        fi
        eval "$output"
        return 0
    else
        printf "$output"
        return 1
    fi
}

__pysource_complete()
{
    local cur prev pysource_opts daemon_opts
    cur=${COMP_WORDS[COMP_CWORD]}
    prev=${COMP_WORDS[COMP_CWORD-1]}
    pysource_opts="daemon list-registered update-env run run-piped source source-def source-inline source-named source-registered"

    case "$prev" in
        daemon)
            daemon_opts="start stop restart status"
            COMPREPLY=( $( compgen -W "${daemon_opts}" -- $cur ) )
            return 0
            ;;
        *)
            ;;
    esac

    COMPREPLY=( $( compgen -W "${pysource_opts}" -- $cur ) )
}
complete -o default -F __pysource_complete pysource
