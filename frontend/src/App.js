import React, { useState } from 'react';
import Navbar from './components/Navbar';
import UploadFiles from './components/UploadFiles';
import AnalysisResults from './components/AnalysisResults';
import GPTQuestions from './components/GPTQuestions';
import MermaidDiagram from './components/MermaidDiagram';

function App() {
  const [analysisData, setAnalysisData] = useState(null);

  return (
    <div>
      <Navbar />
      {!analysisData ? (
        <UploadFiles onAnalysisComplete={setAnalysisData} />
      ) : (
        <>
          <AnalysisResults analysisData={analysisData} />
          <GPTQuestions analysisData={analysisData} />
          <MermaidDiagram analysisData={analysisData} />
        </>
      )}
    </div>
  );
}

export default App;
