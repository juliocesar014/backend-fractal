import pytest
from api.models import Exam


@pytest.fixture
def create_exams(db):
    """Fixture to create multiple exams."""
    return Exam.objects.bulk_create([
        Exam(name="Exam 1", description="First test exam",
             start_date="2024-01-01T10:00:00Z", end_date="2024-01-02T10:00:00Z"),
        Exam(name="Exam 2", description="Second test exam",
             start_date="2024-02-01T10:00:00Z", end_date="2024-02-02T10:00:00Z"),
        Exam(name="Exam 3", description="Third test exam",
             start_date="2024-03-01T10:00:00Z", end_date="2024-03-02T10:00:00Z"),
        Exam(name="Alpha Exam", description="Alpha test exam",
             start_date="2024-04-01T10:00:00Z", end_date="2024-04-02T10:00:00Z"),
    ])


@pytest.fixture
def create_exam(db):
    """Fixture to create a single exam."""
    return Exam.objects.create(
        name="Test Exam",
        description="A test exam",
        start_date="2024-01-01T10:00:00Z",
        end_date="2024-01-02T10:00:00Z",
    )


@pytest.mark.django_db
def test_list_exams(client, create_exams):
    """Test listing all exams."""
    url = "/api/exams/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4


@pytest.mark.django_db
def test_list_exams_search(client, create_exams):
    """Test listing exams with search functionality."""
    url = "/api/exams/?search=Exam"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 4
    exam_names = [exam["name"] for exam in data]
    assert "Exam 1" in exam_names
    assert "Exam 2" in exam_names


@pytest.mark.django_db
def test_list_exams_order(client, create_exams):
    """Test listing exams with ordering."""
    url = "/api/exams/?order=name"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    exam_names = [exam["name"] for exam in data]
    assert exam_names == ["Alpha Exam", "Exam 1", "Exam 2", "Exam 3"]


@pytest.mark.django_db
def test_list_exams_pagination(client, create_exams):
    """Test listing exams with pagination."""
    url = "/api/exams/?page=1&page_size=2"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["name"] == "Exam 1"
    assert data[1]["name"] == "Exam 2"



@pytest.mark.django_db
def test_get_exam(client, create_exam):
    """Test retrieving a single exam by ID."""
    url = f"/api/exams/{create_exam.id}/"
    response = client.get(url)
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Test Exam"
    assert data["description"] == "A test exam"


@pytest.mark.django_db
def test_create_exam(client):
    """Test creating a new exam."""
    url = "/api/exams/"
    payload = {
        "name": "New Exam",
        "description": "Another test exam",
        "start_date": "2024-02-01T10:00:00Z",
        "end_date": "2024-02-02T10:00:00Z",
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "New Exam"
    assert data["description"] == "Another test exam"


@pytest.mark.django_db
def test_create_exam_duplicate_name(client, create_exam):
    """Test creating an exam with duplicate name."""
    url = "/api/exams/"
    payload = {
        "name": "Test Exam",
        "description": "Duplicate test exam",
        "start_date": "2024-05-01T10:00:00Z",
        "end_date": "2024-05-02T10:00:00Z",
    }
    response = client.post(url, payload, content_type="application/json")
    assert response.status_code == 400
    assert "already exists" in response.json()["error"]


@pytest.mark.django_db
def test_update_exam(client, create_exam):
    """Test updating an existing exam."""
    url = f"/api/exams/{create_exam.id}/"
    payload = {
        "name": "Updated Exam",
        "description": "Updated description",
        "start_date": "2024-01-01T10:00:00Z",
        "end_date": "2024-01-02T10:00:00Z",
    }
    response = client.put(url, payload, content_type="application/json")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Exam"
    assert data["description"] == "Updated description"


@pytest.mark.django_db
def test_delete_exam(client, create_exam):
    """Test deleting an exam."""
    url = f"/api/exams/{create_exam.id}/"
    response = client.delete(url)
    assert response.status_code == 200
    assert response.json() == "Exam successfully deleted."
    assert not Exam.objects.filter(id=create_exam.id).exists()


@pytest.mark.django_db
def test_delete_exam_not_found(client):
    """Test deleting an exam that does not exist."""
    url = "/api/exams/999/"
    response = client.delete(url)
    assert response.status_code == 404
    assert response.json()["error"] == "Exam not found."
