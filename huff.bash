exec $'git clone https://github.com/AztecProtocol/huff.git'
exec $'patch -s -p0 < huff.patch'
exec $'cd huff'
exec $'npm install'
exec $'cd ..'
