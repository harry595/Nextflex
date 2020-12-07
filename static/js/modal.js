function first_modal(){
  document.querySelector('body').style.overflow='hidden';
  document.querySelector('.dimmed').style.display='block';
  document.querySelector('.wrapper').style.display='block';
}

function first_cancel(){
  document.querySelector('body').style.overflow='auto';
  document.querySelector('.dimmed').style.display='none';
  document.querySelector('.wrapper').style.display='none';
}

function second_modal(){
  document.querySelector('.dimmed').style.zIndex='3';
  document.querySelector('.wrapper2').style.display='block';
}
function second_cancel(){
  first_cancel();
  document.querySelector('.dimmed').style.zIndex='1';
  document.querySelector('.wrapper2').style.display='none';

}

function third_modal(order_id){
  document.querySelector('body').style.overflow='hidden';
  document.querySelector('.dimmed').style.display='block';
  document.querySelector('.wrapper3').style.display='block';
  document.getElementById('order_id').value=order_id;
}

function third_cancel(){
  document.querySelector('body').style.overflow='auto';
  document.querySelector('.dimmed').style.display='none';
  document.querySelector('.wrapper3').style.display='none';
}

function post_account() {
  let account_num = $('#acc_num').val();
  let account_type = $('#acc_type').val();
  let account_date = $('#plan_month').val();
  
  $.ajax({
    type: "POST",
    url: "/post_account",
    data: {
      'account_num': account_num,
      'account_type': account_type,
      'account_date': account_date
    },
    success: function (response) {
      if (response['result'] == 'success') {
        window.location.reload()
      }
    }
  })
}

function post_rating() {
  let rating=0;
  let order_id=document.getElementById('order_id').value;
  console.log(document.getElementById('order_id').value);
  if($('#star5').is(':checked')) rating=5;
  else if($('#star4').is(':checked')) rating=4;
  else if($('#star3').is(':checked')) rating=3;
  else if($('#star2').is(':checked')) rating=2;
  else if($('#star1').is(':checked')) rating=1;
  else rating=0;

  $.ajax({
    type: "GET",
    url: "/returnmovie",
    data: {
      'oid': order_id,
      'ostar': rating
    },
    success: function (response) {
      if (response['result'] == 'success') {
        window.location.reload()
      }
    }
  })
}

 /*
$(".btn-search").click(function(){
  var town_input = document.getElementById('town_input').value;
  $.ajax({ // .like 버튼을 클릭하면 <새로고침> 없이 ajax로 서버와 통신하겠다.
    type: "POST", // 데이터를 전송하는 방법을 지정
    url: 'townsearch/', // 통신할 url을 지정
    data: {'town_input': town_input, 'csrfmiddlewaretoken': '{{ csrf_token }}'}, // 서버로 데이터 전송시 옵션
    dataType: "json", // 서버측에서 전송한 데이터를 어떤 형식의 데이터로서 해석할 것인가를 지정, 없으면 알아서 판단
    // 서버측에서 전송한 Response 데이터 형식 (json)
    success: function(data){ 
      for (var i in data['town_input']) {    
        var div = document.createElement('option');
        div.innerHTML = data['town_input'][i];
        document.getElementById('town').appendChild(div);
      }
      var div = document.createElement('label');
      div.innerHTML = '"'+town_input+'"으로 검색 결과';
      document.getElementById('whatinput').appendChild(div);
    },
    error: function(request, status, error){ // 통신 실패시 - 리다이렉트
      alert("wrong input")
      window.location.replace("/")
    },
  });
})

$(".btn-2").click(function(){
  var town_input=$("#town option:selected").val()
  var btnToken=$("#btnToken").val()
  $.ajax({ // .like 버튼을 클릭하면 <새로고침> 없이 ajax로 서버와 통신하겠다.
    type: "POST", // 데이터를 전송하는 방법을 지정
    url: 'townenroll/', // 통신할 url을 지정
    data: {'town_input': town_input, 'btnToken': btnToken,'csrfmiddlewaretoken': '{{ csrf_token }}'}, // 서버로 데이터 전송시 옵션
    dataType: "json", // 서버측에서 전송한 데이터를 어떤 형식의 데이터로서 해석할 것인가를 지정, 없으면 알아서 판단
    // 서버측에서 전송한 Response 데이터 형식 (json)
    success: function(data){ 
      document.querySelector('.bg-modal2').style.display ='none';
      document.querySelector('.bg-modal').style.display ='none';
      window.location.replace("/mypage")
    },
    error: function(request, status, error){ // 통신 실패시 - 리다이렉트
      alert("wrong input")
      window.location.replace("/")
    },
  });
})
*/