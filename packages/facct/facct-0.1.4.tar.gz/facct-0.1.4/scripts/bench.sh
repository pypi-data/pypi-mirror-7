#!/bin/bash
script_root=$(dirname $0)
app_root=$(dirname $script_root)
export PYTHONPATH=$PYTHONPATH:$app_root
bench_py="$(ls $app_root/*/bench.py)"
init_py="$(ls $app_root/*/init_year.py)"

# Create configuration if needed:
if [ ! -f $HOME/.facct.rc ]; then
    touch $HOME/.facct.rc
fi
for orga in toto tutu corp_ref; do
        tmp=$(grep -E "\[$orga\]" $HOME/.facct.rc)
        if [ -z "$tmp" ]; then
            echo "$orga:"
            echo "" | python "$init_py" -o "$orga" -y 2013 --create
            if [ "$orga" = "corp_ref" ]; then
                rm -rf $HOME/facct/$orga
            fi
            rm -rf $HOME/facct/$orga/accounts/2013
        fi
done

# Test for Python2 and python3:
for cmd in 'python' 'python3'; do 
    echo "$cmd:"
    $cmd "$bench_py" -o corp_ref
    tmp=$(grep -E "\[figerson\]" $HOME/.facct.rc)
    if [ ! -z "$tmp" ]; then
        $cmd "$bench_py" -o figerson -b
    fi
    $cmd "$bench_py" -o toto
    $cmd "$bench_py" -o tutu
done

$script_root/translation.sh "update"
to_translate=$(grep 'msgstr  ""' $app_root/po/fr.po)
if [ -z "$to_translate" ]; then
    echo "[OK]: Translation OK" >&2
    exit 0
else
    echo "[KO]: Please finish translation" >&2
    exit 2
fi
