

def test_projects_and_documents_workflow(client, db):
    # 1. Sign up and Login
    client.post(
        "/api/v1/auth/signup",
        json={
            "email": "mwp@example.com",
            "username": "mwpuser",
            "full_name": "MWP User",
            "password": "securepassword123",
        },
    )

    login_res = client.post(
        "/api/v1/auth/login",
        data={
            "username": "mwp@example.com",
            "password": "securepassword123",
        },
    )
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 2. Create organization
    org_res = client.post(
        "/api/v1/organizations/",
        json={"name": "Incubator", "slug": "incubator"},
        headers=headers,
    )
    assert org_res.status_code == 201
    org_id = org_res.json()["id"]

    # 3. Create workspace
    workspace_res = client.post(
        f"/api/v1/workspaces/?org_id={org_id}",
        json={
            "name": "Sprint Space",
            "description": "workspace for sprints",
            "visibility": "private",
        },
        headers=headers,
    )
    assert workspace_res.status_code == 201
    workspace_id = workspace_res.json()["id"]

    # 4. Project CRUD tests
    # Create Project
    project_res = client.post(
        f"/api/v1/projects/{workspace_id}",
        json={
            "name": "AI Content Writer",
            "description": "GPT integration",
            "slug": "ai-writer",
            "priority": "High",
        },
        headers=headers,
    )
    assert project_res.status_code == 201
    project_id = project_res.json()["id"]
    assert project_res.json()["name"] == "AI Content Writer"
    assert project_res.json()["slug"] == "ai-writer"

    # List Projects
    list_res = client.get(f"/api/v1/projects/{workspace_id}", headers=headers)
    assert list_res.status_code == 200
    assert len(list_res.json()) >= 1

    # Update Project
    update_res = client.put(
        f"/api/v1/projects/{workspace_id}/{project_id}",
        json={"status": "Development"},
        headers=headers,
    )
    assert update_res.status_code == 200
    assert update_res.json()["status"] == "Development"

    # Duplicate Project
    dup_res = client.post(
        f"/api/v1/projects/{workspace_id}/{project_id}/duplicate",
        headers=headers,
    )
    assert dup_res.status_code == 200
    assert dup_res.json()["name"] == "AI Content Writer (Copy)"
    assert dup_res.json()["slug"] == "ai-writer-copy"

    # Archive Project
    archive_res = client.post(
        f"/api/v1/projects/{workspace_id}/{project_id}/archive",
        headers=headers,
    )
    assert archive_res.status_code == 200
    assert archive_res.json()["archived"] is True
    assert archive_res.json()["status"] == "Archived"

    # Restore Project
    restore_res = client.post(
        f"/api/v1/projects/{workspace_id}/{project_id}/restore",
        headers=headers,
    )
    assert restore_res.status_code == 200
    assert restore_res.json()["archived"] is False

    # Get Project Dashboard Stats
    dash_res = client.get(
        f"/api/v1/projects/{workspace_id}/{project_id}/dashboard",
        headers=headers,
    )
    assert dash_res.status_code == 200
    dash_data = dash_res.json()
    assert dash_data["project"]["name"] == "AI Content Writer"
    assert "stats" in dash_data

    # 5. Document Management tests
    # Upload Document
    files = {
        "file": (
            "requirements.txt",
            b"Initial product spec bytes content",
            "text/plain",
        )
    }
    data = {
        "name": "PRD Spec",
        "project_id": project_id,
        "category": "Requirements",
        "tags_json": '["v1", "ai"]',
    }
    upload_res = client.post(
        f"/api/v1/documents/{workspace_id}",
        files=files,
        data=data,
        headers=headers,
    )
    assert upload_res.status_code == 201
    doc_data = upload_res.json()
    doc_id = doc_data["id"]
    assert doc_data["name"] == "PRD Spec"
    assert doc_data["current_version_number"] == 1
    assert doc_data["category"] == "Requirements"

    # List Documents
    doc_list = client.get(f"/api/v1/documents/{workspace_id}", headers=headers)
    assert doc_list.status_code == 200
    assert len(doc_list.json()) >= 1

    # Download Document
    download_res = client.get(
        f"/api/v1/documents/{workspace_id}/{doc_id}/download", headers=headers
    )
    assert download_res.status_code == 200
    assert download_res.content == b"Initial product spec bytes content"

    # Upload New Version
    new_version_files = {
        "file": (
            "requirements_v2.txt",
            b"Second revision spec bytes content",
            "text/plain",
        )
    }
    version_res = client.post(
        f"/api/v1/documents/{workspace_id}/{doc_id}/version",
        files=new_version_files,
        headers=headers,
    )
    assert version_res.status_code == 200
    assert version_res.json()["current_version_number"] == 2

    # Download New Version and confirm updated content
    download_v2_res = client.get(
        f"/api/v1/documents/{workspace_id}/{doc_id}/download", headers=headers
    )
    assert download_v2_res.status_code == 200
    assert download_v2_res.content == b"Second revision spec bytes content"

    # Restore Version 1
    restore_v1_res = client.post(
        f"/api/v1/documents/{workspace_id}/{doc_id}/version/1/restore",
        headers=headers,
    )
    assert restore_v1_res.status_code == 200
    assert (
        restore_v1_res.json()["current_version_number"] == 3
    )  # incremented to new active version

    # Download restored and confirm matching version 1 bytes
    download_restored = client.get(
        f"/api/v1/documents/{workspace_id}/{doc_id}/download", headers=headers
    )
    assert download_restored.status_code == 200
    assert download_restored.content == b"Initial product spec bytes content"

    # 6. Global Search tests
    search_res = client.get(
        f"/api/v1/search/?q=Content&workspace_id={workspace_id}", headers=headers
    )
    assert search_res.status_code == 200
    results = search_res.json()
    assert len(results["projects"]) >= 1
    assert results["projects"][0]["name"] == "AI Content Writer"

    # 7. Notifications tests
    # Trigger a mock notification directly to test notification center list/reads
    from app.models.notification import Notification
    from app.models.user import User

    db_user = db.query(User).filter_by(email="mwp@example.com").first()
    db_notif = Notification(
        user_id=db_user.id,
        type="Success",
        title="Welcome Alert",
        message="Your account is configured.",
    )
    db.add(db_notif)
    db.commit()

    # Get notifications list
    notif_list = client.get("/api/v1/notifications/", headers=headers)
    assert notif_list.status_code == 200
    assert len(notif_list.json()) >= 1
    notif_id = notif_list.json()[0]["id"]

    # Mark Read
    read_res = client.post(f"/api/v1/notifications/{notif_id}/read", headers=headers)
    assert read_res.status_code == 200
    assert read_res.json()["read"] is True

    # Mark Archive
    archive_notif = client.post(
        f"/api/v1/notifications/{notif_id}/archive", headers=headers
    )
    assert archive_notif.status_code == 200
    assert archive_notif.json()["archived"] is True

    # Mark All Read
    all_read_res = client.post("/api/v1/notifications/read-all", headers=headers)
    assert all_read_res.status_code == 200

    # 8. Activity Timeline tests
    activities_res = client.get(f"/api/v1/activities/{workspace_id}", headers=headers)
    assert activities_res.status_code == 200
    assert len(activities_res.json()) >= 1
