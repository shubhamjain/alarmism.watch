#!/bin/bash

CONTENTS="$(curl -sL "https://docs.google.com/spreadsheets/d/15hRWjG6zTUY1kwTBMMLnBPqtIZ64eEY-sxoCYRQQObg/gviz/tq?tqx=out:json&sheet=Sheet1")"

CLEAN_JSON="$(echo "$CONTENTS" | sed 's/\/\*.*\*\///g' | sed -E 's|google.visualization.Query.setResponse\((.*)\);|\1|')"
FORMATTED_JSON="$(echo "$CLEAN_JSON" | jq '.table.rows[] | {
    headline: .c[0].v,
    link: .c[1].v,
    status: .c[2].v,
    status_comment: .c[3].v,
    category: .c[4].v,
    about_year: .c[5].v,
    year: .c[6].v
}' | jq -s '{items: .}')"

jinja2 root.html <(echo "$FORMATTED_JSON") --format=json > index.html

git add .
git commit -m "New commit"
git push origin