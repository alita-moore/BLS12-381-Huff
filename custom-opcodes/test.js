const expected = require("./f6m_mul_v7.json");
const path = require("path");
const parser = require("../huff/src/parser");

const pathToData = path.posix.resolve(__dirname, "./");

const { inputMap, macros, jumptables } = parser.parseFile(
  "f6m_mul_v7.huff",
  pathToData
);

const f6m_mul = parser.processMacro(
  "F6M_MUL_TEST_HARDCODED",
  0,
  [],
  macros,
  inputMap,
  jumptables
);

console.log(f6m_mul);

const isF6mCorrect =
  "0x" + f6m_mul.data.bytecode === expected.f6m_mul_v7.exec.code;
const message = `f6m_mul ${isF6mCorrect ? "passed" : "failed"}`;

console.log(message);
