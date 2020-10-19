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
    self.data = bytearray()
    self.word_len = word_len
  def __len__(self):
    return len(self.data)
  def __str__(self):
    return "\n".join(self._toString_(self.data))
  def _toString_(self, array, wordOffset=0, start=0, end=0):
    # converts byte to 8bit binary and adds start / end markers if defined
    def encode(byte, word, col):
      index = word * self.word_len + col
      if start != end:
        if index == start and end - start == 1:
          return '*{0:08b}*'.format(byte)
        elif index == start:
          return '*{0:08b}'.format(byte)
        elif index == end - 1:
          return '{0:08b}*'.format(byte)
      return '{0:08b}'.format(byte)
    # create formmated table with each row being a formatted memory row
    table = []
    for word in range(len(array) // self.word_len):
      byteslice = array[word * self.word_len: (word + 1) * self.word_len]
      row = " ".join([encode(byte, word, col) for col, byte in enumerate(byteslice)])
      table.append("| %3d | %s |" % (wordOffset + word, row))
    return table
  def _appendWord_(self, numWords=1, debug=True):
    for _ in range(numWords):
      self.data.extend(bytearray(32))
      if debug:
        memWords = len(self.data) // self.word_len
        log = "\t| word added | total size of memory : %d words \n" % (memWords)
        log_file.write(log)
  def store(self, offset, bytes_, debug=True):
    # allocate memory to spec
    if offset + len(bytes_) > len(self.data):
      required = math.ceil((offset + len(bytes_)) / self.word_len)
      current = len(self.data) // self.word_len
      self._appendWord_(required - current)
    # store bytes in memory
    if len(bytes_) <= self.word_len:
      for i, byte in enumerate(bytes_):
        self.data[offset + i] = byte
    else:
      raise("%d bytes were given, when a word length %d or less were expected" % (len(bytes_), self.word_len))
    if debug:
      wordOffset = offset // self.word_len
      overflows = (offset % self.word_len + len(bytes_)) > self.word_len
      wordsAffected = [wordOffset, wordOffset + 1] if overflows else [wordOffset] 
      log = "\t|   mstore   | assigned %d byte(s) within the word(s) %a\n" % (len(bytes_), wordsAffected)
      log_file.write(log)
  def load(self, offset):
    finalByte = offset + self.word_len
    if finalByte > len(self.data):
      return self.data[offset:finalByte]
    
class EVM:
  def __init__(self, word_len):
    self.word_len = word_len
    self.m = Memory(word_len)
    self.stack = Stack(word_len)
  def _LOGMSTORE_(self, memBefore, offset, bytes_):
    """ Creates a log for the mstore opcode; e.g.
      2020-10-18 21:18:57.303959 | mstore | offset: 50, number of bytes changed: 1 
	      | word added | size of allocated memory : 1 words 
        | word added | size of allocated memory : 2 words 
        |   mstore   | assigned 1 byte(s) within the word(s) [1]
        BEFORE # there was initially no allocated memory
          
        AFTER # only one byte was changed in the 2nd word of memory                                                                                                                                                                    
        |   1 | 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 *01111011* 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 00000000 |
    """   
    # establish the start / end to correctly splice the memory
    firstWord = offset // self.word_len
    lastWord = (offset + len(bytes_)) // self.word_len
    firstByte = firstWord * self.word_len
    lastByte = (lastWord + 1) * self.word_len # because includes changes to last word
    # slice the memory and format into strings
    sliceBefore = memBefore[firstByte:lastByte]
    sliceAfter = self.m.data[firstByte:lastByte]
    before = self.m._toString_(sliceBefore, firstWord)
    # define the relative end and start for labeling changes in log
    relStart = offset % self.word_len
    relEnd = relStart + len(bytes_)
    after  = self.m._toString_(sliceAfter, firstWord, relStart, relEnd)
    # format the before and after memory strings for comparison
    log = "\tBEFORE\n\t" + "\n\t".join(before) + "\n"
    log += "\tAFTER\n\t" + "\n\t".join(after) + "\n"    
    log_file.write(log)
  def mstore(self, offset, bytes_, debug=True):
    memCopy = self.m.data.copy()
    if debug:
      logs = (str(datetime.now()), offset, len(bytes_))
      log_file.write("%s | mstore | offset: %d bytes, bytes changed: %d \n" % logs)
    # special-handling for data that's greater than 1 word
    if len(bytes_) > self.word_len:
      baseOffset = 0
      for idx in range(len(bytes_) // self.word_len):
        baseOffset = idx * self.word_len
        word = bytes_[baseOffset:baseOffset + self.word_len]
        self.m.store(offset + baseOffset, word)
      if len(bytes_) % self.word_len != 0:
        baseOffset = baseOffset + self.word_len
        word = bytes_[baseOffset:]
        self.m.store(offset + baseOffset, word)
    # remaining bytes <= word_len (or if initial bytes were less than or 1 word)
    else:
      self.m.store(offset, bytes_)
    if debug:
      self._LOGMSTORE_(memCopy, offset, bytes_)
