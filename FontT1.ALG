inicio
    varinicio
        A lit;
        B int;
        D int;
        C real;
    varfim;

    escreva "Digite B";
    leia B;

    escreva "Digite A:";
    leia A;

    se (B > 2) entao
        se (B <= 4) entao
            escreva "B está entre 2 e 4";
        fimse
    fimse

    B <- B + 1;
    B <- B + 2;
    B <- B + 3;
    D <- B;
    C <- 5.0;

    faca-ate (B > 5)
        escreva B;
        B <- B + 1;
    fimfaca

    escreva "\nB=\n";
    escreva D;
    escreva "\n";
    escreva C;
    escreva "\n";
    escreva A;
fim
