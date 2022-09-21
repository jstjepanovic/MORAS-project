@5
M=A
$LD(@a, @5)
$LD(@b, @5)

$LOOP(@a)
{
	$ADD(@R10, @R10, 1)
	$LOOP(@b)
	{
		$ADD(@R11, @R11, 1)
		$SUB(@b, @b, 1)
	}
	$SUB(@a, @a, 1)
	$LD(@b, 5)
}

(END)
@END
0; JMP
