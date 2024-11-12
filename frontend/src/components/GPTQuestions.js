// GPTQuestions.js

import React, { useState, useEffect } from 'react';
import { Form, Button, Card, Container, Alert, Spinner, Badge, Tabs, Tab, Dropdown } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faRobot, faPaperPlane, faHistory, faSave, faSearch, faList, faSpinner } from '@fortawesome/free-solid-svg-icons';

const PREDEFINED_QUESTIONS = [
  "What functions does api.py have?",
  "What are different classes present in api.py?",
  "How many imports are present in app.py?",
  "How many functions are related in both app.py and api.py?"
];

function GPTQuestions({ analysisData }) {
  const [question, setQuestion] = useState('');
  const [gptResponse, setGptResponse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [history, setHistory] = useState([]);
  const [savedResponses, setSavedResponses] = useState([]);
  const [activeTab, setActiveTab] = useState('ask');
  const [batchQuestions, setBatchQuestions] = useState([]);
  const [batchLoading, setBatchLoading] = useState(false);

  useEffect(() => {
    // Load today's responses when component mounts
    loadTodayResponses();
  }, []);

  const loadTodayResponses = async () => {
    try {
      const today = new Date().toISOString().split('T')[0];
      const response = await fetch(`http://localhost:8000/gpt/responses/${today}`);
      if (!response.ok) throw new Error('Failed to load saved responses');
      const data = await response.json();
      setSavedResponses(data.responses || []);
    } catch (error) {
      console.error('Error loading saved responses:', error);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/gpt/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ analysis_data: analysisData, question }),
      });

      if (!response.ok) {
        throw new Error('Failed to get response from GPT');
      }

      const result = await response.json();
      const newInteraction = {
        question,
        response: result.response,
        timestamp: new Date().toISOString(),
        file_path: result.file_path
      };

      setGptResponse(result.response);
      setHistory(prev => [newInteraction, ...prev]);
      setQuestion('');
      
      // Refresh saved responses
      await loadTodayResponses();
    } catch (error) {
      setError(error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleBatchSubmit = async () => {
    if (batchQuestions.length === 0) return;

    setBatchLoading(true);
    setError(null);

    try {
      const response = await fetch('http://localhost:8000/gpt/batch', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          analysis_data: analysisData,
          questions: batchQuestions
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to process batch questions');
      }

      const results = await response.json();
      const newInteractions = results.map(result => ({
        question: result.question,
        response: result.response,
        timestamp: result.timestamp,
        file_path: result.file_path
      }));

      setHistory(prev => [...newInteractions, ...prev]);
      setBatchQuestions([]);
      await loadTodayResponses();
    } catch (error) {
      setError(error.message);
    } finally {
      setBatchLoading(false);
    }
  };

  const QuestionForm = () => (
    <Form onSubmit={handleSubmit}>
      <Form.Group className="mb-3">
        <Form.Control
          as="textarea"
          rows={3}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter your question about the analysis..."
          disabled={loading}
        />
        <div className="d-flex justify-content-between align-items-center mt-2">
          <Form.Text className="text-muted">
            Ask any question about the code analysis results
          </Form.Text>
          <Dropdown>
            <Dropdown.Toggle variant="outline-secondary" size="sm">
              Quick Questions
            </Dropdown.Toggle>
            <Dropdown.Menu>
              {PREDEFINED_QUESTIONS.map((q, idx) => (
                <Dropdown.Item key={idx} onClick={() => setQuestion(q)}>
                  {q}
                </Dropdown.Item>
              ))}
            </Dropdown.Menu>
          </Dropdown>
        </div>
      </Form.Group>
      <Button
        type="submit"
        variant="info"
        disabled={loading || !question.trim()}
        className="w-100 text-white mb-4"
      >
        {loading ? (
          <>
            <Spinner animation="border" size="sm" className="me-2" />
            Processing...
          </>
        ) : (
          <>
            <FontAwesomeIcon icon={faPaperPlane} className="me-2" />
            Ask Question
          </>
        )}
      </Button>
    </Form>
  );

  const BatchQuestionForm = () => (
    <div className="mb-4">
      <div className="d-flex mb-3">
        <Form.Control
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Enter a question..."
          className="me-2"
        />
        <Button
          variant="outline-info"
          onClick={() => {
            if (question.trim()) {
              setBatchQuestions(prev => [...prev, question.trim()]);
              setQuestion('');
            }
          }}
        >
          Add
        </Button>
      </div>

      {batchQuestions.length > 0 && (
        <div className="mb-3">
          <div className="bg-light p-3 rounded mb-3">
            <h6>Questions to Process:</h6>
            {batchQuestions.map((q, idx) => (
              <div key={idx} className="d-flex justify-content-between align-items-center mb-2">
                <span>{q}</span>
                <Button
                  variant="outline-danger"
                  size="sm"
                  onClick={() => setBatchQuestions(prev => prev.filter((_, i) => i !== idx))}
                >
                  Remove
                </Button>
              </div>
            ))}
          </div>
          <Button
            variant="info"
            className="w-100 text-white"
            disabled={batchLoading}
            onClick={handleBatchSubmit}
          >
            {batchLoading ? (
              <>
                <Spinner animation="border" size="sm" className="me-2" />
                Processing Batch...
              </>
            ) : (
              <>
                <FontAwesomeIcon icon={faList} className="me-2" />
                Process {batchQuestions.length} Questions
              </>
            )}
          </Button>
        </div>
      )}
    </div>
  );

  return (
    <Container className="mb-4">
      <Card>
        <Card.Header className="bg-info text-white d-flex justify-content-between align-items-center">
          <div>
            <FontAwesomeIcon icon={faRobot} className="me-2" />
            Code Analysis Assistant
          </div>
          <div>
            <Badge bg="light" text="dark" className="me-2">
              {history.length} Questions
            </Badge>
            <Badge bg="light" text="dark">
              {savedResponses.length} Saved
            </Badge>
          </div>
        </Card.Header>
        <Card.Body>
          {error && (
            <Alert variant="danger" dismissible onClose={() => setError(null)}>
              {error}
            </Alert>
          )}

          <Tabs activeKey={activeTab} onSelect={k => setActiveTab(k)} className="mb-4">
            <Tab eventKey="ask" title="Ask Question">
              <QuestionForm />
            </Tab>
            <Tab eventKey="batch" title="Batch Questions">
              <BatchQuestionForm />
            </Tab>
            <Tab eventKey="saved" title="Saved Responses">
              <div className="saved-responses" style={{ maxHeight: '500px', overflowY: 'auto' }}>
                {savedResponses.map((item, index) => (
                  <Card key={index} className="mb-3">
                    <Card.Header className="bg-light d-flex justify-content-between align-items-center">
                      <small>{new Date(item.timestamp).toLocaleString()}</small>
                      <small className="text-muted">ID: {item.file_path.split('/').pop()}</small>
                    </Card.Header>
                    <Card.Body>
                      <p className="fw-bold mb-2">Q: {item.question}</p>
                      <p className="mb-0">A: {item.response}</p>
                    </Card.Body>
                  </Card>
                ))}
              </div>
            </Tab>
          </Tabs>

          {gptResponse && activeTab === 'ask' && (
            <Card className="mb-4">
              <Card.Header className="bg-light">Latest Response</Card.Header>
              <Card.Body>
                <div className="bg-light p-3 rounded">{gptResponse}</div>
              </Card.Body>
            </Card>
          )}

          {history.length > 0 && activeTab === 'ask' && (
            <Card>
              <Card.Header className="bg-light">
                <FontAwesomeIcon icon={faHistory} className="me-2" />
                Question History
              </Card.Header>
              <Card.Body>
                <div className="question-history" style={{ maxHeight: '400px', overflowY: 'auto' }}>
                  {history.map((item, index) => (
                    <div key={index} className="mb-3 pb-3 border-bottom">
                      <div className="d-flex justify-content-between align-items-center mb-1">
                        <small className="text-muted">
                          {new Date(item.timestamp).toLocaleString()}
                        </small>
                        {item.file_path && (
                          <small className="text-muted">
                            Saved as: {item.file_path.split('/').pop()}
                          </small>
                        )}
                      </div>
                      <p className="fw-bold mb-2">Q: {item.question}</p>
                      <p className="mb-0">A: {item.response}</p>
                    </div>
                  ))}
                </div>
              </Card.Body>
            </Card>
          )}
        </Card.Body>
      </Card>
    </Container>
  );
}

export default GPTQuestions;