import pandas as pd
import csv

class CSVIterator:
  def __init__(self, filename, data_start_mark, data_end_mark, stellwagen = False):
    self.stellwagen = stellwagen
    self.filename = filename
    self.twoDArray = self.csvToArr(filename)
    self.data_start_mark = data_start_mark
    self.data_end_mark = data_end_mark
    self.curr_ind = 0
  
  def hasNextData(self):
    return self.curr_ind < len(self.twoDArray) and self.data_start_mark in [arr[0] for arr in self.twoDArray[self.curr_ind:]]
    
  def getNextData(self):
    if not self.hasNextData():
      raise Exception('No data left')
    
    # Move to the column row
    while self.twoDArray[self.curr_ind][0] != self.data_start_mark:
      self.curr_ind += 1

    if self.stellwagen:
      self.curr_ind += 1
      
    columns = self.twoDArray[self.curr_ind]

    # Move to the start of the data
    self.curr_ind += 1
    
    data_start_ind = self.curr_ind

    while self.curr_ind < len(self.twoDArray) and self.twoDArray[self.curr_ind][0] != self.data_end_mark:
      self.curr_ind += 1

    data = self.twoDArray[data_start_ind:self.curr_ind]

    try:
      return pd.DataFrame(data, columns = columns)
    except:
      raise Exception(f'Error parsing {self.filename}')

def csvToArr(filename):
    twoDArray = []
    with open(filename, newline='') as csvfile:
      data = csv.reader(csvfile, delimiter=',', quotechar='"')
      for row in data:
        twoDArray.append(row)
    return [arr if arr else [''] for arr in twoDArray]


def get_all_data(csv_it):
  chunks = []
  while csv_it.hasNextData():
    next_data = csv_it.getNextData()
    chunks.append(next_data)
  try:
    all_data = pd.concat(chunks, ignore_index=True)
  except:
    raise Exception(f'Error concatenating {csv_it.filename}')
  return all_data