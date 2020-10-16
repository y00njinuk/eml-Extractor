# EML 추출기

### 1. 패키지 목록 및 설치확인
- email, quopri, re, pandas, html2text, glob, collcetions
```
import <package>
```

### 2. 패키지 설치
```
pip install email
pip install quopri
pip install re
pip install pandas
pip install html2text
pip install glob
pip install collections
```

### 3. 필요한 파일 
- emlExtracter.py 경로에 header_info.csv
- emlExtracter.py 경로에 추출한 eml 파일 또는 디렉토리

### 3. 사용방법
- python emlExtracter.py "File or Directory"
```
python emlExtracter.py sample
```

### 4. 결과
- 해당 파일 또는 디렉토리 경로에 ouput.csv 생성

### 5. 향후 수정할 작업
- eml 내에 알 수 없는 문자열 존재 시 인코딩 문제
