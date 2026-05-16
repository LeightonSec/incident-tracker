import re
import pytest
from app import app as flask_app, db, generate_ticket_id


@pytest.fixture
def client():
    flask_app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
    })
    with flask_app.app_context():
        db.create_all()
        yield flask_app.test_client()
        db.session.remove()
        db.drop_all()


def _create_ticket(client, **overrides):
    payload = {'title': 'Test Incident', 'description': 'Details here', **overrides}
    return client.post('/api/tickets', json=payload)


class TestTicketId:
    def test_format(self):
        tid = generate_ticket_id()
        assert re.match(r'^INC-\d{8}-[A-Z0-9]{4}$', tid)

    def test_unique(self):
        ids = {generate_ticket_id() for _ in range(20)}
        assert len(ids) > 1


class TestIndex:
    def test_index(self, client):
        assert client.get('/').status_code == 200

    def test_ticket_detail_page(self, client):
        assert client.get('/ticket/INC-20260516-TEST').status_code == 200


class TestCreateTicket:
    def test_success(self, client):
        resp = _create_ticket(client)
        assert resp.status_code == 201
        data = resp.get_json()
        assert re.match(r'^INC-\d{8}-[A-Z0-9]{4}$', data['ticket_id'])
        assert data['title'] == 'Test Incident'
        assert data['status'] == 'Open'
        assert data['priority'] == 'Medium'

    def test_missing_title(self, client):
        resp = client.post('/api/tickets', json={'description': 'desc'})
        assert resp.status_code == 400

    def test_missing_description(self, client):
        resp = client.post('/api/tickets', json={'title': 'title'})
        assert resp.status_code == 400

    def test_no_body(self, client):
        resp = client.post('/api/tickets', content_type='application/json')
        assert resp.status_code == 400

    def test_invalid_priority(self, client):
        resp = _create_ticket(client, priority='Urgent')
        assert resp.status_code == 400

    def test_invalid_status(self, client):
        resp = _create_ticket(client, status='Pending')
        assert resp.status_code == 400

    def test_custom_priority(self, client):
        resp = _create_ticket(client, priority='Critical')
        assert resp.status_code == 201
        assert resp.get_json()['priority'] == 'Critical'

    def test_title_truncated_at_200(self, client):
        resp = _create_ticket(client, title='x' * 300)
        assert resp.status_code == 201
        assert len(resp.get_json()['title']) == 200


class TestGetTickets:
    def test_empty_list(self, client):
        resp = client.get('/api/tickets')
        assert resp.status_code == 200
        assert resp.get_json() == []

    def test_returns_created_ticket(self, client):
        _create_ticket(client)
        resp = client.get('/api/tickets')
        assert len(resp.get_json()) == 1

    def test_filter_by_status(self, client):
        _create_ticket(client)
        _create_ticket(client, status='Resolved')
        resp = client.get('/api/tickets?status=Resolved')
        data = resp.get_json()
        assert len(data) == 1
        assert data[0]['status'] == 'Resolved'

    def test_filter_by_priority(self, client):
        _create_ticket(client, priority='Critical')
        _create_ticket(client, priority='Low')
        resp = client.get('/api/tickets?priority=Critical')
        assert all(t['priority'] == 'Critical' for t in resp.get_json())


class TestGetTicket:
    def test_get_existing(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        resp = client.get(f'/api/tickets/{tid}')
        assert resp.status_code == 200
        assert resp.get_json()['ticket_id'] == tid

    def test_get_nonexistent(self, client):
        assert client.get('/api/tickets/INC-00000000-XXXX').status_code == 404

    def test_includes_comments_key(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        data = client.get(f'/api/tickets/{tid}').get_json()
        assert 'comments' in data


class TestUpdateTicket:
    def test_update_status(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        resp = client.put(f'/api/tickets/{tid}', json={'status': 'In Progress'})
        assert resp.status_code == 200
        assert resp.get_json()['status'] == 'In Progress'

    def test_resolved_sets_resolved_at(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        resp = client.put(f'/api/tickets/{tid}', json={'status': 'Resolved'})
        assert resp.get_json()['resolved_at'] is not None

    def test_update_nonexistent(self, client):
        assert client.put('/api/tickets/INC-FAKE', json={'status': 'Resolved'}).status_code == 404

    def test_no_body(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        assert client.put(f'/api/tickets/{tid}', content_type='application/json').status_code == 400


class TestDeleteTicket:
    def test_delete_existing(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        assert client.delete(f'/api/tickets/{tid}').status_code == 200
        assert client.get(f'/api/tickets/{tid}').status_code == 404

    def test_delete_nonexistent(self, client):
        assert client.delete('/api/tickets/INC-FAKE').status_code == 404


class TestComments:
    def test_add_comment(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        resp = client.post(f'/api/tickets/{tid}/comments',
                           json={'content': 'Investigating now', 'author': 'analyst'})
        assert resp.status_code == 201
        assert resp.get_json()['content'] == 'Investigating now'

    def test_comment_appears_in_ticket(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        client.post(f'/api/tickets/{tid}/comments', json={'content': 'Note'})
        comments = client.get(f'/api/tickets/{tid}').get_json()['comments']
        assert len(comments) == 1

    def test_missing_content(self, client):
        tid = _create_ticket(client).get_json()['ticket_id']
        assert client.post(f'/api/tickets/{tid}/comments', json={}).status_code == 400

    def test_comment_on_nonexistent_ticket(self, client):
        resp = client.post('/api/tickets/INC-FAKE/comments', json={'content': 'x'})
        assert resp.status_code == 404


class TestStats:
    def test_empty_stats(self, client):
        data = client.get('/api/stats').get_json()
        assert data['total'] == 0
        assert data['open'] == 0
        assert data['critical'] == 0

    def test_stats_counts(self, client):
        _create_ticket(client, priority='Critical')
        _create_ticket(client, priority='High')
        _create_ticket(client, status='Resolved')
        data = client.get('/api/stats').get_json()
        assert data['total'] == 3
        assert data['open'] == 2
        assert data['resolved'] == 1
        assert data['critical'] == 1

    def test_escalated_count(self, client):
        _create_ticket(client, escalated=True)
        _create_ticket(client)
        assert client.get('/api/stats').get_json()['escalated'] == 1
