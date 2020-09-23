const path = require("path");
const fs = require("fs");

const { compiler } = require("./huff/src");
const parser = require("./huff/src/parser");

const pathToData = path.posix.resolve(__dirname, "./custom-opcodes");

// uncomment a one file and one macro name below

//const { inputMap, macros, jumptables } = parser.parseFile('f6m_mul_v2.huff', pathToData);
//const { inputMap, macros, jumptables } = parser.parseFile('f6m_mul_v4.huff', pathToData);
const { inputMap, macros, jumptables } = parser.parseFile(
  "f6m_mul_v7.huff",
  pathToData
);

const {
  data: { bytecode: macroCode },
} = parser.processMacro(
  "F6M_MUL_TEST_HARDCODED",
  0,
  [],
  macros,
  inputMap,
  jumptables
);
//} = parser.processMacro('F6M_MUL_BENCH', 0, [], macros, inputMap, jumptables);

console.log("0x" + macroCode);
