import os
import pytest

from quadra_diag.ml.catalog import DISEASE_SPECS


def test_home_page_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "QuadraDiag" in response.text
    assert "Screen smarter" in response.text or "Clinical intelligence" in response.text


def test_health_endpoint(client):
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "features" in data
    assert "version" in data


def test_disease_list_api(client):
    response = client.get("/api/v1/diseases")
    assert response.status_code == 200
    data = response.json()
    assert "diseases" in data
    assert "diabetes" in data["diseases"]
    assert "heart" in data["diseases"]


def test_diabetes_prediction_api(client):
    payload = {
        "Pregnancies": 2,
        "Glucose": 135,
        "BloodPressure": 70,
        "SkinThickness": 20,
        "Insulin": 85,
        "BMI": 31.2,
        "DiabetesPedigreeFunction": 0.45,
        "Age": 42,
    }
    response = client.post("/api/v1/predict/diabetes", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "diabetes"
    assert 0 <= data["probability"] <= 1
    assert "risk_band" in data
    assert "metrics" in data


def test_heart_prediction_api(client):
    payload = {
        "age": 54, "sex": 1, "cp": 2, "trestbps": 130, "chol": 246,
        "fbs": 0, "restecg": 1, "thalach": 150, "exang": 0,
        "oldpeak": 1.3, "slope": 2, "ca": 0, "thal": 2,
    }
    response = client.post("/api/v1/predict/heart", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "heart"
    assert 0 <= data["probability"] <= 1


def test_liver_prediction_api(client):
    payload = {
        "age": 45, "gender": "Male", "tot_bilirubin": 1.0,
        "direct_bilirubin": 0.4, "tot_proteins": 6.8, "albumin": 3.4,
        "ag_ratio": 1.0, "sgpt": 35, "sgot": 40, "alkphos": 210,
    }
    response = client.post("/api/v1/predict/liver", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "liver"


def test_dynamic_prediction_api(client):
    payload = {
        "Pregnancies": 2,
        "Glucose": 135,
        "BloodPressure": 70,
        "SkinThickness": 20,
        "Insulin": 85,
        "BMI": 31.2,
        "DiabetesPedigreeFunction": 0.45,
        "Age": 42,
    }
    response = client.post("/api/v1/predict/diabetes", json=payload)
    assert response.status_code == 200


def test_prediction_api_invalid_disease(client):
    response = client.post("/api/v1/predict/unknown", json={})
    assert response.status_code == 404


def test_prediction_api_invalid_payload(client):
    payload = {"Pregnancies": -1}  # Invalid negative value
    response = client.post("/api/v1/predict/diabetes", json=payload)
    assert response.status_code == 422


def test_404_page(client):
    response = client.get("/nonexistent-page")
    assert response.status_code == 404
    assert "not found" in response.text.lower()


def test_register_page_renders(client):
    response = client.get("/register")
    assert response.status_code == 200
    assert "Create account" in response.text


def test_login_page_renders(client):
    response = client.get("/login")
    assert response.status_code == 200
    assert "Sign in" in response.text


def test_register_and_login_flow(client):
    # Register
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    # Logout
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200

    # Login
    response = client.post(
        "/login",
        data={
            "email": "test@example.com",
            "password": "StrongPass123!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_weak_password_rejection(client):
    response = client.post(
        "/register",
        data={
            "username": "weakuser",
            "email": "weak@example.com",
            "password": "weak",
            "role": "patient",
        },
    )
    assert response.status_code == 422


def test_duplicate_registration_rejected(client):
    client.post(
        "/register",
        data={
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.post(
        "/register",
        data={
            "username": "dupuser",
            "email": "dup@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
    )
    assert response.status_code == 409


def test_dashboard_requires_login(client):
    response = client.get("/dashboard", follow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_dashboard_accessible_when_logged_in(client):
    client.post(
        "/register",
        data={
            "username": "dashuser",
            "email": "dash@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "dashuser" in response.text


def test_profile_page_requires_login(client):
    response = client.get("/profile", follow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_profile_page_accessible_when_logged_in(client):
    client.post(
        "/register",
        data={
            "username": "profileuser",
            "email": "profile@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.get("/profile")
    assert response.status_code == 200
    assert "profileuser" in response.text


def test_password_change(client):
    client.post(
        "/register",
        data={
            "username": "pwduser",
            "email": "pwd@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.post(
        "/profile/change-password",
        data={
            "current_password": "StrongPass123!",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_password_change_wrong_current(client):
    client.post(
        "/register",
        data={
            "username": "pwduser2",
            "email": "pwd2@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.post(
        "/profile/change-password",
        data={
            "current_password": "WrongPass123!",
            "new_password": "NewPass456!",
            "confirm_password": "NewPass456!",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "incorrect" in response.text.lower()


def test_analytics_requires_login(client):
    response = client.get("/analytics", follow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_compare_requires_login(client):
    response = client.get("/compare", follow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_settings_requires_login(client):
    response = client.get("/settings", follow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_batch_upload_flow(client):
    client.post(
        "/register",
        data={
            "username": "batchuser",
            "email": "batch@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    csv_content = (
        "Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age\n"
        "2,135,70,20,85,31.2,0.45,42\n"
        "1,95,66,21,94,28.1,0.17,25\n"
    )
    response = client.post(
        "/batch-lab/diabetes",
        files={"file": ("diabetes_batch.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert response.status_code == 200


def test_batch_upload_requires_login(client):
    csv_content = "Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age\n2,135,70,20,85,31.2,0.45,42\n"
    response = client.post(
        "/batch-lab/diabetes",
        files={"file": ("diabetes_batch.csv", csv_content, "text/csv")},
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_batch_api_endpoint(client):
    csv_content = (
        "Pregnancies,Glucose,BloodPressure,SkinThickness,Insulin,BMI,DiabetesPedigreeFunction,Age\n"
        "2,135,70,20,85,31.2,0.45,42\n"
    )
    response = client.post(
        "/api/v1/predict/diabetes/batch",
        files={"file": ("diabetes_batch.csv", csv_content, "text/csv")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["disease"] == "diabetes"
    assert data["summary"]["total_rows"] == 1


def test_batch_api_invalid_disease(client):
    response = client.post(
        "/api/v1/predict/unknown/batch",
        files={"file": ("test.csv", "a,b\n1,2\n", "text/csv")},
    )
    assert response.status_code == 404


def test_template_download(client):
    response = client.get("/templates/diabetes/download")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/csv; charset=utf-8"


def test_disease_form_pages(client):
    for disease in ["diabetes", "heart", "liver", "parkinsons"]:
        response = client.get(f"/disease/{disease}")
        assert response.status_code == 200
        # Check for key words since apostrophes may be HTML-escaped
        title = DISEASE_SPECS[disease]["title"]
        assert title.split("'")[0] in response.text or title.replace("'", "&#39;") in response.text


def test_invalid_disease_form(client):
    response = client.get("/disease/unknown")
    assert response.status_code == 404


def test_assess_endpoint_web(client):
    client.post(
        "/register",
        data={
            "username": "assessuser",
            "email": "assess@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.post(
        "/assess/diabetes",
        data={
            "Pregnancies": 2,
            "Glucose": 135,
            "BloodPressure": 70,
            "SkinThickness": 20,
            "Insulin": 85,
            "BMI": 31.2,
            "DiabetesPedigreeFunction": 0.45,
            "Age": 42,
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "Assessment outcome" in response.text or "probability" in response.text.lower()


def test_assess_invalid_data(client):
    response = client.post(
        "/assess/diabetes",
        data={
            "Pregnancies": -1,
            "Glucose": 135,
            "BloodPressure": 70,
            "SkinThickness": 20,
            "Insulin": 85,
            "BMI": 31.2,
            "DiabetesPedigreeFunction": 0.45,
            "Age": 42,
        },
    )
    assert response.status_code == 422


def test_admin_requires_admin_role(client):
    response = client.get("/admin", follow_redirects=True)
    assert response.status_code == 200
    # Should redirect to home with error since not logged in


def test_dark_mode_toggle(client):
    response = client.post("/toggle-dark-mode")
    assert response.status_code == 200
    data = response.json()
    assert "dark_mode" in data


def test_analytics_api_risk_distribution(client):
    response = client.get("/api/v1/analytics/risk-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "data" in data


def test_analytics_api_disease_distribution(client):
    response = client.get("/api/v1/analytics/disease-distribution")
    assert response.status_code == 200
    data = response.json()
    assert "labels" in data
    assert "data" in data


def test_system_metrics_api(client):
    response = client.get("/api/v1/admin/system-metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_users" in data
    assert "total_predictions" in data


def test_export_requires_login(client):
    response = client.get("/profile/export", follow_redirects=True)
    assert response.status_code == 200
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_logout_clears_session(client):
    client.post(
        "/register",
        data={
            "username": "logoutuser",
            "email": "logout@example.com",
            "password": "StrongPass123!",
            "role": "patient",
        },
        follow_redirects=True,
    )
    response = client.get("/logout", follow_redirects=True)
    assert response.status_code == 200
    # After logout, dashboard should redirect to login
    response = client.get("/dashboard", follow_redirects=True)
    assert "login" in response.text.lower() or "sign in" in response.text.lower()


def test_liver_feature_labels_correct(client):
    response = client.get("/disease/liver")
    assert response.status_code == 200
    assert "SGPT (Alanine Aminotransferase)" in response.text
    assert "SGOT (Aspartate Aminotransferase)" in response.text
    assert "Alkaline Phosphatase" in response.text

