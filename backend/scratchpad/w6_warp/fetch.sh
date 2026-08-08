#!/bin/bash
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36"
while IFS=$'\t' read -r h url mids; do
  out="dl/$h"
  [ -s "$out.txt" ] && continue
  curl -sL --max-time 45 -A "$UA" "$url" -o "$out.bin" 2>/dev/null
  ft=$(file -b "$out.bin" 2>/dev/null)
  case "$ft" in
    *PDF*) pdftotext -layout "$out.bin" "$out.txt" 2>/dev/null ;;
    *HTML*|*ASCII*|*text*|*Unicode*) python3 -c "
import sys,re,html
d=open('$out.bin','rb').read().decode('utf-8','ignore')
d=re.sub(r'(?is)<(script|style).*?</\1>',' ',d)
d=re.sub(r'(?s)<[^>]+>',' ',d)
print(html.unescape(re.sub(r'[ \t]+',' ',d)))" > "$out.txt" 2>/dev/null ;;
  esac
  [ -s "$out.txt" ] || echo "FAIL $h $url" >> fetch_fail.log
done < dl_list.tsv
