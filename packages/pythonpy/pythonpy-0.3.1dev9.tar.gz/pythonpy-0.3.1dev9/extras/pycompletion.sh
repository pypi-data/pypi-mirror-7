_py()
{
    COMPREPLY=($(pycompleter "${COMP_WORDS[@]:1}" 2>/dev/null ))
}

complete -F _py -o nospace py
