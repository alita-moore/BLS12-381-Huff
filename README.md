# BLS12-381-Huff

BLS12-381 implementation in huff

# 1. Install Huff compiler

These instructions are thanks to @poemm's Huff patch and can be found [here](https://gist.github.com/poemm/bf50b9c8f18c33c0883461ede3a4ae8a)

## Quick-Start

```bash
# first clone this repo, then enter the main dir of that cloned repo
sh huff.sh
```

[huff.sh](/huff.sh) is an automated version of the following:

```bash
# Make sure you're in this projects main directory
git clone https://github.com/AztecProtocol/huff.git
# patch the custom op-codes into huff
patch -s -p0 < custom-opcodes/huff.patch
# initialize huff
cd huff
npm install
cd ..
# run test.js to verify the opcodes were installed properly
node ./custom-opcodes/test.js
```
