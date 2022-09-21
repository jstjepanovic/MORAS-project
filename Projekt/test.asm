@10
D = A
@1
M = D
D = A
@2
M = D

$LD(@i, 2) // postavljamo varijablu i
$LD(@R0, 0) // postavljamo R0 na 0
$LD(@d, 1) // postavljamo varijablu d
$LOOP(@d) // dok varijabla d nije 0 radi
{
$ADD(@R0, @R0, @i) // uvecaj R0 za i
$SUB(@d, @R1, @i) // provjera
$ADD(@i, @i, 1) // uvecaj i za 1
}


@0
D=A
@d
M=D

$IF(@d)
{
    $LD(@d, @0)
    $LOOP(@d)
    {
    $ADD(@R10, @R10, 2)
    $SUB(@d, @d, 1)
    }
}


(END)
@END
0; JMP
