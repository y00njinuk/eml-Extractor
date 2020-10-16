# References :  https://docs.python.org/ko/3.7/library/email.html
#               https://stackoverrun.com/ko/q/10195329
#               https://codingdojang.com/scode/258?orderby=time
#               https://m.blog.naver.com/PostView.nhn?blogId=dudwo567890&logNo=130162403749&proxyReferer=https:%2F%2Fwww.google.com%2F
#               https://thispointer.com/pandas-loop-or-iterate-over-all-or-certain-columns-of-a-dataframe/
#               https://stackoverflow.com/questions/45306988/column-of-lists-convert-list-to-string-as-a-new-column
#               https://stackoverflow.com/questions/3160699/python-progress-bar

import email
import quopri
import re 
import pandas as pd
import sys
import os
import time
from html2text import html2text
from glob import glob
from collections import defaultdict

# update_progress() : Displays or updates a console progress bar
# Accepts a float between 0 and 1. Any int will be converted to a float.
# A value under 0 represents a 'halt'.
# A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1:.1f}% {2}".format( "#" * block + "-" * (barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def prcessing_dir():
    eml_dataframe = pd.DataFrame(columns=headers)
    total_size = len(glob('*.eml'))

    for i, real_file_name in enumerate(glob('*.eml'), 1):
      # File open
      with open(real_file_name, 'r', encoding='UTF8') as fp:
        try:
          msg = email.message_from_file(fp)
          eml_dict=defaultdict(list,{ key:[] for key in headers })

          # Extract header
          for msg_header, msg_contents in msg.items():
            eml_dict['file_name'] = real_file_name
            for header in eml_dict.keys():
              if(msg_header == header):
                eml_dict[header].append(re.sub(r'[\n\t]', '', msg_contents))
                break;

          # Extract text content
          if msg.is_multipart():
            for payload in msg.get_payload():
              encodetype=str(payload.get_charsets()[0])
              if payload.get_content_type() == 'text/html':
                if encodetype == 'None':
                  text_content = payload.get_payload(decode=True).decode('euc-kr','replace')
                  text_content = html2text(text_content)
                else:
                  text_content = payload.get_payload(decode=True).decode(encodetype,'replace')
                  text_content = html2text(text_content)
              elif msg.get_content_type() == 'text/plain':  
                  if encodetype == 'None':
                    text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
                  else:
                    text_content = msg.get_payload(decode=True).decode(encodetype,'replace')
          else:
            encodetype=str(msg.get_charsets()[0])
            if msg.get_content_type() == 'text/plain':
              if encodetype == 'None': 
                text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
              else:
                text_content = msg.get_payload(decode=True).decode(encodetype,'replace')

          text_content = re.sub('\s+', ' ', text_content)
          eml_dict['text_content'] = text_content
		  
        except Exception as message:
          print()
          print(real_file_name + " is Convert Fail...!")
          print("Caused by : " + str(message))
          pass

      # Convert dictionary to series
      eml_series = pd.Series(eml_dict)
      # Insert seires to dataframe
      eml_dataframe = eml_dataframe.append(eml_series, ignore_index=True)
      update_progress(i/total_size)

    # Iterate over the sequence of column names
    for column in eml_dataframe:
       # Select column contents by column name using [] operator
      if(column == "text_content" or column == 'file_name'):
        eml_dataframe[column] = [','.join(map(str, l)) for l in eml_dataframe[column]]

    # Export to csv
    eml_dataframe.to_csv('output.csv', index=False, encoding='utf-8-sig')

def processing_file(real_file_name):
    eml_dataframe = pd.DataFrame(columns=headers)

    # File open
    with open(real_file_name, 'r', encoding='UTF8') as fp:
      try:
        msg = email.message_from_file(fp)
        eml_dict=defaultdict(list,{ key:[] for key in headers })

        # Extract header
        for msg_header, msg_contents in msg.items():
          eml_dict['file_name'] = real_file_name
          for header in eml_dict.keys():
            if(msg_header == header):
              eml_dict[header].append(re.sub(r'[\n\t]', '', msg_contents))
              break;

        # Extract text content
        if msg.is_multipart():
          for payload in msg.get_payload():
            encodetype=str(payload.get_charsets()[0])
            if payload.get_content_type() == 'text/html':
              if encodetype == 'None':
                text_content = payload.get_payload(decode=True).decode('euc-kr','replace')
                text_content = html2text(text_content)
              else:
                text_content = payload.get_payload(decode=True).decode(encodetype,'replace')
                text_content = html2text(text_content)
            elif msg.get_content_type() == 'text/plain':  
                if encodetype == 'None':
                  text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
                else:
                  text_content = msg.get_payload(decode=True).decode(encodetype,'replace')
        else:
          encodetype=str(msg.get_charsets()[0])
          if msg.get_content_type() == 'text/plain':
            if encodetype == 'None': 
              text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
            else:
              text_content = msg.get_payload(decode=True).decode(encodetype,'replace')

        text_content = re.sub('\s+', ' ', text_content)
        eml_dict['text_content'] = text_content
		  
      except Exception as message:
        print()
        print(real_file_name + " is Convert Fail...!")
        print("Caused by : " + str(message))
        pass

    # Convert dictionary to series
    eml_series = pd.Series(eml_dict)
    # Insert seires to dataframe
    eml_dataframe = eml_dataframe.append(eml_series, ignore_index=True)

    # Iterate over the sequence of column names
    for column in eml_dataframe:
      # Select column contents by column name using [] operator
      if(column == "text_content" or column == 'file_name'): continue
      eml_dataframe[column] = [','.join(map(str, l)) for l in eml_dataframe[column]]

    # Export to csv
    eml_dataframe.to_csv('output.csv', index=False, encoding='utf-8-sig')
    update_progress(1)

if __name__ == '__main__':
    # Load header information
    with open('header_info.csv', 'r') as fp:
      headers=fp.readline().split(",")
      headers.insert(0, 'file_name')
      headers.insert(1, 'text_content')

    if os.path.isdir(sys.argv[1]):
        os.chdir(sys.argv[1])
        prcessing_dir()
    else:
        processing_file(sys.argv[1])