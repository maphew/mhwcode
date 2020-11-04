#!/bin/sh
# Rewrite all commits in this repo attributed for my work address to my personal one.
# WARNING! is destructive for collaborators. See:
# https://help.github.com/en/articles/changing-author-info 

git filter-branch --env-filter '

OLD_EMAIL="maphew@gmail.com"
CORRECT_NAME="Matt Wilkie"
CORRECT_EMAIL="matt.wilkie@gov.yk.ca"

if [ "$GIT_COMMITTER_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_COMMITTER_NAME="$CORRECT_NAME"
    export GIT_COMMITTER_EMAIL="$CORRECT_EMAIL"
fi
if [ "$GIT_AUTHOR_EMAIL" = "$OLD_EMAIL" ]
then
    export GIT_AUTHOR_NAME="$CORRECT_NAME"
    export GIT_AUTHOR_EMAIL="$CORRECT_EMAIL"
fi
' --tag-name-filter cat -- --branches --tags