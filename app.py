# -*- coding: utf-8 -*-
import streamlit as st
import json
import os
import hashlib
import base64
import time
from io import BytesIO
from datetime import datetime
from PIL import Image
from supabase import create_client, Client


# ==========================================
# [TPM 파트 CA 기술부] 이미지 및 유틸리티 함수
# ==========================================
def get_local_car_base64_html(image_path="supercar.jpg", target_height=60):
    if not os.path.exists(image_path): return "🚘"
    try:
        img = Image.open(image_path)
        aspect_ratio = img.width / img.height
        target_width = int(target_height * aspect_ratio)
        img_resized = img.resize((target_width, target_height))
        buffered = BytesIO()
        img_resized.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f'<img src="data:image/png;base64,{img_str}" style="height: {target_height}px; vertical-align: middle; margin-right: 15px; border-radius: 4px;">'
    except: return "🚘"

def get_local_place_base64_html(image_path="jeju.jpeg", target_height=60):
    if not os.path.exists(image_path): return "🚘"
    try:
        img = Image.open(image_path)
        aspect_ratio = img.width / img.height
        target_width = int(target_height * aspect_ratio)
        img_resized = img.resize((target_width, target_height))
        buffered = BytesIO()
        img_resized.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f'<img src="data:image/png;base64,{img_str}" style="height: {target_height}px; vertical-align: middle; margin-right: 15px; border-radius: 4px;">'
    except: return "🚘"

def get_car_icon_html(car_name, target_height=40):
    name_lower = car_name.lower()
    known_cars = {
        "테슬라": "https://cdn-icons-png.flaticon.com/512/3261/3261549.png",
        "tesla": "https://cdn-icons-png.flaticon.com/512/3261/3261549.png",
        "제네시스": "https://cdn-icons-png.flaticon.com/512/3067/3067160.png",
        "genesis": "https://cdn-icons-png.flaticon.com/512/3067/3067160.png",
        "소나타": "https://cdn-icons-png.flaticon.com/512/3202/3202926.png",
        "아반떼": "https://cdn-icons-png.flaticon.com/512/3202/3202926.png",
        "그랜저": "https://cdn-icons-png.flaticon.com/512/3067/3067160.png",
        "벤츠": "https://cdn-icons-png.flaticon.com/512/3067/3067198.png",
        "benz": "https://cdn-icons-png.flaticon.com/512/3067/3067198.png",
        "비엠": "https://cdn-icons-png.flaticon.com/512/741/741460.png",
        "bmw": "https://cdn-icons-png.flaticon.com/512/741/741460.png",
        "아우디": "https://cdn-icons-png.flaticon.com/512/741/741408.png",
        "audi": "https://cdn-icons-png.flaticon.com/512/741/741408.png",
        "포르쉐": "https://cdn-icons-png.flaticon.com/512/3067/3067216.png",
        "porsche": "https://cdn-icons-png.flaticon.com/512/3067/3067216.png",
        "카니발": "https://cdn-icons-png.flaticon.com/512/3202/3202888.png",
        "suv": "https://cdn-icons-png.flaticon.com/512/3202/3202888.png",
        "모닝": "https://cdn-icons-png.flaticon.com/512/3202/3202869.png",
        "레이": "https://cdn-icons-png.flaticon.com/512/3202/3202869.png",
        "키트": "https://cdn-icons-png.flaticon.com/512/3199/3199920.png",
        "kitt": "https://cdn-icons-png.flaticon.com/512/3199/3199920.png",
    }
    image_url = ""
    for key, url in known_cars.items():
        if key in name_lower:
            image_url = url
            break
    if not image_url:
        random_icons = [
            "https://cdn-icons-png.flaticon.com/512/3202/3202926.png",
            "https://cdn-icons-png.flaticon.com/512/2554/2554936.png",
            "https://cdn-icons-png.flaticon.com/512/741/741407.png",
            "https://cdn-icons-png.flaticon.com/512/3067/3067222.png",
            "https://cdn-icons-png.flaticon.com/512/171/171239.png",
            "https://cdn-icons-png.flaticon.com/512/575/575775.png",
            "https://cdn-icons-png.flaticon.com/512/2312/2312959.png",
            "https://cdn-icons-png.flaticon.com/512/1553/1553980.png"
        ]
        hash_val = int(hashlib.md5(car_name.encode('utf-8')).hexdigest(), 16)
        image_url = random_icons[hash_val % len(random_icons)]
    return f'<img src="{image_url}" style="height: {target_height}px; vertical-align: middle; margin-right: 10px; border-radius: 4px;">'

# ==========================================
# [왕실 서고] 데이터 관리 함수 (Supabase 연동)
# ==========================================
@st.cache_resource
def init_connection():
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_KEY"]
    return create_client(url, key)

supabase = init_connection()

def load_data():
    try:
        response = supabase.table("carpool_db").select("data").eq("id", 1).execute()
        if response.data:
            return response.data[0]['data']
        return {"cars": [], "passengers": []}
    except Exception as e:
        st.error(f"장부 로드 중 오류가 발생하였사옵니다: {e}")
        return {"cars": [], "passengers": []}

def save_data(data):
    try:
        supabase.table("carpool_db").update({"data": data}).eq("id", 1).execute()
    except Exception as e:
        st.error(f"장부 기록 중 오류가 발생하였사옵니다: {e}")

# 페이지 설정
st.set_page_config(page_title="TPM 파트 카풀", page_icon="🚘", type="primary", use_container_width=True)

# 데이터 로드 및 세션 상태 초기화
db = load_data()
if 'selected_role' not in st.session_state:
    st.session_state.selected_role = None
if 'last_notice_id' not in st.session_state:
    st.session_state.last_notice_id = ""
if 'party_confirmed' not in st.session_state:
    st.session_state.party_confirmed = False

# ==========================================
# [타이틀 영역 및 대시보드 진입 버튼]
# ==========================================
main_car_icon_html = get_local_car_base64_html("supercar.jpg", target_height=60)
sub_place_icon_html = get_local_place_base64_html("jeju.jpeg", target_height=50)

col_t1, col_t2 = st.columns([4, 1])
with col_t1:
    st.markdown(f"## {main_car_icon_html} TPM 파트 카풀", unsafe_allow_html=True)
with col_t2:
    st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
    # 누구나 볼 수 있는 대시보드 버튼 배치
    if st.button("📊 현황 대시보드", type="primary", use_container_width=True):
        st.session_state.selected_role = "admin"
        st.session_state.party_confirmed = True
        st.rerun()

st.markdown("---")

# ==========================================
# [사이드바]
# ==========================================
st.sidebar.header("1. 신원 확인")
user_name = st.sidebar.text_input("성함을 입력하세요", placeholder="예: 마이클 나이트")

st.sidebar.markdown("---")
st.sidebar.header("2. 역할 선택")
col1, col2 = st.sidebar.columns(2)
if col1.button("🚘 운전자", use_container_width=True):
    st.session_state.selected_role = "driver"
    st.session_state.party_confirmed = True

if col2.button("🏃 탑승자", use_container_width=True):
    st.session_state.selected_role = "passenger"
    st.session_state.party_confirmed = False

# 역할별 추가 입력
my_party_size = 1 

if st.session_state.selected_role == "driver":
    st.sidebar.success("✅ [운전자] 모드로 접속 중")
elif st.session_state.selected_role == "passenger":
    st.sidebar.markdown("---")
    st.sidebar.subheader("🏃 동승자 설정")
    companion_count = st.sidebar.number_input("동승 인원 (본인 제외)", min_value=0, max_value=5, value=0)
    my_party_size = companion_count + 1
    
    st.sidebar.info(f"총 인원: **{my_party_size}명**")
    
    if not st.session_state.party_confirmed:
        if st.sidebar.button("✅ 입장하기 (OK)", type="primary", use_container_width=True):
            st.session_state.party_confirmed = True
            st.rerun()
    else:
        st.sidebar.success(f"✅ 입장 완료 (총 {my_party_size}명)")
        if st.sidebar.button("🔄 인원 재설정"):
            st.session_state.party_confirmed = False
            st.rerun()
elif st.session_state.selected_role == "admin":
    st.sidebar.success("📊 [대시보드] 모드로 열람 중")

try:
    db_password = st.secrets["db_password"]
except KeyError:
    db_password = "1325"
st.sidebar.markdown("---")
with st.sidebar.expander("👑 관리자 메뉴"):
    # 암구호 통과 시 데이터 초기화만 노출
    if st.text_input("암구호", type="password") == db_password:
        if st.button("🚨 데이터 초기화", type="primary", use_container_width=True):
            db = {"cars": [], "passengers": []}
            save_data(db)
            st.rerun()

# ==========================================
# [메인 로직]
# ==========================================
if not user_name and st.session_state.selected_role != "admin":
    st.info("👈 왼쪽 사이드바에서 **성함**을 먼저 입력해 주세요.")
elif not st.session_state.selected_role:
    st.info(f"환영합니다, **{user_name}** 님! 👈 왼쪽 사이드바에서 **역할** 버튼을 눌러 주세요")
else:
    if st.session_state.selected_role == "passenger" and not st.session_state.party_confirmed:
        st.warning("👈 왼쪽 사이드바에서 동승 인원을 확인하신 후, **[✅ 입장하기 (OK)]** 버튼을 눌러주시옵소서.")
        st.stop()

    role = st.session_state.selected_role
    if role != "admin":
        st.write(f"#### 어서오세요, **{user_name}** ({'운전자' if role == 'driver' else '탑승자'}) 님.")
    
    # --------------------------------------
    # A. 운전자 (Driver) 로직
    # --------------------------------------
    if role == "driver":
        my_car = next((car for car in db['cars'] if car['driver'] == user_name), None)

        if my_car:
            car_icon = get_car_icon_html(my_car['car_name'])
            is_locked = my_car.get('locked', False)
            lock_status_icon = "🔒" if is_locked else "🔓"
            
            dept_loc = my_car.get('dept_loc', '미정')
            dest_loc = my_car.get('dest_loc', '미정')
            dept_time = my_car.get('dept_time', '미정')
            
            st.markdown(f"### {car_icon} **[{my_car['car_name']}]** {lock_status_icon}", unsafe_allow_html=True)
            st.info(f"📍 **여정:** {dept_loc} ➡️ {dest_loc}  |  ⏰ **출발 시간:** {dept_time}")

            current_occupancy = sum(r['size'] for r in my_car['riders'])
            capacity = my_car['capacity']
            with st.container(border=True):
                with st.expander("📝 출발 정보 수정하기"):
                    new_loc = st.text_input("출발 위치 변경", value=dept_loc)
                    new_dest = st.text_input("목적지 변경", value=dest_loc)
                    new_time = st.text_input("출발 시간 변경", value=dept_time)
                    if st.button("정보 수정 완료"):
                        my_car['dept_loc'] = new_loc
                        my_car['dest_loc'] = new_dest
                        my_car['dept_time'] = new_time
                        
                        if my_car['riders']:
                            timestamp = datetime.now().strftime('%H:%M:%S')
                            auto_msg = f"📢 출발 정보가 변경되었습니다. (위치: {new_loc} ➡️ {new_dest}, 시간: {new_time})"
                            my_car['notice'] = f"[{timestamp}] {auto_msg}"
                            my_car['notice_id'] = f"{user_name}_AUTO_{datetime.now().timestamp()}"
                            my_car['confirmed_riders'] = [] 
                            st.toast("탑승객들에게 정보 변경 사항이 자동으로 공지됩니다!", icon="🔔")

                        save_data(db)
                        st.success("정보가 수정되었습니다.")
                        st.rerun()

                c1, c2, c3 = st.columns([2, 1, 1])
                riders_display = [f"{r['name']}({r['size']}인)" for r in my_car['riders']]
                riders_str = ", ".join(riders_display) if riders_display else "없음"
                
                c1.markdown(f"**현재 탑승객:** :blue[{riders_str}]")
                c1.progress(current_occupancy / capacity if capacity > 0 else 0, text=f"좌석 점유율 ({current_occupancy}/{capacity})")
                
                if is_locked:
                    if c2.button("🔓 문 열기"):
                        my_car['locked'] = False
                        save_data(db)
                        st.rerun()
                else:
                    if c2.button("🔒 문 잠그기", type="primary"):
                        my_car['locked'] = True
                        save_data(db)
                        st.rerun()

                if c3.button("🗑️ 등록 취소"):
                    if my_car['riders']:
                        for rider in my_car['riders']:
                            db['passengers'].append({
                                "name": rider['name'],
                                "time": "기존 차량 취소됨",
                                "size": rider['size']
                            })
                        st.toast("탑승객들을 대기 명단으로 이동시켰습니다.", icon="ℹ️")
                        
                    db['cars'] = [c for c in db['cars'] if c['driver'] != user_name]
                    save_data(db)
                    st.warning("차량 등록을 취소하였습니다.")
                    st.rerun()

            if my_car['riders']:
                st.write("#### 📡 탑승객 수신 확인 현황")
                confirmed_list = my_car.get('confirmed_riders', [])
                status_cols = st.columns(len(my_car['riders'])) if len(my_car['riders']) > 0 else [st.container()]
                for idx, rider in enumerate(my_car['riders']):
                    r_name = rider['name']
                    r_size = rider['size']
                    is_read = r_name in confirmed_list
                    icon = "✅" if is_read else "❌"
                    color = "green" if is_read else "red"
                    with status_cols[idx]:
                        st.markdown(f"**{r_name}({r_size})**")
                        st.markdown(f":{color}[{icon} {'확인' if is_read else '미확인'}]")

                with st.expander("📣 탑승객 안내방송", expanded=True):
                    notice_msg = st.text_input("메시지 입력", placeholder="예: 10분뒤 R5 2층에서 모여서 출발!")
                    if st.button("전송"):
                        for c in db['cars']:
                            if c['driver'] == user_name:
                                timestamp = datetime.now().strftime('%H:%M:%S')
                                c['notice'] = f"[{timestamp}] {notice_msg}"
                                c['notice_id'] = f"{user_name}_{datetime.now().timestamp()}"
                                c['confirmed_riders'] = [] 
                        save_data(db)
                        st.toast("공지 전송 완료!", icon="📣")
                        st.rerun()

            st.write("#### 🚶 대기 중인 사람 태우기")
            if is_locked:
                st.warning("🔒 차량이 잠겨 있어 탑승객을 태울 수 없습니다.")
            elif db['passengers']:
                for p in db['passengers']:
                    with st.container(border=True):
                        pc1, pc2 = st.columns([4, 1])
                        p_size = p.get('size', 1)
                        dept_time = p.get('time', '항시가능')
                        pc1.write(f"**{p['name']}** ({p_size}명) :blue[({dept_time})]")
                        if current_occupancy + p_size <= capacity:
                            if pc2.button("태우기", key=f"pickup_{p['name']}"):
                                my_car['riders'].append({"name": p['name'], "size": p_size})
                                db['passengers'] = [x for x in db['passengers'] if x['name'] != p['name']]
                                save_data(db)
                                st.rerun()
                        else:
                            pc2.error(f"좌석부족({p_size})")
            else:
                st.info("대기 중인 사람이 없습니다.")

            st.markdown("---")
            st.write("#### 📡 동료 운전자 현황 (탑승자 명단)")
            other_cars = [c for c in db['cars'] if c['driver'] != user_name]
            if other_cars:
                for car in other_cars:
                    oc1, oc2, oc3 = st.columns([2, 2, 1])
                    oc1.markdown(f"**{get_car_icon_html(car['car_name'])} {car['car_name']}**", unsafe_allow_html=True)
                    oc1.caption(f"운전자: {car['driver']}")
                    r_list = [f"{r['name']}({r['size']})" for r in car['riders']]
                    riders_str = ", ".join(r_list) if r_list else "없음"
                    oc2.markdown(f"👥 **탑승자:** :blue[{riders_str}]")
                    d_loc = car.get('dept_loc', '미정')
                    dest_loc = car.get('dest_loc', '미정')
                    d_time = car.get('dept_time', '미정')
                    oc2.caption(f"📍{d_loc} ➡️ {dest_loc} | ⏰ {d_time}")
                    
                    oc3.button("운전 중", disabled=True, key=f"view_{car['id']}")
            else:
                st.caption("다른 차량이 없습니다.")

        else:
            with st.form("car_register"):
                st.subheader("🚘 차량 등록")
                c_name = st.text_input("차량 닉네임", placeholder="예: 홍길동_4885")
                in_loc = st.text_input("출발 위치", placeholder="예: R5/센트럴파크")
                dest_loc = st.text_input("목적지", placeholder="예: 가보쟝")
                in_time = st.text_input("출발 시간", placeholder="예: 6시 정각")
                capacity = st.number_input("빈 자리", 1, 10, 2)
                if st.form_submit_button("등록하기(OK)", type="primary"):
                    fname = c_name.strip() if c_name.strip() else f"{user_name}_차"
                    db['cars'].append({
                        "driver": user_name, "car_name": fname, "capacity": capacity, 
                        "dept_loc": in_loc, "dest_loc": dest_loc, "dept_time": in_time,
                        "riders": [], "notice": "", "notice_id": "", "confirmed_riders": [], "locked": False,
                        "id": f"{user_name}_{datetime.now().strftime('%M%S')}"
                    })
                    save_data(db)
                    st.rerun()

    # --------------------------------------
    # B. 탑승자 (Passenger) 로직
    # --------------------------------------
    elif role == "passenger":
        is_waiting = any(p['name'] == user_name for p in db['passengers'])
        riding_car = None
        for car in db['cars']:
            if any(r['name'] == user_name for r in car['riders']):
                riding_car = car
                break

        if riding_car:
            riding_icon = get_car_icon_html(riding_car['car_name'])
            is_locked = riding_car.get('locked', False)
            d_loc = riding_car.get('dept_loc', '미정')
            dest_loc = riding_car.get('dest_loc', '미정')
            d_time = riding_car.get('dept_time', '미정')

            st.markdown(f"### {riding_icon} **{riding_car['driver']}** 님의 차에 탑승 중", unsafe_allow_html=True)
            st.info(f"📍 **여정:** {d_loc} ➡️ {dest_loc}  |  ⏰ **출발 시간:** {d_time}")
            
            r_list = [f"{r['name']}({r['size']})" for r in riding_car['riders']]
            st.info(f"**탑승자 :** :blue[{', '.join(r_list)}]")

            if is_locked:
                st.error("🔒 **차량 문이 잠겨 하차가 불가능합니다.**")
            
            current_notice = riding_car.get('notice', '')
            current_notice_id = riding_car.get('notice_id', '')
            confirmed_list = riding_car.get('confirmed_riders', [])

            if current_notice:
                if current_notice_id and current_notice_id != st.session_state.last_notice_id:
                    st.toast(f"🔔 새로운 공지: {current_notice}", icon="🚨")
                    st.session_state.last_notice_id = current_notice_id
                
                is_confirmed = user_name in confirmed_list
                with st.container(border=True):
                    st.markdown(f"### 📣 운전자 공지사항")
                    st.write(current_notice)
                    if not is_confirmed:
                        st.warning("⚠️ 확인 버튼을 눌러주세요!")
                        if st.button("✅ 확인했습니다", type="primary"):
                            riding_car['confirmed_riders'].append(user_name)
                            save_data(db)
                            st.rerun()
                    else:
                        st.success("✅ 확인 완료")
            else:
                st.caption("공지가 없습니다.")

            st.write("")
            if is_locked:
                st.button("⛔ 하차 불가 (문 잠김)", disabled=True)
            else:
                if st.button("🏃 하차하기"):
                    riding_car['riders'] = [r for r in riding_car['riders'] if r['name'] != user_name]
                    if 'confirmed_riders' in riding_car and user_name in riding_car['confirmed_riders']:
                        riding_car['confirmed_riders'].remove(user_name)
                    save_data(db)
                    st.success("하차하였습니다.")
                    st.rerun()

        elif is_waiting:
            st.warning("⏳ 대기 명단에 등록되었습니다.")
            if st.button("대기 취소"):
                db['passengers'] = [p for p in db['passengers'] if p['name'] != user_name]
                save_data(db)
                st.rerun()
        else:
            dept_time_input = st.text_input("출발 가능 시간 (미입력시 [항시 가능] 으로 대기)", placeholder="예: 6시 10분, 지금 당장")

            if st.button("📝 대기 명단 등록"):
                final_time = dept_time_input if dept_time_input else "시간 미정"
                db['passengers'].append({
                    "name": user_name, 
                    "time": final_time,
                    "size": my_party_size
                })
                save_data(db)
                st.rerun()

        st.markdown("---")
        st.write("#### 🚕 탑승 가능 차량 목록")
        if db['cars']:
            for car in db['cars']:
                cur_occ = sum(r['size'] for r in car['riders'])
                cap = car['capacity']
                is_full = cur_occ >= cap
                is_car_locked = car.get('locked', False)
                d_loc = car.get('dept_loc', '미정')
                dest_loc = car.get('dest_loc', '미정')
                d_time = car.get('dept_time', '미정')
                
                with st.container(border=True):
                    c1, c2, c3 = st.columns([2, 2, 1])
                    lock_icon = "🔒" if is_car_locked else ""
                    c1.markdown(f"### {get_car_icon_html(car['car_name'])} {car['car_name']} {lock_icon}", unsafe_allow_html=True)
                    c1.caption(f"운전자: {car['driver']}")
                    c1.write(f"📍 {d_loc} ➡️ {dest_loc} | ⏰ {d_time}")
                    
                    r_list = [f"{r['name']}({r['size']})" for r in car['riders']]
                    riders_str = ", ".join(r_list) if r_list else "없음"
                    c1.markdown(f"**탑승자:** :blue[{riders_str}]")

                    c2.metric("잔여석", f"{cap - cur_occ}", f"전체 {cap}")
                    
                    if riding_car and riding_car['id'] == car['id']:
                        c3.button("탑승 중", disabled=True, key=f"r_{car['id']}")
                    elif is_car_locked:
                        c3.button("⛔ 마감", disabled=True, key=f"l_{car['id']}")
                    else:
                        if cur_occ + my_party_size <= cap:
                            if c3.button(f"탑승 ({my_party_size}명)", key=f"j_{car['id']}", type="primary"):
                                for ec in db['cars']:
                                    ec['riders'] = [r for r in ec['riders'] if r['name'] != user_name]
                                    if 'confirmed_riders' in ec and user_name in ec['confirmed_riders']:
                                        ec['confirmed_riders'].remove(user_name)
                                db['passengers'] = [p for p in db['passengers'] if p['name'] != user_name]
                                car['riders'].append({"name": user_name, "size": my_party_size})
                                save_data(db)
                                st.rerun()
                        elif is_full:
                            c3.button("만석", disabled=True, key=f"f_{car['id']}")
                        else:
                            c3.button(f"좌석부족({my_party_size}명)", disabled=True, key=f"lack_{car['id']}")
        else:
            st.write("운행 중인 차량 없음")

    # --------------------------------------
    # C. 대시보드 (Admin) 로직
    # --------------------------------------
    elif role == "admin":
        st.markdown("### 📊 대시보드")
        
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("등록된 차량", f"{len(db['cars'])} 대")
        col_m2.metric("대기 중인 인원", f"{len(db['passengers'])} 팀")
        total_riders = sum(sum(r['size'] for r in c['riders']) for c in db['cars'])
        col_m3.metric("탑승 완료된 총 인원", f"{total_riders} 명")
        
        st.markdown("---")
        st.write("#### 🚘 운행 차량 상세 내역")
        if db['cars']:
            for car in db['cars']:
                cur_occ = sum(r['size'] for r in car['riders'])
                with st.expander(f"운전자: {car['driver']}의 차량 [{car['car_name']}] (점유 {cur_occ}/{car['capacity']})", expanded=True):
                    st.write(f"- **여정:** {car.get('dept_loc', '미정')} ➡️ {car.get('dest_loc', '미정')}")
                    st.write(f"- **시간:** {car.get('dept_time', '미정')}")
                    r_list = [f"{r['name']}({r['size']}인)" for r in car['riders']]
                    st.write(f"- **탑승객:** {', '.join(r_list) if r_list else '없음'}")
        else:
            st.info("현재 운행 중인 차량이 없음.")
            
        st.write("#### 🚶 대기 명단 상세 내역")
        if db['passengers']:
            p_list = [f"{p['name']}({p.get('size', 1)}인, {p.get('time', '미정')})" for p in db['passengers']]
            st.write(", ".join(p_list))
        else:
            st.info("대기 중인 인원 없음.")

# ==========================================
# [왕실 기술부] 자동 새로고침 (카운트다운)
# ==========================================
st.markdown("---")
st.write("") 
refresh_placeholder = st.empty()

for i in range(5, 0, -1):
    if refresh_placeholder.button(f"🔄 새로고침 ({i}초 후 자동 갱신)", key=f"auto_refresh_{i}", use_container_width=True):
        st.rerun()
    time.sleep(1)

st.rerun()
