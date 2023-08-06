_py()
{
    local cur=${COMP_WORDS[COMP_CWORD]}
    COMPREPLY=($(echo ${COMP_WORDS[@]:1} | pycompleter))
}

complete -F _py -o nospace py
