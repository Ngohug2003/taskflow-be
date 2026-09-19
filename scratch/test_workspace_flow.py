import httpx
import sys

BASE_URL = "http://localhost:8000/api/v1"

def log(msg, status="INFO"):
    print(f"[{status}] {msg}")

def run_tests():
    client = httpx.Client(timeout=10.0)

    # 1. Tạo 2 users: Owner & Member
    owner_email = "owner_test@taskflow.dev"
    member_email = "member_test@taskflow.dev"
    pwd = "Password123!"

    log("1. Đăng ký & lấy token cho Owner và Member...")
    r = client.post(f"{BASE_URL}/auth/register", json={"email": owner_email, "name": "Owner User", "password": pwd})
    if r.status_code == 201:
        owner_token = r.json()["data"]["access_token"]
    else:
        r_login = client.post(f"{BASE_URL}/auth/login", json={"email": owner_email, "password": pwd})
        assert r_login.status_code == 200, f"Owner login failed: {r_login.text}"
        owner_token = r_login.json()["data"]["access_token"]

    r = client.post(f"{BASE_URL}/auth/register", json={"email": member_email, "name": "Member User", "password": pwd})
    if r.status_code == 201:
        member_token = r.json()["data"]["access_token"]
    else:
        r_login = client.post(f"{BASE_URL}/auth/login", json={"email": member_email, "password": pwd})
        assert r_login.status_code == 200, f"Member login failed: {r_login.text}"
        member_token = r_login.json()["data"]["access_token"]

    # Lấy thông tin user id của Member
    r_me = client.get(f"{BASE_URL}/users/me", headers={"Authorization": f"Bearer {member_token}"})
    assert r_me.status_code == 200
    member_user_id = r_me.json()["data"]["id"]

    log("✓ Cả 2 tài khoản đã sẵn sàng", "PASS")

    # 2. Test POST /workspaces (Tạo mới)
    log("2. Test POST /api/v1/workspaces...")
    owner_headers = {"Authorization": f"Bearer {owner_token}"}
    r = client.post(
        f"{BASE_URL}/workspaces",
        headers=owner_headers,
        json={"name": "TaskFlow Core Team", "description": "Không gian làm việc chính thức"},
    )
    assert r.status_code == 201, f"Create workspace failed: {r.text}"
    ws_data = r.json()["data"]
    workspace_id = ws_data["id"]
    assert ws_data["name"] == "TaskFlow Core Team"
    assert ws_data["current_user_role"] == "OWNER"
    assert ws_data["members_count"] == 1
    log(f"✓ Tạo workspace thành công (ID: {workspace_id})", "PASS")

    # 3. Test GET /workspaces (Danh sách)
    log("3. Test GET /api/v1/workspaces...")
    r = client.get(f"{BASE_URL}/workspaces", headers=owner_headers)
    assert r.status_code == 200
    workspaces = r.json()["data"]
    assert any(w["id"] == workspace_id for w in workspaces)
    log(f"✓ Lấy danh sách workspace thành công ({len(workspaces)} workspaces)", "PASS")

    # 4. Test GET /workspaces/{id} (Chi tiết)
    log(f"4. Test GET /api/v1/workspaces/{workspace_id}...")
    r = client.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=owner_headers)
    assert r.status_code == 200
    ws_detail = r.json()["data"]
    assert ws_detail["id"] == workspace_id
    assert len(ws_detail["members"]) == 1
    assert ws_detail["members"][0]["role"] == "OWNER"
    log("✓ Lấy chi tiết workspace và members thành công", "PASS")

    # 5. Test POST /workspaces/{id}/members/invite (Mời thành viên)
    log(f"5. Test POST /api/v1/workspaces/{workspace_id}/members/invite...")
    r = client.post(
        f"{BASE_URL}/workspaces/{workspace_id}/members/invite",
        headers=owner_headers,
        json={"email": member_email, "role": "MEMBER"},
    )
    assert r.status_code == 201, f"Invite member failed: {r.text}"
    invited_data = r.json()["data"]
    assert invited_data["email"] == member_email
    assert invited_data["role"] == "MEMBER"
    log("✓ Mời thành viên mới thành công", "PASS")

    # 6. Test Member truy cập workspace vừa được mời
    log("6. Test Member truy cập workspace đã gia nhập...")
    member_headers = {"Authorization": f"Bearer {member_token}"}
    r = client.get(f"{BASE_URL}/workspaces", headers=member_headers)
    assert r.status_code == 200
    member_workspaces = r.json()["data"]
    target_ws = next((w for w in member_workspaces if w["id"] == workspace_id), None)
    assert target_ws is not None
    assert target_ws["current_user_role"] == "MEMBER"
    log("✓ Member đã thấy workspace với vai trò MEMBER", "PASS")

    # 7. Test BR-WS-005: Member cố gắng DELETE workspace -> Phải bị từ chối 403 Forbidden
    log("7. Test BR-WS-005: Member cố gắng xóa workspace (Phải bị 403)...")
    r = client.delete(f"{BASE_URL}/workspaces/{workspace_id}", headers=member_headers)
    assert r.status_code == 403, f"Expected 403 Forbidden, got {r.status_code}"
    log("✓ Đúng quy tắc BR-WS-005: Member không được phép xóa workspace (403 Forbidden)", "PASS")

    # 8. Test PATCH /workspaces/{id}/members/{user_id} (Owner nâng quyền lên ADMIN)
    log("8. Test Owner nâng quyền Member lên ADMIN...")
    r = client.patch(
        f"{BASE_URL}/workspaces/{workspace_id}/members/{member_user_id}",
        headers=owner_headers,
        json={"role": "ADMIN"},
    )
    assert r.status_code == 200
    assert r.json()["data"]["role"] == "ADMIN"
    log("✓ Nâng quyền thành viên lên ADMIN thành công", "PASS")

    # 9. Test ADMIN cập nhật tên workspace (PATCH /workspaces/{id})
    log("9. Test ADMIN cập nhật tên workspace...")
    r = client.patch(
        f"{BASE_URL}/workspaces/{workspace_id}",
        headers=member_headers,
        json={"name": "TaskFlow Enterprise Global"},
    )
    assert r.status_code == 200
    assert r.json()["data"]["name"] == "TaskFlow Enterprise Global"
    log("✓ ADMIN cập nhật tên workspace thành công", "PASS")

    # 10. Test GET /workspaces/{id}/members (Danh sách thành viên)
    log(f"10. Test GET /api/v1/workspaces/{workspace_id}/members...")
    r = client.get(f"{BASE_URL}/workspaces/{workspace_id}/members", headers=owner_headers)
    assert r.status_code == 200
    members = r.json()["data"]
    assert len(members) == 2
    roles = {m["email"]: m["role"] for m in members}
    assert roles[owner_email] == "OWNER"
    assert roles[member_email] == "ADMIN"
    log(f"✓ Danh sách 2 thành viên chính xác ({roles})", "PASS")

    # 11. Test DELETE /workspaces/{id}/members/{user_id} (Gỡ thành viên)
    log("11. Test gỡ thành viên khỏi workspace...")
    r = client.delete(f"{BASE_URL}/workspaces/{workspace_id}/members/{member_user_id}", headers=owner_headers)
    assert r.status_code == 200
    log("✓ Gỡ thành viên thành công", "PASS")

    # 12. Test DELETE /workspaces/{id} (Owner xóa workspace)
    log("12. Test Owner xóa vĩnh viễn workspace...")
    r = client.delete(f"{BASE_URL}/workspaces/{workspace_id}", headers=owner_headers)
    assert r.status_code == 200
    log("✓ Xóa workspace thành công", "PASS")

    # 13. Verify workspace không còn tồn tại
    r = client.get(f"{BASE_URL}/workspaces/{workspace_id}", headers=owner_headers)
    assert r.status_code in [403, 404]
    log("✓ Xác nhận workspace đã bị xóa sạch khỏi hệ thống", "PASS")

    print("\n=======================================================")
    print("🎉 TẤT CẢ 12 KỊCH BẢN KIỂM THỬ WORKSPACE API ĐÃ VƯỢT QUA 100%!")
    print("=======================================================")

if __name__ == "__main__":
    try:
        run_tests()
    except AssertionError as e:
        print(f"\n[FAIL] Assertion failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Exception: {e}")
        sys.exit(1)
