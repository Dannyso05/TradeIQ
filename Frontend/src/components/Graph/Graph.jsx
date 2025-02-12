// src/components/Graph.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './GraphStyles.module.css';

const Graph = () => {
    const [graphData, setGraphData] = useState(null);

    const fetchGraphData = async (ticker) => {
        const response = await axios.get(`/graph?ticker=${ticker}`);
        setGraphData(response.data);
    };

    return (
        <div className="graph">
            <h2>Graph Data</h2>
            <button className="btn" onClick={() => fetchGraphData('AAPL')}>Get Graph for AAPL</button>
            <pre className="graph-data">{JSON.stringify(graphData, null, 2)}</pre>
        </div>
    );
};

export default Graph;