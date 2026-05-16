# economic-calendar-dashboard

**⚠️ ARCHIVED 2026-05-16** — BLS 가 GitHub Actions datacenter IP 를 403 Forbidden 으로 차단. 자동 fetch path 막힘.

## 학습 결과 (시범 운용)

- ✅ 새 레포 생성·GitHub Actions cron·Pages 활성·PUT contents API 모두 작동 확인
- ✅ BLS ICS 표준 format 발견 — Python parser 코드 transferable
- ❌ BLS 도메인 IP 기반 차단 (datacenter IP 거부)
- 📚 transferable knowledge: 정부 사이트 (BLS·BEA 등) datacenter IP 차단 일반 패턴 — 향후 dashboard 작업 시 사전 평가 의무

## 권고 — 외부 Google Calendar subscribe

BLS 가 ICS 공식 publish 한 이유는 **Google Calendar·Outlook·Apple iCal 에서 직접 subscribe** 하기 위함. dashboard 안 calendar 가 외부 도구 대체 X.

### Subscribe 방법

1. <https://calendar.google.com>
2. 좌측 "다른 캘린더" 옆 **+** → "URL 로 추가"
3. URL paste: `https://www.bls.gov/schedule/news_release/bls.ics`
4. 자동 sync (매일)

## 보존된 코드 (참조용)

- `scripts/collect_data.py` — BLS ICS parser (다른 ICS source 에 재사용 가능)
- `.github/workflows/update.yml` — GitHub Actions cron pattern + debug log commit

향후 datacenter IP 우회 (Cloudflare Worker, paid proxy 등) 시 코드 재활용 가능. 현재는 archive.
