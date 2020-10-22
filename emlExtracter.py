# References :  https://docs.python.org/ko/3.7/library/email.html
#               https://stackoverrun.com/ko/q/10195329
#               https://codingdojang.com/scode/258?orderby=time
#               https://m.blog.naver.com/PostView.nhn?blogId=dudwo567890&logNo=130162403749&proxyReferer=https:%2F%2Fwww.google.com%2F
#               https://thispointer.com/pandas-loop-or-iterate-over-all-or-certain-columns-of-a-dataframe/
#               https://stackoverflow.com/questions/45306988/column-of-lists-convert-list-to-string-as-a-new-column
#               https://stackoverflow.com/questions/3160699/python-progress-bar
#               https://stackoverflow.com/questions/7331351/python-email-header-decoding-utf-8/21715870

import email
import quopri
import re 
import sys
import os
import time
import csv
from html2text import html2text
from glob import glob
from collections import defaultdict
from email.header import make_header
from email.header import decode_header

# update_progress() : Displays or updates a console progress bar
# Accepts a float between 0 and 1. Any int will be converted to a float.
# A value under 0 represents a 'halt'.
# A value at 1 or bigger represents 100%
def update_progress(progress, num):
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
    text = "\rNow Finished : {0} EA / Percent: [{1}] {2:.1f}% {3}".format( num, "#" * block + "-" * (barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def prcessing_dir():
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
                decode_msg_contents = make_header(decode_header(msg_contents))
                eml_dict[header] = str(decode_msg_contents)  

          # Extract text content
          if msg.is_multipart():
            for payload in msg.get_payload():
              encodetype=str(payload.get_charsets()[0])
              if payload.get_content_type() == 'text/html':
                if encodetype == 'None':
                  text_content = payload.get_payload(decode=True).decode('euc-kr','replace')
                  text_content = html2text(text_content)
                elif encodetype == 'cp-850': 
                  text_content = payload.get_payload(decode=True).decode('cp850','replace')
                  text_content = html2text(text_content)
                else:
                  text_content = payload.get_payload(decode=True).decode(encodetype,'replace')
                  text_content = html2text(text_content)
              elif msg.get_content_type() == 'text/plain':  
                  if encodetype == 'None':
                    text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
                  elif encodetype == 'cp-850':
                    text_content = msg.get_payload(decode=True).decode('cp850','replace')
                  else:
                    text_content = msg.get_payload(decode=True).decode(encodetype,'replace')
          else:
            encodetype=str(msg.get_charsets()[0])
            if msg.get_content_type() == 'text/plain':
              if encodetype == 'None': 
                text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
              elif encodetype == 'cp-850': 
                text_content = msg.get_payload(decode=True).decode('cp850','replace')
              else:
                text_content = msg.get_payload(decode=True).decode(encodetype,'replace')

          text_content = re.sub('\s+', ' ', text_content)
          eml_dict['text_content'] = text_content
		  
        except Exception as message:
          print()
          print(real_file_name + " is Convert Fail...!")
          print("Caused by : " + str(message))
          pass
        
        for key, value in eml_dict.items():
          if not value:
            eml_dict[key] = ", ".join(value)

        # Export to CSV
        writer.writerow(eml_dict.values())
        # Update Progress Bar
        update_progress(i/total_size, i)

    # File Close
    fp.close()

def processing_file(real_file_name):
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
              decode_msg_contents = make_header(decode_header(msg_contents))
              eml_dict[header] = str(decode_msg_contents)
              break

        # Extract text content
        if msg.is_multipart():
          for payload in msg.get_payload():
            encodetype=str(payload.get_charsets()[0])
            if payload.get_content_type() == 'text/html':
              if encodetype == 'None':
                text_content = payload.get_payload(decode=True).decode('euc-kr','replace')
                text_content = html2text(text_content)
              elif encodetype == 'cp-850':
                text_content = payload.get_payload(decode=True).decode('cp850','replace')
                text_content = html2text(text_content)
              else:
                text_content = payload.get_payload(decode=True).decode(encodetype,'replace')
                text_content = html2text(text_content)
            elif msg.get_content_type() == 'text/plain':  
                if encodetype == 'None':
                  text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
                elif encodetype == 'cp-850':
                  text_content = msg.get_payload(decode=True).decode('cp850','replace') 
                else:
                  text_content = msg.get_payload(decode=True).decode(encodetype,'replace')
        else:
          encodetype=str(msg.get_charsets()[0])
          if msg.get_content_type() == 'text/plain':
            if encodetype == 'None': 
              text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
            elif encodetype == 'cp-850': 
              text_content = msg.get_payload(decode=True).decode('cp850','replace')  
            else:
              text_content = msg.get_payload(decode=True).decode(encodetype,'replace')

        text_content = re.sub('\s+', ' ', text_content)
        eml_dict['text_content'] = text_content
		  
      except Exception as message:
        print()
        print(real_file_name + " is Convert Fail...!")
        print("Caused by : " + str(message))
        pass

    for key, value in eml_dict.items():
      if not value:
        eml_dict[key] = ", ".join(value)

    # Export to CSV
    writer.writerow(eml_dict.values())
    # Update Progress Bar
    update_progress(1, 1)

    # File Close
    fp.close()

if __name__ == '__main__':
    # Load Ouput CSV
    fp = open("output.csv", "w", newline='', encoding='utf-8-sig')
    writer = csv.writer(fp)

    # Load header information
    with open('header_info.csv', 'r') as fp:
      headers=fp.readline().split(",")
      headers.insert(0, 'file_name')
      headers.insert(1, 'text_content')

    # Write Header  
    writer.writerow(headers)

    if os.path.isdir(sys.argv[1]):
        os.chdir(sys.argv[1])
        prcessing_dir()
    else:
        processing_file(sys.argv[1])