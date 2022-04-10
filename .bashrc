# .bashrc

# User specific aliases and functions

alias rm='rm -i'
alias cp='cp -i'
alias mv='mv -i'
alias svansible='su - svadmin /data01/home/svadmin/svansible'
alias svansible-console='su - svadmin /data01/home/svadmin/svansible-console'
alias svansible-playbook='su - svadmin /data01/home/svadmin/svansible-playbook'
# Source global definitions
if [ -f /etc/bashrc ]; then
	. /etc/bashrc
fi
