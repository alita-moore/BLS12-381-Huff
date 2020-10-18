"""
Extremely basic EVM implementation
"""
import math
from datetime import datetime

now = str(datetime.now())
log_file = open(".evm/logs_" + now, 'w+')

class Stack:
  def __init__(self, word_len):
    self.stack=bytearray()
    self.word_len=word_len

  def __len__(self):
    return len(self.stack)
  
  def push(self, word):
    isWord = len(word) <= self.word_len
    for idx in range(self.word_len):
      try:
        self.stack.append(word[idx])
      except IndexError:
        self.stack.append(0)

  def top(self):
    result = bytearray()
    for idx in range(self.word_len):
      try:
        result.append(self.stack[idx - self.word_len])
      except IndexError:
        result.append(0)
    return result
  
  def pop(self):
    topWord = self.stack[-32:]
    del self.stack[-32:]
    return topWord

class Memory:
  def __init__(self, word_len):
    self.mem = bytearray()
    self.word_len = word_len

  def __len__(self):
    return len(self.mem)

  def __str__(self):
    return "\n".join(self._toString_(self.mem, 0))

  def _toString_(self, array, wordOffset):
    string = []
    for idx in range(int(len(array) / self.word_len)):
      byteslice = array[idx * self.word_len: (idx + 1) * self.word_len]
      temp = ['{0:08b}'.format(byte) for byte in byteslice]
      string.append("| %3d | " % (wordOffset + idx) + " ".join(temp) + " |")
    return string

  def _appendWord_(self, numWords=1):
    for _ in range(numWords):
      self.mem.extend(bytearray(32))
      log = "word added | new mem size : %d words \n" % (len(self.mem) // self.word_len)
      log_file.write(log)

  def _logStore_(self, memBefore, offset, bytes_):
    logs = (str(datetime.now()), offset, len(bytes_))
    log_file.write("%s | mstore | offset: %d number of bytes: %d \n" % logs)

    lowBound = self.word_len*offset//self.word_len
    upBound = self.word_len*((offset + 2*self.word_len) // self.word_len) 
    sliceBefore = self._toString_(memBefore[lowBound:upBound], offset//self.word_len)
    sliceAfter = self._toString_(self.mem[lowBound:upBound], offset//self.word_len)
    memCompare = "\tBEFORE\n\t" + "\n\t".join(sliceBefore) + "\n"
    memCompare += "\tAFTER\n\t" + "\n\t".join(sliceAfter) + "\n"    
    log_file.write(memCompare)

  def store(self, offset, bytes_):
    if offset + self.word_len > len(self.mem):
      required = (offset + 2*self.word_len) // self.word_len
      current = len(self.mem) // self.word_len
      self._appendWord_(required - current)
    isWord = len(bytes_) <= self.word_len
    if isWord:
      debug = self.mem.copy()
      for i, byte in enumerate(bytes_):
        self.mem[offset + i] = byte
      self._logStore_(debug, offset, bytes_)
    else:
      raise("%d bytes were given, when a word length %d or less were expected" % (len(bytes_), self.word_len))

  def load(self, offset):
    result = bytearray()
    for idx in range(32):
      result.append(self.mem[offset + idx])
    return result
    
class EVM:
  def __init__(self, word_len):
    self.word_len = word_len
    self.m = Memory(word_len)
    self.stack = Stack(word_len)

  def mstore(self, offset, bytes_):
    isMultiWord = len(bytes_) > self.word_len
    if isMultiWord:
      baseOffset = 0
      for idx in range(math.floor(len(bytes_) / self.word_len)):
        baseOffset = idx * self.word_len
        word = bytes_[baseOffset:baseOffset + self.word_len]
        self.m.store(offset + baseOffset, word)
      if len(bytes_) % self.word_len != 0:
        baseOffset = baseOffset + self.word_len
        word = bytes_[baseOffset:]
        self.m.store(offset + baseOffset, word)
    else:
      self.m.store(offset, bytes_)
