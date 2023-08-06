_py()
{
    #COMPREPLY=($(echo "${COMP_WORDS[@]:1}" | pycompleter))
    COMPREPLY=($(pycompleter "${COMP_WORDS[@]:1}" ))
}

complete -F _py -o nospace py
