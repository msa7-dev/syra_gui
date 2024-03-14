#!/bin/zsh

# Define the variables
gitServer="https://gitlab.com"
userToken="glpat-s65JavBxs6TYvc582VAm"
sshName="sykno@sykno-pi"

# Generate SSH key pair if needed
if [ ! -f ~/.ssh/id_rsa.pub ]; then
    ssh-keygen -t rsa -N "" -f ~/.ssh/id_rsa
fi

# Retrieve the SSH key
sshKey=$(cat ~/.ssh/id_rsa.pub)

# Add the SSH key to GitLab
curl -X POST --data-urlencode "private_token=${userToken}" --data-urlencode "title=${sshName}" --data-urlencode "key=${sshKey}" "${gitServer}/api/v4/user/keys"

curl -v --header "PRIVATE-TOKEN: $userToken" "$gitServer/api/v4/user/keys" | jq


