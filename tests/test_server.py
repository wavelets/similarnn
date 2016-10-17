import falcon
import hug
import os
import numpy as np

os.environ['CONFIG_PATH'] = 'tests/data/config.toml'


from similarnn import server
from similarnn.storage import get_model_db


def test_num_topics_model_not_found():
    assert '404 Not Found' == \
        hug.test.get(server, "models/invalidmodel/num_topics").status


def test_num_topics():
    assert '200 OK' == \
        hug.test.get(server, "models/lda/num_topics").status


def test_num_topics():
    url = "models/lda/num_topics"
    response = hug.test.get(server, url)
    assert '200 OK' == response.status
    assert 'This model has 10 topics' == response.data


def test_post_documents_method_not_allowed():
    assert '405 Method Not Allowed' == \
        hug.test.get(server, "models/invalidmodel/documents").status


def test_post_documents_model_not_found():
    assert '404 Not Found' == \
        hug.test.post(server, "models/invalidmodel/documents").status


def test_post_documents():
    db = get_model_db(server.config['models']['lda'])
    assert db.n_items == 0

    url = "models/lda/documents"
    document = {"id": "document1", "body": "frango"}
    response = hug.test.post(server, url, body=document)
    assert '200 OK' == response.status

    expected_topics = server.config['models']['lda'].infer_topics(document)
    assert np.allclose(expected_topics, response.data, rtol=1e-3)
    assert db.n_items == 1


def test_get_document_404():
    response = hug.test.get(server, 'models/lda/documents/doc2')
    assert '404 Not Found' == response.status


def test_get_document():
    topics = np.array(range(10))
    db = get_model_db(server.config['models']['lda'])
    db.clean()
    db.add_item("doc1", topics)

    response = hug.test.get(server, 'models/lda/documents/doc1')
    assert '200 OK' == response.status
    assert np.allclose(topics, response.data, rtol=1e-3)


def test_get_document_404():
    response = hug.test.get(server, 'models/lda/documents/doc2/similar')
    assert '404 Not Found' == response.status


def test_get_document():
    topics = np.array(range(10))
    db = get_model_db(server.config['models']['lda'])
    db.clean()
    db.add_item("doc1", topics)
    db.add_item("doc2", topics)

    response = hug.test.get(server, 'models/lda/documents/doc1/similar')
    assert '200 OK' == response.status
    assert ['similar'] == list(response.data.keys())
    assert 1 == len(response.data['similar'])
    assert 'doc2' == response.data['similar'][0]['key']
    assert 0 == response.data['similar'][0]['distance']