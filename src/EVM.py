class EVM_Stack:
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

class EVM_Mem:
  def __init__(self, size, word_len, stack):
    self.memory = bytearray(size)
    self.word_len = word_len
    self.stack = stack

  def __len__(self):
    return len(self.memory)

  def store(self, offset, bytes_):
    isWordStart = offset % self.word_len == 0
    isWord = len(bytes_) <= self.word_len
    if not isWordStart:
      raise("offset was %d, which is not the start of a word (not a multiple of %d)" % (offset, self.word_len))
    if isWord:
      for i, byte in enumerate(bytes_):
        self.memory[offset + i] = byte
    else:
      raise("%d were given, when the word length %d or less were expected" % (len(bytes_), self.word_len))
  
  def load(self, offset):
    result = bytearray()
    for idx in range(32):
      result.append(self.memory[offset + idx])
    return 
    
class EVM:
  def __init__(self, mem_size, word_len):
    self.word_len = word_len
    self.memory = EVM_Mem(size, word_len)
    self.stack = EVM_Stack(word_len)
  def memstore(self, offset, word):
    if len(word) == self.word_len:
      for byte in word:
        self.memory.