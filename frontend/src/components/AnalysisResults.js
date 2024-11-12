import React from 'react';
import { Card, Container, Badge, Row, Col, Accordion, ListGroup, Table } from 'react-bootstrap';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faChartBar, 
  faCode, 
  faCodeBranch,
  faExclamationCircle,
  faCog,
  faList,
  faFileCode,
  faDownload,
  faExchange,
  faWarning,
  faGears,
  faProjectDiagram,
  faNetworkWired,
  faCodeMerge,
  faServer,
  faWandMagicSparkles
} from '@fortawesome/free-solid-svg-icons';

function AnalysisResults({ analysisData }) {
  if (!analysisData) return null;

  const renderCrossReferences = (data) => {
    if (!data?.cross_reference_analysis) return null;
    
    const crossRefs = data.cross_reference_analysis;
    
    return (
      <Card className="mb-4 shadow">
        <Card.Header className="bg-info text-white">
          <FontAwesomeIcon icon={faCodeBranch} className="me-2" />
          Cross-Reference Analysis
        </Card.Header>
        <Card.Body>
          <Row className="mb-4">
            <Col md={6} className="mb-3">
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <FontAwesomeIcon icon={faExchange} className="me-2" />
                  Function Usage
                </Card.Header>
                <Card.Body>
                  <div className="mb-3">
                    <h6>Direct Function Calls</h6>
                    <ListGroup variant="flush">
                      {crossRefs.function_usage.direct_function_calls.map((func, index) => (
                        <ListGroup.Item key={index} className="font-monospace">
                          {func}
                        </ListGroup.Item>
                      ))}
                      {crossRefs.function_usage.direct_function_calls.length === 0 && (
                        <ListGroup.Item className="text-muted">No direct function calls found</ListGroup.Item>
                      )}
                    </ListGroup>
                  </div>
                  <div>
                    <h6>Imported Functions</h6>
                    <ListGroup variant="flush">
                      {crossRefs.function_usage.imported_functions.map((func, index) => (
                        <ListGroup.Item key={index} className="font-monospace">
                          {func}
                        </ListGroup.Item>
                      ))}
                      {crossRefs.function_usage.imported_functions.length === 0 && (
                        <ListGroup.Item className="text-muted">No imported functions found</ListGroup.Item>
                      )}
                    </ListGroup>
                  </div>
                </Card.Body>
              </Card>
            </Col>
            <Col md={6} className="mb-3">
              <Card className="h-100">
                <Card.Header className="bg-light">
                  <FontAwesomeIcon icon={faNetworkWired} className="me-2" />
                  Shared Dependencies
                </Card.Header>
                <Card.Body>
                  <ListGroup variant="flush">
                    {crossRefs.shared_dependencies.map((dep, index) => (
                      <ListGroup.Item key={index} className="font-monospace">
                        {dep}
                      </ListGroup.Item>
                    ))}
                    {crossRefs.shared_dependencies.length === 0 && (
                      <ListGroup.Item className="text-muted">No shared dependencies found</ListGroup.Item>
                    )}
                  </ListGroup>
                </Card.Body>
              </Card>
            </Col>
          </Row>

          <Card>
            <Card.Header className="bg-light">
              <FontAwesomeIcon icon={faServer} className="me-2" />
              API Integration
            </Card.Header>
            <Card.Body>
              <Table hover size="sm">
                <thead>
                  <tr>
                    <th>Endpoint</th>
                    <th>Method</th>
                    <th>Client Library</th>
                    <th>Arguments</th>
                  </tr>
                </thead>
                <tbody>
                  {crossRefs.api_integration.api_calls.map((call, index) => (
                    <tr key={index}>
                      <td className="font-monospace">{call.endpoint}</td>
                      <td className="font-monospace">{call.http_method}</td>
                      <td className="font-monospace">{call.client_library}</td>
                      <td className="font-monospace">
                        <pre className="mb-0" style={{ fontSize: '0.875em' }}>
                          {JSON.stringify(call.arguments, null, 2)}
                        </pre>
                      </td>
                    </tr>
                  ))}
                  {crossRefs.api_integration.api_calls.length === 0 && (
                    <tr>
                      <td colSpan={4} className="text-center text-muted">
                        No API calls found
                      </td>
                    </tr>
                  )}
                </tbody>
              </Table>
            </Card.Body>
          </Card>
        </Card.Body>
      </Card>
    );
  };

  const renderMetrics = (type, data) => {
    if (!data) return null;

    // Extract function count from function_call_chains
    const functionCount = type === 'Application' 
      ? Object.keys(data?.function_call_chains?.app_py || {}).length 
      : Object.keys(data?.function_call_chains?.api_py || {}).length;

    // Extract class count from class hierarchy
    const classCount = type === 'Application'
      ? Object.keys(data?.class_hierarchy?.app_py || {}).length
      : Object.keys(data?.class_hierarchy?.api_py || {}).length;

    // Extract function calls from node types
    const functionCallCount = type === 'Application'
      ? (data?.node_type_frequencies?.app_py?.call || 0)
      : (data?.node_type_frequencies?.api_py?.call || 0);

    const metrics = [
      { 
        label: 'Functions', 
        value: functionCount, 
        variant: 'primary',
        icon: faCode
      },
      { 
        label: 'Classes', 
        value: classCount, 
        variant: 'info',
        icon: faGears
      },
      { 
        label: 'Function Calls', 
        value: functionCallCount, 
        variant: 'success',
        icon: faExchange
      }
    ];

    return (
      <>
        <h4 className="mb-3">
          <FontAwesomeIcon icon={faCog} className="me-2" />
          {type} Analysis
        </h4>
        <Row className="mb-4">
          {metrics.map((metric, index) => (
            <Col key={index} md={4} className="mb-3">
              <Card className="h-100 shadow-sm">
                <Card.Body className="d-flex flex-column align-items-center justify-content-center">
                  <FontAwesomeIcon 
                    icon={metric.icon} 
                    className={`mb-2 text-${metric.variant}`} 
                    size="2x"
                  />
                  <h6 className="text-muted mb-2">{metric.label}</h6>
                  <h3>
                    <Badge bg={metric.variant} className="px-4 py-2">
                      {metric.value}
                    </Badge>
                  </h3>
                </Card.Body>
              </Card>
            </Col>
          ))}
        </Row>
      </>
    );
  };

  const renderNodeTypes = (nodeTypes) => {
    if (!nodeTypes) return null;
    
    return (
      <Card className="mb-3">
        <Card.Header className="bg-light">
          <FontAwesomeIcon icon={faProjectDiagram} className="me-2" />
          Node Types Analysis
        </Card.Header>
        <Card.Body>
          <div className="table-responsive">
            <Table hover size="sm">
              <thead>
                <tr>
                  <th>Node Type</th>
                  <th>Count</th>
                </tr>
              </thead>
              <tbody>
                {Object.entries(nodeTypes)
                  .sort(([, a], [, b]) => b - a)
                  .map(([type, count]) => (
                    <tr key={type}>
                      <td className="font-monospace">{type}</td>
                      <td>
                        <Badge bg="secondary">{count}</Badge>
                      </td>
                    </tr>
                  ))}
              </tbody>
            </Table>
          </div>
        </Card.Body>
      </Card>
    );
  };

  const renderRelationships = (type) => {
    // Get relationships from data
    const relationships = type === 'Application' ? 
      analysisData?.api_analysis?.relationships || [] :
      analysisData?.app_analysis?.relationships || [];
  
    if (!Array.isArray(relationships) || relationships.length === 0) return null;
  
    return (
      <Card className="mb-3">
        <Card.Header className="bg-light">
          <FontAwesomeIcon icon={faNetworkWired} className="me-2" />
          Class Relationships
        </Card.Header>
        <Card.Body>
          <Table hover size="sm">
            <thead>
              <tr>
                <th>Class</th>
                <th>Function</th>
                <th>Type</th>
              </tr>
            </thead>
            <tbody>
              {relationships.map((rel, index) => (
                <tr key={index}>
                  <td className="font-monospace">{rel.class}</td>
                  <td className="font-monospace">{rel.function}</td>
                  <td>
                    <Badge bg={rel.is_async ? "info" : "primary"}>
                      {rel.is_async ? "Async" : "Sync"}
                    </Badge>
                  </td>
                </tr>
              ))}
              {relationships.length === 0 && (
                <tr>
                  <td colSpan={3} className="text-center text-muted">
                    No class relationships found
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    );
  };

  const renderFunctionDependencies = (dependencies) => {
    if (!dependencies) return null;

    return (
      <Card className="mb-3">
        <Card.Header className="bg-light">
          <FontAwesomeIcon icon={faCodeMerge} className="me-2" />
          Function Dependencies
        </Card.Header>
        <Card.Body>
          <Accordion>
            {Object.entries(dependencies).map(([func, deps], index) => (
              <Accordion.Item eventKey={index} key={func}>
                <Accordion.Header>
                  <span className="font-monospace">{func}</span>
                  <Badge bg="secondary" className="ms-2">{deps.length} dependencies</Badge>
                </Accordion.Header>
                <Accordion.Body>
                  <ListGroup variant="flush">
                    {deps.map((dep, i) => (
                      <ListGroup.Item key={i} className="font-monospace">
                        {dep}
                      </ListGroup.Item>
                    ))}
                  </ListGroup>
                </Accordion.Body>
              </Accordion.Item>
            ))}
          </Accordion>
        </Card.Body>
      </Card>
    );
  };

  const renderDecoratedFunctions = (decoratedFunctions) => {
    if (!decoratedFunctions || decoratedFunctions.length === 0) return null;

    return (
      <Card className="mb-3">
        <Card.Header className="bg-light">
          <FontAwesomeIcon icon={faWandMagicSparkles} className="me-2" />
          Decorated Functions
        </Card.Header>
        <Card.Body>
          <ListGroup variant="flush">
            {decoratedFunctions.map((func, index) => (
              <ListGroup.Item key={index}>
                <h6 className="font-monospace mb-2">{func.name}</h6>
                <div className="ms-3">
                  <div className="mb-2">
                    <Badge bg={func.is_async ? "info" : "secondary"} className="me-2">
                      {func.is_async ? "Async" : "Sync"}
                    </Badge>
                    {func.decorators.map((dec, i) => (
                      <Badge bg="primary" className="me-2" key={i}>@{dec.name}</Badge>
                    ))}
                  </div>
                  {func.parameters && func.parameters.length > 0 && (
                    <div className="font-monospace small">
                      Parameters:
                      <ul className="mb-0">
                        {func.parameters.map((param, i) => (
                          <li key={i}>
                            {param.name}
                            {param.type && `: ${param.type}`}
                            {param.default && ` = ${param.default}`}
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </ListGroup.Item>
            ))}
          </ListGroup>
        </Card.Body>
      </Card>
    );
  };

  const renderClassHierarchy = (hierarchy) => {
    if (!hierarchy || Object.keys(hierarchy).length === 0) return null;

    return (
      <Card className="mb-3">
        <Card.Header className="bg-light">
          <FontAwesomeIcon icon={faProjectDiagram} className="me-2" />
          Class Hierarchy
        </Card.Header>
        <Card.Body>
          <Accordion>
            {Object.entries(hierarchy).map(([className, details], index) => (
              <Accordion.Item eventKey={index} key={className}>
                <Accordion.Header>
                  <span className="font-monospace">{className}</span>
                </Accordion.Header>
                <Accordion.Body>
                  {details.parent_classes?.length > 0 && (
                    <div className="mb-3">
                      <strong>Parent Classes:</strong>
                      <ListGroup variant="flush">
                        {details.parent_classes.map((parent, i) => (
                          <ListGroup.Item key={i} className="font-monospace">
                            {parent}
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </div>
                  )}
                  {details.methods?.length > 0 && (
                    <div>
                      <strong>Methods:</strong>
                      <ListGroup variant="flush">
                        {details.methods.map((method, i) => (
                          <ListGroup.Item key={i} className="font-monospace">
                            {method}
                          </ListGroup.Item>
                        ))}
                      </ListGroup>
                    </div>
                  )}
                </Accordion.Body>
              </Accordion.Item>
            ))}
          </Accordion>
        </Card.Body>
      </Card>
    );
  };

  const renderAnalysisSection = (type, data) => {
    if (!data) return null;

    return (
      <Card className="mb-4 shadow">
        <Card.Header className={`bg-${type === 'Application' ? 'primary' : 'success'} text-white`}>
          <FontAwesomeIcon icon={type === 'Application' ? faFileCode : faCode} className="me-2" />
          {type} Analysis
        </Card.Header>
        <Card.Body>
          {renderMetrics(type, analysisData)}
          
          <Accordion className="mb-3">
            <Accordion.Item eventKey="0">
              <Accordion.Header>
                <FontAwesomeIcon icon={faList} className="me-2" />
                Detailed Analysis
              </Accordion.Header>
              <Accordion.Body>
                {renderNodeTypes(type === 'Application' ? 
                  analysisData.node_type_frequencies?.app_py : 
                  analysisData.node_type_frequencies?.api_py)}
                {renderRelationships(type === 'Application' ?
                  analysisData.function_call_chains?.app_py :
                  analysisData.function_call_chains?.api_py)}
                {renderFunctionDependencies(type === 'Application' ?
                  analysisData.function_call_chains?.app_py :
                  analysisData.function_call_chains?.api_py)}
                {type === 'Application' && renderApiCalls(
                  analysisData.cross_reference_analysis?.api_integration?.api_calls
                )}
                {renderDecoratedFunctions(type === 'Application' ?
                  analysisData.decorated_functions?.app_py :
                  analysisData.decorated_functions?.api_py)}
                {renderClassHierarchy(type === 'Application' ?
                  analysisData.class_hierarchy?.app_py :
                  analysisData.class_hierarchy?.api_py)}
              </Accordion.Body>
            </Accordion.Item>
          </Accordion>
        </Card.Body>
      </Card>
    );
  };
  const renderApiCalls = (apiCalls) => {
    if (!apiCalls || apiCalls.length === 0) return null;

    return (
      <Card className="mb-3">
        <Card.Header className="bg-light">
          <FontAwesomeIcon icon={faServer} className="me-2" />
          API Calls
        </Card.Header>
        <Card.Body>
          <Table hover size="sm">
            <thead>
              <tr>
                <th>Endpoint</th>
                <th>Method</th>
                <th>Client Library</th>
                <th>Arguments</th>
              </tr>
            </thead>
            <tbody>
              {apiCalls.map((call, index) => (
                <tr key={index}>
                  <td className="font-monospace">{call.endpoint || '-'}</td>
                  <td className="font-monospace">{call.http_method}</td>
                  <td className="font-monospace">{call.client_library}</td>
                  <td className="font-monospace">
                    <pre className="mb-0" style={{ fontSize: '0.875em' }}>
                      {JSON.stringify(call.arguments, null, 2)}
                    </pre>
                  </td>
                </tr>
              ))}
              {apiCalls.length === 0 && (
                <tr>
                  <td colSpan={4} className="text-center text-muted">
                    No API calls found
                  </td>
                </tr>
              )}
            </tbody>
          </Table>
        </Card.Body>
      </Card>
    );
  };
  const renderErrorHandling = () => {
    const appErrors = analysisData.error_handling?.app_py || [];
    const apiErrors = analysisData.error_handling?.api_py || [];

    if (appErrors.length === 0 && apiErrors.length === 0) return null;

    return (
      <Card className="mb-4 shadow">
        <Card.Header className="bg-warning text-dark">
          <FontAwesomeIcon icon={faWarning} className="me-2" />
          Error Handling Analysis
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h6>Application Error Handling</h6>
              <ListGroup variant="flush">
                {appErrors.map((func, index) => (
                  <ListGroup.Item key={index} className="font-monospace">
                    {func}
                  </ListGroup.Item>
                ))}
                {appErrors.length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No error handling found
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
            <Col md={6}>
              <h6>API Error Handling</h6>
              <ListGroup variant="flush">
                {apiErrors.map((func, index) => (
                  <ListGroup.Item key={index} className="font-monospace">
                    {func}
                  </ListGroup.Item>
                ))}
                {apiErrors.length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No error handling found
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  const renderAsyncFunctions = () => {
    const appAsync = analysisData.async_functions?.app_py || [];
    const apiAsync = analysisData.async_functions?.api_py || [];

    if (appAsync.length === 0 && apiAsync.length === 0) return null;

    return (
      <Card className="mb-4 shadow">
        <Card.Header className="bg-secondary text-white">
          <FontAwesomeIcon icon={faGears} className="me-2" />
          Asynchronous Functions
        </Card.Header>
        <Card.Body>
          <Row>
            <Col md={6}>
              <h6>Application Async Functions</h6>
              <ListGroup variant="flush">
                {appAsync.map((func, index) => (
                  <ListGroup.Item key={index} className="font-monospace">
                    {func}
                  </ListGroup.Item>
                ))}
                {appAsync.length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No async functions found
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
            <Col md={6}>
              <h6>API Async Functions</h6>
              <ListGroup variant="flush">
                {apiAsync.map((func, index) => (
                  <ListGroup.Item key={index} className="font-monospace">
                    {func}
                  </ListGroup.Item>
                ))}
                {apiAsync.length === 0 && (
                  <ListGroup.Item className="text-muted">
                    No async functions found
                  </ListGroup.Item>
                )}
              </ListGroup>
            </Col>
          </Row>
        </Card.Body>
      </Card>
    );
  };

  return (
    <Container className="mb-4">
      {renderCrossReferences(analysisData)}
      {renderAnalysisSection('Application', analysisData)}
      {renderAnalysisSection('API', analysisData)}
      {renderErrorHandling()}
      {renderAsyncFunctions()}
    </Container>
  );
}

export default AnalysisResults;