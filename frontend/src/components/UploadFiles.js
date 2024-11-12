// UploadFiles.js

import React, { useState } from 'react';
import { Form, Button, Card, Container, Row, Col, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faFileCode } from '@fortawesome/free-solid-svg-icons';

function UploadFiles({ onAnalysisComplete }) {
  const [appFile, setAppFile] = useState(null);
  const [apiFile, setApiFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!appFile || !apiFile) {
      setError('Please select both app.py and api.py files.');
      return;
    }

    setLoading(true);
    setError(null);
    const formData = new FormData();
    formData.append('app_file', appFile);
    formData.append('api_file', apiFile);

    try {
      const response = await fetch('http://localhost:8000/analyze/', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'An error occurred');
      }

      const result = await response.json();
      onAnalysisComplete(result);
    } catch (error) {
      console.error('Fetch error:', error);
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleFileChange = (setter) => (e) => {
    const file = e.target.files[0];
    if (file && file.name.endsWith('.py')) {
      setter(file);
      setError(null);
    } else {
      setError('Please select a valid Python (.py) file');
    }
  };

  return (
    <Container className="mb-4">
      <Card>
        <Card.Header className="bg-primary text-white">
          <FontAwesomeIcon icon={faUpload} className="me-2" />
          Upload Python Files
        </Card.Header>
        <Card.Body>
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          )}
          <Form onSubmit={handleSubmit}>
            <Row>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    <FontAwesomeIcon icon={faFileCode} className="me-2" />
                    app.py
                  </Form.Label>
                  <Form.Control
                    type="file"
                    accept=".py"
                    onChange={handleFileChange(setAppFile)}
                    isInvalid={error && !appFile}
                  />
                  <Form.Text className="text-muted">
                    Select your main application file
                  </Form.Text>
                </Form.Group>
              </Col>
              <Col md={6}>
                <Form.Group className="mb-3">
                  <Form.Label>
                    <FontAwesomeIcon icon={faFileCode} className="me-2" />
                    api.py
                  </Form.Label>
                  <Form.Control
                    type="file"
                    accept=".py"
                    onChange={handleFileChange(setApiFile)}
                    isInvalid={error && !apiFile}
                  />
                  <Form.Text className="text-muted">
                    Select your API file
                  </Form.Text>
                </Form.Group>
              </Col>
            </Row>
            <Button
              type="submit"
              variant="primary"
              disabled={loading || !appFile || !apiFile}
              className="w-100"
            >
              {loading ? (
                <>
                  <span className="spinner-border spinner-border-sm me-2" />
                  Analyzing...
                </>
              ) : (
                <>
                  <FontAwesomeIcon icon={faUpload} className="me-2" />
                  Analyze Files
                </>
              )}
            </Button>
          </Form>
        </Card.Body>
      </Card>
    </Container>
  );
}

export default UploadFiles;