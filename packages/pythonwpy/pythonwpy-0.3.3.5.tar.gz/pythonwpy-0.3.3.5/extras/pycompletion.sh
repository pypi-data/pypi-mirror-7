_py()
{
    COMPREPLY=($(pycompleter "${COMP_WORDS[@]}" 2>/dev/null ))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

_py3()
{
    COMPREPLY=($(pycompleter3 "${COMP_WORDS[@]}" 2>/dev/null ))
    if [[ ${COMPREPLY[0]} == '_longopt' ]]; then
        COMPREPLY=()
        _longopt 2>/dev/null
    fi
}

complete -F _py -o nospace py
complete -F _py3 -o nospace py3
