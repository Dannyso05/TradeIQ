// src/components/Recommendations.jsx
import React, { useState } from 'react';
import axios from 'axios';
import './RecommendationsStyles.module.css';

const Recommendations = () => {
    const [recommendations, setRecommendations] = useState([]);

    const fetchRecommendations = async () => {
        const response = await axios.post('/recommendations', { /* portfolio data */ });
        setRecommendations(response.data);
    };

    return (
        <div className="recommendations">
            <h2>Recommendations</h2>
            <button className="btn" onClick={fetchRecommendations}>Get Recommendations</button>
            <ul className="recommendation-list">
                {recommendations.map((rec, index) => (
                    <li key={index} className="recommendation-item">
                        {rec.suggested_asset}: {rec.suggested_percentage}%
                    </li>
                ))}
            </ul>
        </div>
    );
};

export default Recommendations;