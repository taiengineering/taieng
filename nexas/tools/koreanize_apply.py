#!/usr/bin/env python3
"""One-off batch: replace common English UI strings with Korean in nexas HTML."""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKIP = {"demo.html", "koreanize_apply.py"}

# Order matters: longer / more specific first where needed
REPLACEMENTS = [
    ('<html lang="zxx">', '<html lang="ko">'),
    ('<html lang="en">', '<html lang="ko">'),
    ('aria-label="Toggle navigation"', 'aria-label="메뉴 열기"'),
    ('placeholder="Search....."', 'placeholder="검색..."'),
    ('placeholder="Enter Your Full Name"', 'placeholder="이름을 입력하세요"'),
    ('placeholder="Enter Your Email Address"', 'placeholder="이메일 주소를 입력하세요"'),
    ('placeholder="Enter Your Email"', 'placeholder="이메일을 입력하세요"'),
    ('placeholder="Enter Your Project Details...."', 'placeholder="문의 내용을 입력하세요"'),
    ('<h6 class="widget-title">Menu</h6>', '<h6 class="widget-title">메뉴</h6>'),
    ('<h6 class="widget-title">About Us</h6>', '<h6 class="widget-title">회사 소개</h6>'),
    ('<h6 class="widget-title">Services</h6>', '<h6 class="widget-title">서비스</h6>'),
    ('<h6 class="widget-title">Our Link</h6>', '<h6 class="widget-title">바로가기</h6>'),
    ('<h2>Contact with Us</h2>', '<h2>문의하기</h2>'),
    ('<p class="pe-5">Subscribe to our newsletter and we will bring you the latest news. Roin tincidunt nisl et odio faucibus</p>',
     '<p class="pe-5">뉴스레터를 구독하시면 최신 소식을 보내드립니다.</p>'),
    ('<p>Subscribe to our newsletter and we will bring you the latest news. Roin tincidunt nisl et odio faucibus</p>',
     '<p>뉴스레터를 구독하시면 최신 소식을 보내드립니다.</p>'),
    ('<button type="submit" class="btn btn-base">Submit your project</button>',
     '<button type="submit" class="btn btn-base">문의 보내기</button>'),
    ('<p>© Copyright 2021 All rights reserved.</p>', '<p>© TAI Engineering. 무단 복제를 금합니다.</p>'),
    ('<p>Made theme by\xa0<a href="https://themeforest.net/user/themefie">Themefie.</a></p>',
     '<p>원본 테마: Themefie</p>'),
    ('<p>Made theme by <a href="https://themeforest.net/user/themefie">Themefie.</a></p>',
     '<p>원본 테마: Themefie</p>'),
    ('alt="img"', 'alt=""'),
    ('alt="#"', 'alt=""'),
    # Footer quick links (template defaults)
    ('<i class="fas fa-angle-right"></i>About</a>', '<i class="fas fa-angle-right"></i>회사 소개</a>'),
    ('<i class="fas fa-angle-right"></i>Service</a>', '<i class="fas fa-angle-right"></i>서비스</a>'),
    ('<i class="fas fa-angle-right"></i>Team</a>', '<i class="fas fa-angle-right"></i>팀</a>'),
    ('<i class="fas fa-angle-right"></i>Blog</a>', '<i class="fas fa-angle-right"></i>블로그</a>'),
    ('<i class="fas fa-angle-right"></i>Graphics </a>', '<i class="fas fa-angle-right"></i>그래픽 </a>'),
    ('<i class="fas fa-angle-right"></i>Web Design </a>', '<i class="fas fa-angle-right"></i>웹 디자인 </a>'),
    ('<i class="fas fa-angle-right"></i>Web Development </a>', '<i class="fas fa-angle-right"></i>웹 개발 </a>'),
    ('<i class="fas fa-angle-right"></i>Help </a>', '<i class="fas fa-angle-right"></i>도움말 </a>'),
    ('<i class="fas fa-angle-right"></i>Support </a>', '<i class="fas fa-angle-right"></i>고객 지원 </a>'),
    ('<i class="fas fa-angle-right"></i>Clients </a>', '<i class="fas fa-angle-right"></i>고객 사례 </a>'),
    ('<i class="fas fa-angle-right"></i>Contacts</a>', '<i class="fas fa-angle-right"></i>연락처</a>'),
    ('<i class="fas fa-angle-right"></i>Company</a>', '<i class="fas fa-angle-right"></i>회사</a>'),
    ('<i class="fas fa-angle-right"></i>Leadership</a>', '<i class="fas fa-angle-right"></i>리더십</a>'),
    ('<i class="fas fa-angle-right"></i>Diversity</a>', '<i class="fas fa-angle-right"></i>다양성</a>'),
    ('<i class="fas fa-angle-right"></i>Jobs</a>', '<i class="fas fa-angle-right"></i>채용</a>'),
    # Breadcrumb / common
    ('<a href="index.html">Home</a>', '<a href="index.html">홈</a>'),
    ('<h2 class="mt-n1">Contact with Us</h2>', '<h2 class="mt-n1">문의하기</h2>'),
    ('<h1 class="page-title">Contact with Us</h1>', '<h1 class="page-title">문의하기</h1>'),
    ('<li class="breadcrumb-item active" aria-current="page">Contact</li>',
     '<li class="breadcrumb-item active" aria-current="page">문의</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">FAQ</li>',
     '<li class="breadcrumb-item active" aria-current="page">자주 묻는 질문</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Log In</li>',
     '<li class="breadcrumb-item active" aria-current="page">로그인</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Sign In</li>',
     '<li class="breadcrumb-item active" aria-current="page">회원가입</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">About us</li>',
     '<li class="breadcrumb-item active" aria-current="page">회사 소개</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Blog</li>',
     '<li class="breadcrumb-item active" aria-current="page">블로그</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Team</li>',
     '<li class="breadcrumb-item active" aria-current="page">팀</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Team Details</li>',
     '<li class="breadcrumb-item active" aria-current="page">팀 상세</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Service</li>',
     '<li class="breadcrumb-item active" aria-current="page">서비스</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Service Details</li>',
     '<li class="breadcrumb-item active" aria-current="page">서비스 상세</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Blog Details</li>',
     '<li class="breadcrumb-item active" aria-current="page">블로그 상세</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Blog Details with Left Sidebar</li>',
     '<li class="breadcrumb-item active" aria-current="page">블로그 상세(좌측 사이드바)</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Blog with Sidebar</li>',
     '<li class="breadcrumb-item active" aria-current="page">블로그(사이드바)</li>'),
    ('<li class="breadcrumb-item active" aria-current="page">Blog with Left Sidebar</li>',
     '<li class="breadcrumb-item active" aria-current="page">블로그(좌측 사이드바)</li>'),
    ('<a href="blog.html">Blog</a>', '<a href="blog.html">블로그</a>'),
    ('<a href="team.html">Team</a>', '<a href="team.html">팀</a>'),
    ('<a href="service.html">Service</a>', '<a href="service.html">서비스</a>'),
    # Login / signup forms (h1 Welcome Back handled per file in SPECIAL)
    ('<label class="form-label">Username</label>', '<label class="form-label">아이디</label>'),
    ('<label class="form-label">Password</label>', '<label class="form-label">비밀번호</label>'),
    ('<label class="form-label">Email</label>', '<label class="form-label">이메일</label>'),
    ('placeholder="Password"', 'placeholder="비밀번호"'),
    ('placeholder="Name"', 'placeholder="이름"'),
    ('<button type="submit" class="btn btn-base w-100">Login</button>',
     '<button type="submit" class="btn btn-base w-100">로그인</button>'),
    ('<button type="submit" class="btn btn-base w-100">Sign Up</button>',
     '<button type="submit" class="btn btn-base w-100">회원가입</button>'),
    ('<p>Allready have an account?<a href="log-in.html">Login Now</a></p>',
     '<p>이미 계정이 있으신가요? <a href="log-in.html">로그인</a></p>'),
    ('<p>New user?<a href="sign-up.html">Don\'t have an account?</a></p>',
     '<p>아직 계정이 없으신가요? <a href="sign-up.html">회원가입</a></p>'),
    ('<a class="reset-pass" href="#">Forgot your password?</a>',
     '<a class="reset-pass" href="#">비밀번호를 잊으셨나요?</a>'),
    ('<label class="form-check-label" for="exampleCheck1">Remember me</label>',
     '<label class="form-check-label" for="exampleCheck1">로그인 상태 유지</label>'),
    # Pricing / CTAs (index & variants)
    ('<label class="toggler toggler--is-active ms-0" id="filt-monthly">Monthly</label>',
     '<label class="toggler toggler--is-active ms-0" id="filt-monthly">월간</label>'),
    ('<label class="toggler" id="filt-hourly">Annualy</label>',
     '<label class="toggler" id="filt-hourly">연간</label>'),
    ('<span class="tags">(Save 30%)</span>', '<span class="tags">(30% 절약)</span>'),
    ('<span>Select Currency</span>', '<span>통화 선택</span>'),
    ('<h4 class="pricing-title">Free</h4>', '<h4 class="pricing-title">무료</h4>'),
    ('<h4 class="pricing-title">BASIC</h4>', '<h4 class="pricing-title">베이직</h4>'),
    ('<h4 class="pricing-title">ADVANCED</h4>', '<h4 class="pricing-title">어드밴스드</h4>'),
    ('<span class="category">/monthly</span>', '<span class="category">/월</span>'),
    ('<span class="category">/annualy</span>', '<span class="category">/년</span>'),
    ('<a class="btn btn-border" href="index.html">Start Now</a>', '<a class="btn btn-border" href="index.html">시작하기</a>'),
    ('<a class="btn btn-base" href="index.html">Start Now</a>', '<a class="btn btn-base" href="index.html">시작하기</a>'),
    ('<button class="btn btn-base">Sign Up</button>', '<button class="btn btn-base">구독하기</button>'),
    ('<h4><a href="service-details.html">Sign Up to Ride</a></h4>',
     '<h4><a href="service-details.html">서비스 알아보기</a></h4>'),
    ('<h4><a href="service.html">Sign Up to Ride</a></h4>',
     '<h4><a href="service.html">서비스 알아보기</a></h4>'),
    ('<a class="read-more-btn" href="#">Read More</a>', '<a class="read-more-btn" href="#">더 보기</a>'),
    ('placeholder="Enter Your Domain Name"', 'placeholder="도메인을 입력하세요"'),
    ('<button class="nav-link active" id="pills-home-tab" data-bs-toggle="pill" data-bs-target="#pills-home" type="button" role="tab" aria-controls="pills-home" aria-selected="true">Monthly</button>',
     '<button class="nav-link active" id="pills-home-tab" data-bs-toggle="pill" data-bs-target="#pills-home" type="button" role="tab" aria-controls="pills-home" aria-selected="true">월간</button>'),
    ('<h4 class="sub-title">About us</h4>', '<h4 class="sub-title">회사 소개</h4>'),
    ('<h5><a href="#">Monthly Progress</a></h5>', '<h5><a href="#">월간 진행 현황</a></h5>'),
    # Standard Lorem blocks → Korean placeholder
    (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quis ipsum suspendisse ultrices gravida. Risus commodo viverra maecenas accumsan lacus vel facilisisy.",
        "산업안전 규정·점검·실무를 한곳에서 정리하는 TAI 플랫폼 안내입니다. 상세 내용은 각 서비스 페이지에서 확인하세요.",
    ),
    (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quis ipsum suspendisse ultrices gravida. Risus commodo viverra maecenas accumsan lacus vel facilisis.",
        "산업안전 규정·점검·실무를 한곳에서 정리하는 TAI 플랫폼 안내입니다. 상세 내용은 각 서비스 페이지에서 확인하세요.",
    ),
    (
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, empor incididunt ut labore et dolore magna aliqua.",
        "산업안전 관련 안내와 최신 정보를 제공합니다.",
    ),
    (
        '<p class="px-md-5">Lorem ipsum dolor sit amet, consectetur adipiscing elit, empor incididunt ut labore et dolore magna aliqua.</p>',
        '<p class="px-md-5">산업안전 관련 안내와 최신 정보를 제공합니다.</p>',
    ),
    (
        '<p class="px-5">Lorem ipsum dolor sit amet, consectetur adipiscing elit, empor incididunt ut labore et dolore magna aliqua.</p>',
        '<p class="px-5">산업안전 관련 안내와 최신 정보를 제공합니다.</p>',
    ),
    # Pricing bullets
    ("<li>User Interface Design</li>", "<li>사용자 인터페이스 설계</li>"),
    ("<li>Web developmet</li>", "<li>웹 개발</li>"),
    ("<li> Support Tools</li>", "<li>지원 도구</li>"),
    ("<li> Products management</li>", "<li>제품 관리</li>"),
    ("<li>Support Tools</li>", "<li>지원 도구</li>"),
    ("<li>Products management</li>", "<li>제품 관리</li>"),
    # Index / landing sections
    ('<h4 class="sub-title">SERVICES</h4>', '<h4 class="sub-title">서비스</h4>'),
    (
        '<h2 class="title">Use your android or ios device to manage everything.</h2>',
        '<h2 class="title">안드로이드·iOS에서 산업안전 업무를 한곳에서 관리하세요.</h2>',
    ),
    ('<img src="assets/img/featured/1i.png" alt="">App Development', '<img src="assets/img/featured/1i.png" alt="">앱·업무 화면'),
    ('<img src="assets/img/featured/2i.png" alt="">User Interface Design', '<img src="assets/img/featured/2i.png" alt="">사용자 화면 설계'),
    ('<img src="assets/img/featured/3i.png" alt="">Cloud Storage', '<img src="assets/img/featured/3i.png" alt="">클라우드 저장'),
    ('<img src="assets/img/featured/4i.png" alt="">Customer Support', '<img src="assets/img/featured/4i.png" alt="">고객 지원'),
    (
        '<h2 class="title">Super fast project management system</h2>',
        '<h2 class="title">빠르게 이어지는 안전관리 절차</h2>',
    ),
    (
        '<p>Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quis ipsum suspendisse ultrices gravida. Risus commodo viverra maecenas accumsan lacus vel facilisis. </p>',
        '<p>선임·점검·이력까지 단계별로 정리해, 현장과 경영진이 같은 정보를 공유합니다.</p>',
    ),
    ('<li><i class="far fa-check-circle"></i>Easy Installation Guide</li>',
     '<li><i class="far fa-check-circle"></i>도입·설치 가이드 제공</li>'),
    ('<li><i class="far fa-check-circle"></i>Easy setup process with Nexas</li>',
     '<li><i class="far fa-check-circle"></i>TAI 기준 초기 설정 지원</li>'),
    ('<li><i class="far fa-check-circle"></i>24/7 Live call support</li>',
     '<li><i class="far fa-check-circle"></i>긴급 문의 대응(연락처 안내)</li>'),
    ('<a class="btn btn-border" href="about.html">View More</a>', '<a class="btn btn-border" href="about.html">더 알아보기</a>'),
    ('<h4 class="sub-title">PRICING PLAN</h4>', '<h4 class="sub-title">요금 안내</h4>'),
    (
        '<h2 class="title">No Hidden Charges! Choose Plan.</h2>',
        '<h2 class="title">숨은 비용 없이, 플랜을 선택하세요.</h2>',
    ),
    (
        '<h2 class="title text-white">Join 63,000+ people connect with us</h2>',
        '<h2 class="title text-white">많은 기업이 TAI와 함께 산업안전을 관리합니다</h2>',
    ),
    ('<p class="text-white">Try our products free for 30 days</p>', '<p class="text-white">제품 체험 및 상담을 요청해 보세요</p>'),
    ('<i class="fab fa-google-play"></i>Google-play</a>', '<i class="fab fa-google-play"></i>Google Play</a>'),
    ('<i class="fab fa-google-play"></i>App-Store</a>', '<i class="fab fa-apple"></i>App Store</a>'),
    ('alt="app"', 'alt="앱 화면"'),
    (
        '<h2 class="title">What’s clients say about us</h2>',
        '<h2 class="title">고객 후기</h2>',
    ),
    (
        '<h2>Subscribe For Newsletter</h2>',
        '<h2>뉴스레터 구독</h2>',
    ),
    (
        '<input type="text" class="form-control" placeholder="Enter Your Email" aria-label="Recipient\'s username" aria-describedby="button-addon2">',
        '<input type="text" class="form-control" placeholder="이메일을 입력하세요" aria-label="이메일" aria-describedby="button-addon2">',
    ),
    ('<button class="btn btn-base" type="button" id="button-addon2">Get Started</button>',
     '<button class="btn btn-base" type="button" id="button-addon2">시작하기</button>'),
    (
        '<a class="play-btn pulse" href="https://www.youtube.com/embed/Wimkqo8gDZ0" data-effect="mfp-zoom-in"><span class="play-icon"><i class="fas fa-play"></i></span>Watch Video</a>',
        '<a class="play-btn pulse" href="https://www.youtube.com/embed/Wimkqo8gDZ0" data-effect="mfp-zoom-in"><span class="play-icon"><i class="fas fa-play"></i></span>소개 영상</a>',
    ),
    # Pages: team, about, blog, contact
    (
        '<h1 class="page-title">The Experts Nexas Team Members.</h1>',
        '<h1 class="page-title">TAI 전문 팀</h1>',
    ),
    ('<h1 class="page-title">About us</h1>', '<h1 class="page-title">회사 소개</h1>'),
    ('<h1 class="page-title">Nexas Blog Details</h1>', '<h1 class="page-title">블로그 상세</h1>'),
    (
        '<button type="submit" class="btn btn-base w-100">Submit your project</button>',
        '<button type="submit" class="btn btn-base w-100">문의 보내기</button>',
    ),
    (
        '<button type="submit" class="btn btn-base">Submit your Message</button>',
        '<button type="submit" class="btn btn-base">댓글 등록</button>',
    ),
    ('placeholder="Search Here"', 'placeholder="검색어를 입력하세요"'),
    ('<a class="page-link" href="#">Next</a>', '<a class="page-link" href="#">다음</a>'),
    ('<h5>03 Comments</h5>', '<h5>댓글 3건</h5>'),
    ('<h5>Comments</h5>', '<h5>댓글 작성</h5>'),
    ('<h4 class="sub-title">Team Members</h4>', '<h4 class="sub-title">팀 구성원</h4>'),
    (
        '<h2 class="title">The Experts Nexas Team Members.</h2>',
        '<h2 class="title">TAI 전문 팀을 소개합니다.</h2>',
    ),
    (
        "<p>There are many variations of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>Softwere landing are many variations of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>Variations of passages of technology available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>There are many business landing of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>There are many variations of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>There are many business landing of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>There are many variations of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>There are many business landing of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    (
        "<p>There are many variations of passages of available in some form, by injected humour</p>",
        "<p>산업안전과 관련된 다양한 주제를 다룹니다.</p>",
    ),
    # Footer contact (template)
    ("<h6>(+1) 123-4567-8910 </h6>", "<h6>02-0000-0000</h6>"),
    (
        "<p>New York, NY 256364, United States contact@example.com</p>",
        "<p>서울특별시 ㅣ contact@taieng.co.kr</p>",
    ),
    # Curly apostrophe heading (if any file left)
    ("What’s clients say about us", "고객 후기"),
    # Long testimonial / filler (appears in many pages)
    (
        "<p>Contrary to popular belief, This is not simply random text. It has roots in a piece of Latin from 45 BC, making it over 2000 years old. Richard McClintock, a professor at in Virginia, looked up one of the more obscure words. </p>",
        "<p>도입 후 점검·기록·보고가 한 화면에 모여, 현장과 본사가 같은 기준으로 소통하게 되었습니다.</p>",
    ),
    (
        "<p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas excepturi sint occaecati cupiditate non provident, qui officia deserunt mollitia animi. </p>",
        "<p>법정 점검 주기와 증빙 자료를 놓치지 않게 되어, 감사·인증 대응 부담이 줄었습니다.</p>",
    ),
    (
        "<p>This is not simply random text. It has roots in a piece of Latin from 45 BC, making it over 2000 years old. Richard McClintock, a professor at -SyHampdendney College in Virginia, looked up one of the more obscure Latin words. </p>",
        "<p>대행사·수급사와 일정·이력을 공유하니 협업이 훨씬 수월해졌습니다.</p>",
    ),
    (
        "<p>This is not simply random text. It has roots in a piece of Latin from 45 BC, making it over 2000 years old. Richard McClintock, a professor at -SyHampdendney College in Virginia, looked up one of the more obscure Latin words.  </p>",
        "<p>대행사·수급사와 일정·이력을 공유하니 협업이 훨씬 수월해졌습니다.</p>",
    ),
    (
        "<p>Tempor ibus autem quibusdam et aut officiis debitis aut rerum necessitatibus saepe eveniet ut et voluptates repudiandae sint et molestiae non. Thic tenetur a sapiente delectus, ut aut reiciendis voluptatibus maiores alias consequatur. </p>",
        "<p>리스크 요인을 사전에 정리해 두니, 교육·개선 활동에 집중할 수 있습니다.</p>",
    ),
    (
        "<p>At vero eos et accusamus et iusto odio dignissimos ducimus qui blanditiis praesentium voluptatum deleniti atque corrupti quos dolores et quas excepturi sint non provident, similique sunt in culpa qui officia deserunt mollitia animi. </p>",
        "<p>현장 피드백을 데이터로 남겨, 반복 재발을 줄이는 데 도움이 됩니다.</p>",
    ),
    (
        "In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be pain. But in certain circumstances and owing accepted. </p>",
        "선임·점검·보고를 한 화면에서 정리해, 현장 의사결정이 빨라집니다. </p>",
    ),
    (
        "In a free hour, when our power of choice is untrammelled and when nothing prevents our being able to do what we like best, every pleasure is to be pain. But in certain circumstances and owing accepted.</p>",
        "선임·점검·보고를 한 화면에서 정리해, 현장 의사결정이 빨라집니다.</p>",
    ),
    ("<h4><a href=\"service-details.html\">Download Nexas app</a></h4>", "<h4><a href=\"service-details.html\">TAI 앱 다운로드</a></h4>"),
    ("<h4><a href=\"service.html\">Download Nexas app</a></h4>", "<h4><a href=\"service.html\">TAI 앱 다운로드</a></h4>"),
    ('<button class="btn btn-base">Search</button>', '<button class="btn btn-base">검색</button>'),
    ("<p>Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Quis ipsum suspendisse ultrices.</p>", "<p>법령·점검 주기에 맞춰 업무 흐름을 안내합니다.</p>"),
    ("<h1>The next generation App Landing Page</h1>", "<h1>차세대 산업안전 플랫폼</h1>"),
    ("<h3>Top Client’s from all over world</h3>", "<h3>전국 주요 고객사</h3>"),
    ("<h2 class=\"title\">Behind the story of Nexas Agency.</h2>", "<h2 class=\"title\">TAI 이야기</h2>"),
    ("<h2 class=\"title\">We are here to help you with</h2>", "<h2 class=\"title\">함께 해결해 드립니다</h2>"),
    ("<h2 class=\"title\">Nexas Anywhere Access </h2>", "<h2 class=\"title\">어디서나 접속하는 TAI</h2>"),
    ("<h1>Manage all your finances easily with Nexas.</h1>", "<h1>TAI로 산업안전 업무를 쉽게 관리하세요.</h1>"),
    ("<h4>Here is what you can expect Nexas.</h4>", "<h4>TAI에서 기대할 수 있는 것</h4>"),
    ("<h4>Easily growth your Business..</h4>", "<h4>비즈니스 성장을 함께합니다</h4>"),
    ('<a class="btn btn-base" href="faq.html">Chat with a Live Person</a>', '<a class="btn btn-base" href="faq.html">상담 요청</a>'),
    ('<h2 class="title">Need help? We\'re always here for you.</h2>', '<h2 class="title">도움이 필요하신가요? 언제든 연락 주세요.</h2>'),
    ('<i class="fas fa-angle-right"></i>Nexas</a>', '<i class="fas fa-angle-right"></i>TAI</a>'),
]

SPECIAL_H1 = {
    "log-in.html": ('<h1 class="page-title">Welcome Back</h1>', '<h1 class="page-title">로그인</h1>'),
    "sign-up.html": ('<h1 class="page-title">Welcome Back</h1>', '<h1 class="page-title">회원가입</h1>'),
}

TITLES = {
    "index.html": "TAI Engineering | 산업안전 AI 플랫폼",
    "index-1.html": "TAI SAFE | TAI Engineering",
    "index-2.html": "TAI MANAGER | TAI Engineering",
    "index-3.html": "TAI FIX | TAI Engineering",
    "index-4.html": "TAI CARE | TAI Engineering",
    "index-5.html": "안전정보 | TAI Engineering",
    "index-6.html": "TAI Engineering",
    "about.html": "회사 소개 | TAI Engineering",
    "contact.html": "문의하기 | TAI Engineering",
    "faq.html": "자주 묻는 질문 | TAI Engineering",
    "log-in.html": "로그인 | TAI Engineering",
    "sign-up.html": "회원가입 | TAI Engineering",
    "mypage.html": "마이페이지 | TAI Engineering",
    "service.html": "서비스 | TAI Engineering",
    "service-details.html": "서비스 상세 | TAI Engineering",
    "blog.html": "블로그 | TAI Engineering",
    "blog-2.html": "블로그 | TAI Engineering",
    "blog-3.html": "블로그 | TAI Engineering",
    "blog-single.html": "블로그 상세 | TAI Engineering",
    "blog-single-2.html": "블로그 상세 | TAI Engineering",
    "blog-single-3.html": "블로그 상세 | TAI Engineering",
    "team.html": "팀 | TAI Engineering",
    "team-details.html": "팀 상세 | TAI Engineering",
}


def main() -> None:
    for path in sorted(ROOT.glob("*.html")):
        if path.name in SKIP:
            continue
        text = path.read_text(encoding="utf-8")
        orig = text
        for a, b in REPLACEMENTS:
            text = text.replace(a, b)
        if path.name in TITLES:
            text = re.sub(
                r"<title>.*?</title>",
                f"<title>{TITLES[path.name]}</title>",
                text,
                count=1,
                flags=re.DOTALL,
            )
        if text != orig:
            path.write_text(text, encoding="utf-8")
            print("updated", path.name)

    for fname, (a, b) in SPECIAL_H1.items():
        p = ROOT / fname
        if not p.exists():
            continue
        t = p.read_text(encoding="utf-8")
        if a in t:
            p.write_text(t.replace(a, b, 1), encoding="utf-8")
            print("special h1", fname)


if __name__ == "__main__":
    main()
