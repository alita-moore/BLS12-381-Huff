eval $'git clone https://github.com/AztecProtocol/huff.git'
eval $'patch -s -p0 < custom-opcodes/huff.patch'
eval $'cd huff'
eval $'npm install'
eval $'cd ..'
eval $'node ./custom-opcodes/test.js'

# install python 3.8-dev
eval $'brew install openssl readline sqlite3 xz zlib' # for mac
eval $'brew update'
eval $'brew install pyenv'
eval $'pyenv install 3.8-dev'

# add this to .zshrc / .bashrc
# export PATH="$HOME/.pyenv/bin:$PATH"
# eval "$(pyenv init -)"

eval $'pyenv init -'
eval $'pip install py-evm'
eval $'pip install pycryptodome pysha3'
