# BLS12-381-Huff

BLS12-381 implementation in huff

# 1. Install Huff compiler

These instructions are thanks to @poemm's Huff patch and can be found [here](https://gist.github.com/poemm/bf50b9c8f18c33c0883461ede3a4ae8a)

## Requirements

- Python >= 3.8 (for use with the debugger)
    - [py-evm](https://github.com/ethereum/py-evm)

## Quick-Start

```bash
# first clone this repo, then enter the main dir of that cloned repo
sh huff.sh
pip install py-evm
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
# 2. Install dependencies
```bash
npm install
sudo pacman -S geth
```

# 3. Create a private evm
```bash
mkdir privatechain
cd privatechain
puppeth
```
follow [this](https://hackernoon.com/hands-on-creating-your-own-local-private-geth-node-beginner-friendly-3d45902cc612) to setup the system

# Pure EVM BLS12-381 Pairing Algorithm

## Introduction

To learn more about elliptic curves, I recommend you read / skim the following in order:
- [primer](https://blog.cloudflare.com/a-relatively-easy-to-understand-primer-on-elliptic-curve-cryptography/) 
- [bls12-381 for the rest of us](https://hackmd.io/@benjaminion/bls12-381)
- [exploring elliptic curves](https://medium.com/@VitalikButerin/exploring-elliptic-curve-pairings-c73c1864e627)
- [pairing for beginners](http://www.craigcostello.com.au/pairings/PairingsForBeginners.pdf)

This project builds off of Axic's work on precompiles capable of doing the necessary math in good time. The goal of this project is to implement an optimal BLS12-381 (using the optimized algorithms given by IETF) in a new EVM programming language called Huff. Huff allows the necessary close to metal precision required to implement an optimized BLS algorithm.

The existence of pre-compiles is not popular in the Ethereum community due to their oblique nature. A pure EVM based executable is preferred. What that means simply is that this method will be built using purely the building blocks / precompiles of the Ethereum network -- analogous to assembly.

As mentioned by Axic in his initial exploration and benchmarking, BLS12 implementation in evm is estimated to run at about 1/3 of its native counterpart (programmed in rust). The difference between the performance of a BLS12 precompile and pure EVM implementation is very large, and that gap would practically limit the capacity for for fast crypto in Ethereum.

Using the high-precision language of Huff, I will avoid high-gas opcodes: ```SLOAD``` or ```SSTORE``` by micro-managing local memory resources. 

## BLS12-381

The Barreto-Lynn-Scott (BLS) curve has a pairing friendly variant known as BLS12-381. Notably, this method is ~117 bit secure. The BLS curve offers a wide variety of benefits to the functionality and versatility of the ethereum network; for example, the BLS curve allows for someone to verify the integrity of a block's transactions by simply adding them up. The pairing step of BLS12-381 integration is the most computationally expensive part of the process.

What is pairing? well to put it simply, let's say you're given two points on two pairing friendly curves, let's call them G1 and G2; when we imput G1 and G2 into a map e s.t. e(G1, G2) => G_T or when you input G1 and G2 into this mapping function it outputs a point on G_T; notably G1 and G2 are formalized in such a way that e(G1, G2) = 1 if and only if they are G1 and G2. Meaning, that there's only one solution to the corresponding solution, and that means it requires a lot of work to fake a signature so is encryption secure. If you're interested you can read more about to-spec pairing methods [here](https://tools.ietf.org/html/draft-irtf-cfrg-pairing-friendly-curves-02). 

The BLS curve does this by creating two elliptic curve E and E' using a well chosen integer t.

E: y^2 = x^3 + b (twisted, and proportional to a single prime with cofactor h)
E': y^2 = x^3 + b' with (D-type: b' = b / m, M-type: b' = b * m)

parameterized p and r are given by the following equations

p = (t-1)^2 * (t^4 - t^2 - 1) / 3 + t
r = t^4 - t^2 + 1

for a well chosen integer t

G_1 is a subgroup of E(F_p) of order r, G_2 as an order r subgroup of E'(F_p^2). G_T is an order r subgroup of a multiplicative group (F_p^12)^*

The IETF spec G1 and G2 curves are defined in [Appendix A](#Appendix-A):

---

Algorithmically, I will use optimal ate pairing -- Miller's loop. 

## Miller's loop

What is Miller's loop? Ignoring the details, Miller's loop makes pairing practicle [pairing for beginners](http://www.craigcostello.com.au/pairings/PairingsForBeginners.pdf). Essentially, it works under the premise that there is a direct relationship between successive orders. Or more simply,
$x_{2} = x_{1}*y$
where y is some complex function that is the product of previous factors. This therefore allows us to increment our $x_{1}$ to a higher order $x_{n}$; the order is base 2 (binary), so in this case to get to order 281, we need to do 281 loops to bring an order 1 to 281. The resulting output can then be used to verify the validity of a signature.  
Therefore, instead of having to do $2^{281}$ operations, we only have to do 281. Without the Miller loop, pairing would be impossible. This is all made possible by the previously mentioned factor.

The equation used here is

![image](https://i.imgur.com/4kicZLU.png)

so we need to have the line between two points $l$, the vertical line $v$, and then be able to multiplication and division.

## Line Arithmetic Using Mixed Addition

Side-channel attacks are common concerns for most optimization methods used in the miller loop. This problem arises because the algorithms to perform arithmetic are not performed in constant time, that allows an adversary to spy on and steal the secret information. To combat this, the "complete" mixed-addition method will be used [[source](https://eprint.iacr.org/2015/1060), [implementation](https://github.com/mratsim/constantine/blob/7163d870d2a1793a8ccb518eb512b07528d66fde/constantine/elliptic/ec_weierstrass_projective.nim#L130-L162), [benchmark](https://github.com/mratsim/constantine/pull/90#issue-493406885)]  

---

This has a loop length of log2(t-1) and $e(Q,P) = f_{u,Q}(P)$ for BLS-12, the simplest of the pairing friendly curves. note that $f_{u,Q}(P)$ symbolizes the output of Miller's algorithm [Khandaker et-al, 2017](https://eprint.iacr.org/2017/1174.pdf).

"the projective coordinates are more efficient while for quadratic and quartic twists, jacobian coordinates are more efficient [...] We use the complete addition law from [Renes2015](https://eprint.iacr.org/2015/1060) for projective coordinates" [source](https://github.com/mratsim/constantine/tree/master/constantine/elliptic), [article1](https://eprint.iacr.org/2009/615), [article2](https://www.math.u-bordeaux.fr/~damienrobert/csi2018/pairings.pdf)

complete, mixed point addition for arbitrary prime order short weierstrass curves

[miller loop in projective](https://github.com/scipr-lab/zexe/issues/20)

![mixed point addition](https://imgur.com/bTr5MQg.png)

Mixed addition is the use of multiplications and additions to minimize the number of expensive operations such as inversion or squaring. from [Abarua](https://eprint.iacr.org/2019/010.pdf): 

![mixed addition](https://imgur.com/yXkJUBw.png)
![mixed addition algorithm](https://imgur.com/huPqMZh.png)
(but this is insecure)

Clean implementation of both of these [here](https://github.com/mratsim/constantine/blob/0effd66dbd3201f4d40cfbbe72c65fd950c4429b/constantine/elliptic/ec_shortweierstrass_projective.nim#L240-L285)

side-channel resistance:
- montgomery ladder algorithm (SSCA); randomized projective coordinate (DSCA) [Liu, 2017](https://ieeexplore.ieee.org/abstract/document/7803934)
- 

[investigation of security risks](https://eprint.iacr.org/2019/010)
"it is often assumed that I ~ 100M and S = 0.8M", where I is 100x more expensive than multiplication, and squaring is 80% as taxing

[efficient final exponentiation algorithm](https://eprint.iacr.org/2020/875.pdf)

### Elliptic Curve Discrete Logarithm Problem



Notable miller loop method optimizations exist: Pre-computation and

### Security Considerations

- timing attacks (Renes2015)
    - inherent "branching", complex logic with processing variability


# Implementations

Assembly offers major performance improvements ([Scott, 2020](https://eprint.iacr.org/2020/514.pdf))


# Appendix A | _Base Constants_
These constants are taken directly from 

t = -2^63 - 2^62 - 2^60 - 2^57 - 2^48 - 2^16 = -15132376222941642752

p: a character prime  
r: and order  
BP = (x, y) : a base point  
h: a cofactor  
b: a coefficient of E  

|   |                                                 G1                                                 |
|---|:--------------------------------------------------------------------------------------------------:|
| p | 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab |
| r | 0x73eda753299d7d483339d80809a1d80553bda402fffe5bfeffffffff00000001                                 |
| x | 0x17f1d3a73197d7942695638c4fa9ac0fc3688c4f9774b905a14e3a3f171bac586c55e83ff97a1aeffb3af00adb22c6bb |
| y | 0x08b3f481e3aaa0f1a09e30ed741d8ae4fcf5e095d5d00af600db18cb2c04b3edd03cc744a2888ae40caa232946c5e7e1 |
| h | 0x396c8c005555e1568c00aaab0000aaab                                                                 |
| b | 4                                                                                                  |

r' : an order  
BP' = (x', y') : a base point  
x' = x0' + x1' * u(x0', x1' in Fp)  
y' = y0' + y1' * u(y0', y1' in Fp)  

|      |                                                                 G2                                                                |
|------|:---------------------------------------------------------------------------------------------------------------------------------:|
| r'   | 0x1a0111ea397fe69a4b1ba7b6434bacd764774b84f38512bf6730d2a0f6b0f6241eabfffeb153ffffb9feffffffffaaab                                |
| x'_0 | 0x024aa2b2f08f0a91260805272dc51051c6e47ad4fa403b02b4510b647ae3d1770bac0326a805bbefd48056c8c121bdb8                                |
| x'_1 | 0x13e02b6052719f607dacd3a088274f65596bd0d09920b61ab5da61bbdc7f5049334cf11213945d57e5ac7d055d042b7e                                |
| y'_0 | 0x0ce5d527727d6e118cc9cdc6da2e351aadfd9baa8cbdd3a76d429a695160d12c923ac9cc3baca289e193548608b82801                                |
| y'_1 | 0x0606c4a02ea734cc32acd2b02bc28b99cb3e287e85a763af267492ab572e99ab3f370d275cec1da1aaa9075ff05f79be                                |
| h'   | 0x5d543a95414e7f1091d50792876a202cd91de4547085abaa68a205b2e5a7ddfa628f1cb4d9e82ef21537e293a6691ae1616ec6e786f0c70cf1c38e31c7238e5 |
| b'   | 4 * (u + 1)                                                                                                                       |

# Appendix B | _Optimal Ate Pairing_

The primary sources for this algorithm are [Vercauteren](https://eprint.iacr.org/2008/096.pdf), [IETF](https://tools.ietf.org/id/draft-yonezawa-pairing-friendly-curves-02.html#optimal-ate-pairings-over-barreto-lynn-scott-curves), and [Khandaker et-al](https://eprint.iacr.org/2017/1174.pdf).

![optimal ate pairing](https://imgur.com/iW9k2is.png) [IETF](https://tools.ietf.org/id/draft-yonezawa-pairing-friendly-curves-02.html#optimal-ate-pairings-over-barreto-lynn-scott-curves)

![miller](https://imgur.com/U5LAdMh.png) [Khandaker et-al, 2017](https://eprint.iacr.org/2017/1174.pdf)

![pseudo 8-sparse pairing](https://imgur.com/ZUayVgH.png) [Khandaker et-al, 2017](https://eprint.iacr.org/2017/1174.pdf)

# Appendix C | _Implementations_

Python [[1](https://github.com/miracl/core/blob/cef0ac83718ec70e6b1e1411bf0a3d98c1ec6608/python/pair.py#L139)]

Rust [[1](https://github.com/zkcrypto/bls12_381/blob/8fe77daf444efdcf70c5fead1d152a100d62d8ff/src/pairings.rs#L34)], [[2](https://github.com/mratsim/constantine/blob/master/constantine/pairing/pairing_bls12.nim)]



---

[Rene2015](https://eprint.iacr.org/2015/1060.pdf)
