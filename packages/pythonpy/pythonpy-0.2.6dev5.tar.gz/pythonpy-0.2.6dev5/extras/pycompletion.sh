_py()
{
    COMPREPLY=($(echo ${COMP_WORDS[@]:1} | pycompleter))
}

complete -F _py -o nospace py
