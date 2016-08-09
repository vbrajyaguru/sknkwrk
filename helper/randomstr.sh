# random string generator: outputs printable strings from /dev/urandom
# if string length not provided, default length of 20 is chosen (i.e., 20 bytes long)
# sha-1 produces a 20-byte message digest, md5 produces a 16-byte message digest

len=${1-20}
strings /dev/urandom | grep -o '[[:alnum:]]' | head -n $len | tr -d '\n'; echo
