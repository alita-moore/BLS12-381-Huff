const Evmc = require("evmc");
const f6m_mul_v7 = require("../custom-opcodes/f6m_mul_v7.json");
const evmasm = require("evmasm");

class MyEVM extends Evmc.Evmc {}

const evmPath = "/home/alita/ethereum/BLS12-381-Huff/GethChain/geth.ipc";
console.log("evm");
const evm = new MyEVM(evmPath);
// const result = evm.execute("test", f6m_mul_v7.f6m_mul_v7.exec.code);

console.log("ran");
