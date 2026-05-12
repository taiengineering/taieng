// factory-list.patch — fpTab2 + collectFactoryBody notification_time 패치
// v1.0.0 (FN-07 추가)
// 적용 대상: factory-list.html
// 수정 위치 1: fpTab2() 함수 체크박스 앞
//   추가: '<div class="col-6">...알림 발송 시간 input...' 필드
// 수정 위치 2: collectFactoryBody() 마지막
//   추가: notification_time 필드 수집
//
// DB: factories.notification_time (time without time zone, default '07:00:00')
// 미간주: Supabase migration be07_factory_notification_time 이미 적용

/*
 ===== fpTab2 함수 수정 =====

 기존 (챙크박스 바로 앞):
     '<div class="col-12"><div class="form-check">...공장 등록 여부...

 변경후 (그 앞에 삽입):
     '<div class="col-6"><label class="form-label small">현장별 알림 시간</label>'
     + '<input type="time" class="form-control" id="fp-notif-time" value="'+escapeHtml(v('notification_time')||'07:00')+'"'+dis+'></div>'
     + '<div class="col-6"><div class="alert alert-light py-2 px-3 mb-0" style="font-size:.8rem;">바스 ......

 ===== collectFactoryBody 함수 수정 =====

 기존 (마지막 줄):
     longitude:hiddenLongitude!=null?hiddenLongitude:undefined

 변경후:
     longitude:hiddenLongitude!=null?hiddenLongitude:undefined,
     notification_time:(function(){var el=document.getElementById('fp-notif-time');return el&&el.value?el.value:undefined;})()
*/
