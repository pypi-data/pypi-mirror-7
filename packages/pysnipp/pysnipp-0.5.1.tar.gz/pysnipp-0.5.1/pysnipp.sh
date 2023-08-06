_available_categories()
{
    redis-cli --raw keys "*" | cut -d":" -f1
}

_available_snippets()
{
    redis-cli --raw keys "${COMP_WORDS[COMP_CWORD-1]}:*" | cut -d":" -f2
}

_pysnipp()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev=${COMP_WORDS[COMP_CWORD-1]}


    if [ $COMP_CWORD -eq 1 ]
    then
        COMPREPLY=( $( compgen -W 'delete about show list add rename edit' -- $cur) )
    elif [ $COMP_CWORD -eq 3 ]
    then
        COMPREPLY=( $( compgen -W '$(_available_snippets)' -- $cur) )
    else 
        case ${COMP_WORDS[1]} in
            delete|show|rename|add|edit)
            _pysnipp_action
        ;;
            about)
            _pysnipp_about
        ;;
        esac
    fi
}

_pysnipp_action()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -eq 2 ]; then
        COMPREPLY=( $( compgen -W '$(_available_categories)' -- $cur) )
    fi
 
}

_pysnipp_about()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -W ' ' -- $cur) )
    fi
}

_pysnipp_list()
{
    local cur
    cur="${COMP_WORDS[COMP_CWORD]}"

    if [ $COMP_CWORD -ge 2 ]; then
        COMPREPLY=( $( compgen -W '-C ' -- $cur) )
    fi
}
complete -F _pysnipp pysnipp
