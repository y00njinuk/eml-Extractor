# References :  https://stackoverrun.com/ko/q/10195329
#               https://codingdojang.com/scode/258?orderby=time
#               https://m.blog.naver.com/PostView.nhn?blogId=dudwo567890&logNo=130162403749&proxyReferer=https:%2F%2Fwww.google.com%2F

import email
import quopri
import re 
import pandas as pd
from html2text import html2text
from glob import glob

headers = []
names = []
text_contents = []
for eml_file in glob('*.eml'):
    # Code to extract a particular section from raw emails.
    with open(eml_file, 'r') as fp:
      names.append(eml_file)
      msg = email.message_from_file(fp)
      # print(msg.items())

    # Extract Header
      headers.extend(msg.items())

    # Extract Text Content
      if msg.is_multipart():
          for payload in msg.get_payload():
            if payload.get_content_type() == 'text/html':
              text_content = payload.get_payload(decode=True).decode('euc-kr','replace')
              text_content = html2text(text_content)
            elif msg.get_content_type() == 'text/plain':  
              text_content = msg.get_payload(decode=True).decode('euc-kr','replace')
      else:
          if msg.get_content_type() == 'text/plain':  
            text_content = msg.get_payload(decode=True).decode('euc-kr','replace')

    text_content = re.sub('\s+', ' ', text_content)
    text_contents.append(text_content)

# print(headers)

# Covert DataFrame
file_list = pd.DataFrame({'eml_name': names,'text_content': text_contents}, dtype=str)
print(file_list['text_content'])