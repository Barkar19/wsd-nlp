Poprawne działanie WoSeDona wymaga zainstalowania modułu PLWNGraphBuilder oraz wosedon.

I) Instalacja PLWNGraphBuilder'a, będąc w aktualnym katalogu, wydać polecenie:

    cd PLWNGraphBuilder; sudo python setup.py install; cd ..

II) Instalacja wosedona, będąc w aktualnym katalogu, wydać polecenie:

  cd wosedon; sudo python setup.py install; cd ..


II) Jeśli instalacja przebiegła pomyslne, to po wpisaniu w konsoli polecenia: wosedon
    Powinien ukazać się komunikat zbliżony do tego:

usage: wosedon [-h] [-c CONFIG] [-md MODEL_DIR] [-it] [-a ALPHA] [-V] -f CCL
               [-r RELCCL] [-o OUT_FILE] [-b] [-vd VISUALISATION_DIR]
wosedon: error: argument -f/--cclfile is required

