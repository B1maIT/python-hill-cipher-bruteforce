#generator odwracalnej macierzy 2x2 nad Z26
def gen_key():
    while True:
        K = Matrix(ZZ, 2, 2, [randint(0, 25) for _ in range(4)])
        if gcd(K.det(), 26) == 1:
            return K

#zamiana tekstu na bloki (po n liter)
def txt2blk(txt, n):
    txt = txt.upper().replace(" ", "")
    if len(txt) % n != 0:
        txt += "X" * (n - len(txt) % n)
    return [vector(ZZ, [ord(c) - ord('A') for c in txt[i:i+n]]) for i in range(0, len(txt), n)]

#zamiana blokow na tekst
def blk2txt(blks):
    return ''.join(chr(int(c) + ord('A')) for b in blks for c in b)

#szyfrowanie
def enc(txt, K):
    Z26 = IntegerModRing(26)
    KM = Matrix(Z26, K)
    n = K.nrows()
    blks = txt2blk(txt, n)
    enc_blks = [(KM * vector(Z26, b)) for b in blks]
    enc_int = [vector(ZZ, [int(c) for c in v]) for v in enc_blks]
    return blk2txt(enc_int)

#deszyfrowanie
def dec(ctxt, K):
    Z26 = IntegerModRing(26)
    KM = Matrix(Z26, K)
    Kinv = KM.inverse()
    n = K.nrows()
    blks = txt2blk(ctxt, n)
    dec_blks = [(Kinv * vector(Z26, b)) for b in blks]
    dec_int = [vector(ZZ, [int(c) for c in v]) for v in dec_blks]
    return blk2txt(dec_int).rstrip("X")

#brute-force przy znanym rozmiarze bloku (2x2)
def brute_known_block(ptxt, ctxt):
    P = txt2blk(ptxt, 2)
    C = txt2blk(ctxt, 2)
    Z26 = IntegerModRing(26)

    for a in range(26):
        for b in range(26):
            for c in range(26):
                for d in range(26):
                    K = Matrix(ZZ, 2, 2, [a, b, c, d])
                    if gcd(K.det(), 26) != 1:
                        continue
                    KM = Matrix(Z26, K)
                    if all((KM * vector(Z26, p)) == vector(Z26, c) for p, c in zip(P, C)):
                        return K
    return None

#brute-force bez znajomosci dlugosci bloku (dla n = 2..max_n)
def brute_unknown_block(ptxt, ctxt, max_n=4):
    Z26 = IntegerModRing(26)
    ptxt = ptxt.upper().replace(" ", "")
    ctxt = ctxt.upper().replace(" ", "")

    for n in range(2, max_n + 1):
        print(f"\n[+] Proba dlugosci bloku: {n}x{n}")
        if len(ptxt) % n != 0:
            ptxt += "X" * (n - len(ptxt) % n)
        if len(ctxt) % n != 0:
            ctxt += "X" * (n - len(ctxt) % n)
        try:
            P = txt2blk(ptxt, n)
            C = txt2blk(ctxt, n)
        except:
            continue
        total = 26 ** (n * n)
        print(f"  - Testuje do {total} kluczy...")

        for vals in cartesian_product_iterator([range(26)] * (n * n)):
            flat = list(vals)
            K = Matrix(ZZ, n, n, flat)
            if gcd(K.det(), 26) != 1:
                continue
            try:
                KM = Matrix(Z26, K)
                if all((KM * vector(Z26, p)) == vector(Z26, c) for p, c in zip(P, C)):
                    print("Znaleziono klucz!")
                    return K, n
            except ZeroDivisionError:
                continue
    print("Klucz nie został znaleziony.")
    return None, None

#uzycie
K = gen_key()
msg = "WATSTEFKO"
ctxt = enc(msg, K)

print("Wiadomosc:", msg)
print("Szyfrogram:", ctxt)
print("Klucz:\n", K)

#brute-force przy znanym rozmiarze
K_rec = brute_known_block(msg, ctxt)
print("\n[Brute znany blok] Odzyskany klucz:\n", K_rec)
print("Poprawny?", K == K_rec)

#brute-force przy nieznanym rozmiarze
K_rec2, n = brute_unknown_block(msg, ctxt)
print("\n[Brute nieznany blok] Odzyskany klucz:\n", K_rec2)
print("Rozmiar bloku:", n)
print("Poprawny?", K == K_rec2)