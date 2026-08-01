
## 데이터시트·그래프 추출 도구

업체 데이터시트에서 물성을 뽑고, 논문 그래프에서 곡선을 디지타이즈한다.

### extract_datasheet.py — PDF → 물성 텍스트
```
extract_datasheet.py <pdf|url> [--ocr] [--dpi 300] [--lang eng|kor|eng+kor]
```
텍스트 레이어를 먼저 시도하고, 비어 있으면(Illustrator로 만든 이미지 전용 PDF —
Kuraray FCCL 브로슈어 같은 경우) 자동으로 OCR로 폴백한다.

### digitize_curve.py — 그래프 이미지 → 좌표
```
digitize_curve.py chart.png --probe                    # 색 후보·크기 확인
digitize_curve.py chart.png --color "#1f77b4" \
  --px0 100 --py0 445 --px1 720 --py1 60 \
  --x0 0 --y0 0 --x1 0.8 --y1 250 --csv out.csv
```
검증: 알려진 곡선(Kapton HN 실측)으로 왕복 시험 시 UTS 231.0→231.5 MPa,
파단변형률 일치, 평균 상대오차 1.9%. 원점 부근은 값이 0에 가까워 상대오차가
커지므로 절대값으로 판단할 것.

### 필요 패키지
```
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-kor
pip install pytesseract pdf2image opencv-python-headless
```
