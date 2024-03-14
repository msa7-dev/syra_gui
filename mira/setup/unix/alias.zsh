alias up='sudo apt update'
alias upup='sudo apt update && sudo apt upgrade -y'

alias cdu='cd ..'
alias ..='cd ..'
alias ...='cd ../../../'
alias ....='cd ../../../../'
alias .....='cd ../../../../'


alias mv='mv -i'
alias cp='cp -i'
alias ln='ln -i'

alias ls='ls --color=auto'
alias ll='ls -la'
alias l.='ls -d .* --color=auto'

alias grep='grep --color=auto'
alias egrep='egrep --color=auto'
alias fgrep='fgrep --color=auto'

alias bc='bc -l'

alias now='date +"%T"'
alias nowdate='date +"%d-%m-%Y"'

alias ping='ping -c 5'
alias fastping='ping -c 25 -s.2'
alias ports='netstat -tulanp'

alias h="history -15"
alias hc="history -c"

alias cz='code ~/.oh-my-zsh/custom/alias.zsh'
alias czsh='code ~/.oh-my-zsh/custom/'
alias rz='omz reload'
