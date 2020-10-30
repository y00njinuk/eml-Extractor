# EML 추출기

### 1. 패키지 목록 및 설치확인
- email, quopri, re, pandas, html2text, glob, collcetions, csv
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
pip install csv
```

### 3. 필요한 파일 
- emlExtracter.py 경로에 header_info.csv
- emlExtracter.py 경로에 추출할 eml 디렉토리

### 3. 사용방법
- python emlExtracter.py <directory>
```
python emlExtracter.py sample
```

### 4. 결과
- 해당 실행파일 경로에 ouput.csv 생성
