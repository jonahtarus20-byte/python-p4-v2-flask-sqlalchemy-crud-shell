
import pytest
from app import app
from models import db, Pet

@pytest.fixture(autouse=True)
def setup_and_teardown():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_get_pets_empty(client):
    response = client.get('/pets')
    assert response.status_code == 200
    assert response.get_json() == []

def test_create_pet(client):
    response = client.post('/pets', json={'name': 'Fluffy', 'species': 'Cat'})
    assert response.status_code == 201
    data = response.get_json()
    assert data['name'] == 'Fluffy'
    assert data['species'] == 'Cat'
    assert 'id' in data

def test_get_pets_after_create(client):
    client.post('/pets', json={'name': 'Fluffy', 'species': 'Cat'})
    client.post('/pets', json={'name': 'Rex', 'species': 'Dog'})

    response = client.get('/pets')
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 2
    assert data[0]['name'] == 'Fluffy'
    assert data[1]['name'] == 'Rex'

def test_get_pet_by_id(client):
    # Create a pet first
    create_response = client.post('/pets', json={'name': 'Fluffy', 'species': 'Cat'})
    pet_id = create_response.get_json()['id']

    # Get the pet by ID
    response = client.get(f'/pets/{pet_id}')
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Fluffy'
    assert data['species'] == 'Cat'
    assert data['id'] == pet_id

def test_get_pet_by_id_not_found(client):
    response = client.get('/pets/999')
    assert response.status_code == 404
    assert response.get_json() == {"error": "Pet not found"}

def test_update_pet(client):
    # Create a pet first
    create_response = client.post('/pets', json={'name': 'Fluffy', 'species': 'Cat'})
    pet_id = create_response.get_json()['id']

    # Update the pet
    response = client.patch(f'/pets/{pet_id}', json={'name': 'Fluffball', 'species': 'Cat'})
    assert response.status_code == 200
    data = response.get_json()
    assert data['name'] == 'Fluffball'
    assert data['species'] == 'Cat'

def test_update_pet_not_found(client):
    response = client.patch('/pets/999', json={'name': 'New Name'})
    assert response.status_code == 404
    assert response.get_json() == {"error": "Pet not found"}

def test_delete_pet(client):
    # Create a pet first
    create_response = client.post('/pets', json={'name': 'Fluffy', 'species': 'Cat'})
    pet_id = create_response.get_json()['id']

    # Delete the pet
    response = client.delete(f'/pets/{pet_id}')
    assert response.status_code == 200
    assert response.get_json() == {"message": "Pet deleted"}

    # Verify it's deleted
    get_response = client.get(f'/pets/{pet_id}')
    assert get_response.status_code == 404

def test_delete_pet_not_found(client):
    response = client.delete('/pets/999')
    assert response.status_code == 404
    assert response.get_json() == {"error": "Pet not found"}

def test_create_pet_missing_fields(client):
    response = client.post('/pets', json={'name': 'Fluffy'})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Name and species are required"}

    response = client.post('/pets', json={'species': 'Cat'})
    assert response.status_code == 400
    assert response.get_json() == {"error": "Name and species are required"}
