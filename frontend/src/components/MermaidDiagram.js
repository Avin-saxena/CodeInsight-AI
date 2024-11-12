import React, { useState } from 'react';
import { Form, Button, Card, Container, Alert } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faDiagramProject, faWandMagicSparkles } from '@fortawesome/free-solid-svg-icons';
import mermaid from 'mermaid';

function MermaidDiagram({ analysisData }) {
  const [diagramCode, setDiagramCode] = useState('');
  const [diagramType, setDiagramType] = useState('flowchart');
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const generateDiagram = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/mermaid/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_data: analysisData, diagram_type: diagramType }),
      });

      if (!response.ok) {
        throw new Error('Failed to generate diagram');
      }

      const result = await response.json();

      if (result.error) {
        throw new Error(result.error);
      }

      setDiagramCode(result.mermaid_code);
      mermaid.initialize({ startOnLoad: true });
      mermaid.contentLoaded();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Container className="mb-4">
      <Card>
        <Card.Header className="bg-warning text-dark">
          <FontAwesomeIcon icon={faDiagramProject} className="me-2" />
          Generate Mermaid Diagram
        </Card.Header>
        <Card.Body>
          {error && <Alert variant="danger">{error}</Alert>}
          <Form.Group className="mb-3">
            <Form.Label>Diagram Type</Form.Label>
            <Form.Select
              value={diagramType}
              onChange={(e) => setDiagramType(e.target.value)}
            >
              <option value="flowchart">Flowchart</option>
              <option value="class">Class Diagram</option>
            </Form.Select>
          </Form.Group>
          <Button
            onClick={generateDiagram}
            variant="warning"
            disabled={loading}
            className="w-100 mb-3"
          >
            {loading ? (
              <>
                <span className="spinner-border spinner-border-sm me-2" />
                Generating...
              </>
            ) : (
              <>
                <FontAwesomeIcon icon={faWandMagicSparkles} className="me-2" />
                Generate Diagram
              </>
            )}
          </Button>
          {diagramCode && (
            <div className="bg-light p-3 rounded">
              <div className="mermaid">
                {diagramCode}
              </div>
            </div>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}

export default MermaidDiagram;