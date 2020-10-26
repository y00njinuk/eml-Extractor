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
import html2text
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
    text = "\rNow Finished : {0} EA / Percent: [{1}] {2:.1f}% {3}"\
      .format( num, "#" * block + "-" * (barLength-block), progress*100, status)
    sys.stdout.write(text)
    sys.stdout.flush()

def convert_header(real_file_name, header, headerList): 
    result_header = []

    for header_info in headerList:
      try:
        codeprint, charset = header_info

        # unknonw-8bit -> euc-kr
        if charset == 'unknown-8bit': 
          charset = 'euc-kr'
  
        decode_msg_header = str(make_header([(codeprint, charset)]))
        result_header.append(decode_msg_header)
  
      # If error occured in decoding, reset character set  
      except Exception as header_decodeError:
        if charset == 'iso-2022-jp': 
          new_charset = 'shift_jis'
        elif charset == 'gb2312':
          new_charset = 'gbk'
  
        # [Error] unkonwn-8bit -> euc-kr
        # [Solved] euc-kr -> utf-8 (but, character is garbled)
        else: 
          new_charset = 'utf-8'  
  
        # print('\n')
        # print("----[Error] File Name : " + real_file_name + "\nCaused by : " + str(header_decodeError))
        # print("----[Solved] Retry '"+ header + "' to Setting Charcter : " + charset + " -> " + new_charset)
        
        new_decode_msg_header = str(make_header([(codeprint, new_charset)]))
        result_header.append(new_decode_msg_header)
        continue 
      
    return ' '.join(result_header)

def convert_contents(real_file_name, part, msg, content_type, encode_type, check_multipart):
  text_content = ''

  h = html2text.HTML2Text()

  # Skipped HTML Tag Element
  # h.ignore_emphasis = True
  # h.ignore_images = True 
  # h.ignore_links = True 
  # h.ignore_tables = True 
  # h.images_as_html = True
  # h.images_to_alt = True

  # get_payload(decode=True) : quoted-printable, base64, 7bit -> byte
  # decode(encode_type,'replace') : byte -> euc-kr, utf8, cp-850, iso-2022-jp -> text 
  try:
    if check_multipart is True:
      if encode_type == 'None':
        text_content = part.get_payload(decode=True).decode('euc-kr','replace')
      elif encode_type == 'cp-850':
        text_content = part.get_payload(decode=True).decode('cp850','replace') 
      elif encode_type == 'iso-2022-jp':
        text_content = part.get_payload(decode=True).decode('shift_jis','replace') 
      else:
        text_content = part.get_payload(decode=True).decode(encode_type,'replace')    
        
    else:
      if encode_type == 'None':
        text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
      elif encode_type == 'cp-850': 
        text_content = msg.get_payload(decode=True).decode('cp850','replace') 
      elif encode_type == 'iso-2022-jp': 
        text_content = msg.get_payload(decode=True).decode('shift_jis','replace') 
      else:
        text_content = msg.get_payload(decode=True).decode(encode_type,'replace')             

  except Exception as text_convertError:
    # [Error] unkonwn-8bit -> euc-kr
    # [Solved] euc-kr -> utf-8 (but, character is garbled)
    new_encode_type = 'utf-8'

    # print('\n')
    # print("----[Error] File name : " + real_file_name + "\nCaused by : " + str(text_convertError) + '\n')
    # print("----[Solved] Retry 'text_content' to Setting Charcter : " + encode_type + " -> " + new_encode_type)

    if check_multipart is True:
      text_content = part.get_payload(decode=True).decode(new_encode_type,'replace')
    else:
      text_content = msg.get_payload(decode=True).decode(new_encode_type,'replace')
    pass
  
  if content_type == 'text/html':  
    text_content = h.handle(text_content)

  del h
  text_content = re.sub('\\s+', ' ', text_content)

  return text_content        

def prcessing_dir():
    total_size = len(glob('*.eml'))

    for i, real_file_name in enumerate(glob('*.eml'), 1):
      # 1. File open
      with open(real_file_name, 'rb') as fp:
        try:
          msg = email.message_from_binary_file(fp)
          eml_dict=defaultdict(list,{ key:[] for key in headers })

          # 2. Extract header
          for msg_header, msg_contents in msg.items():
            for header in eml_dict.keys():
              if msg_header == header:
                headerList = decode_header(msg_contents)
                eml_dict[header] = convert_header(real_file_name, header, headerList)
            
          # 3. Extract content
          text_contents = []
          if msg.is_multipart():
            for part in msg.get_payload():
              encode_type = str(part.get_content_charset())
              content_type = part.get_content_type()
              text_content = convert_contents(real_file_name, part, msg, content_type, encode_type, True)
          else:
            encode_type = str(msg.get_content_charset())
            content_type = msg.get_content_type()
            text_content = convert_contents(real_file_name, None, msg, content_type, encode_type, False)
  
          text_contents.append(text_content)
          
          eml_dict['file_name'] = real_file_name
          eml_dict['text_content'] = ' '.join(text_contents)
		      
          # 4. Insert value to dictionary
          for key, value in eml_dict.items():
            if not value:
              eml_dict[key] = ", ".join(value)
  
          # 5. Export to CSV
          writer.writerow(eml_dict.values())
          # 6. Update Progress Bar
          update_progress(i/total_size, i)
          # 7. File Close
          fp.close()

        except Exception as convertError:
          print("----[Error] File name : " + real_file_name + "\nCaused by : " + str(convertError) + '\n')
          continue

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