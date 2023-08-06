_py()
{
    COMPREPLY=($(pycompleter "${COMP_WORDS[@]}" 2>/dev/null ))
    if [[ ${COMPREPLY[0]} == '_pycd' ]]; then
        COMPREPLY=()
        _cd 2>/dev/null
    fi
}

complete -F _py -o nospace py
