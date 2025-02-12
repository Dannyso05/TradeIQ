import React, { useState } from 'react';
import axios from 'axios';
import styles from './PortfolioAnalysisStyles.module.css';  // Make sure this matches your CSS file name exactly

const PortfolioAnalysis = () => {
    const [portfolio, setPortfolio] = useState([]);
    const [stockTicker, setStockTicker] = useState('');
    const [quantity, setQuantity] = useState('');
    const [isUploadMode, setIsUploadMode] = useState(false);

    const handleAddRow = () => {
        if (stockTicker && quantity) {
            setPortfolio([...portfolio, { stockTicker, quantity }]);
            setStockTicker('');
            setQuantity('');
        }
    };

    const handleDeleteRow = (index) => {
        const newPortfolio = portfolio.filter((_, i) => i !== index);
        setPortfolio(newPortfolio);
    };

    const handleFileUpload = (event) => {
        const file = event.target.files[0];
        console.log('Uploaded file:', file);
    };

    const fetchPortfolioAnalysis = async () => {
        const response = await axios.post('/analysis', { assets: portfolio });
        console.log('Analysis response:', response.data);
    };

    return (
        <div className={styles.portfolioAnalysis}>
            <h2>Portfolio Analysis</h2>
            <button className={`${styles.btn} ${styles.toggleBtn}`} onClick={() => setIsUploadMode(!isUploadMode)}>
                {isUploadMode ? 'Switch to Table Input' : 'Switch to File Upload'}
            </button>

            {isUploadMode ? (
                <div>
                    <input type="file" accept="application/pdf" onChange={handleFileUpload} />
                </div>
            ) : (
                <div className={styles.tableContainer}>
                    <table>
                        <thead>
                            <tr>
                                <th>Stock Ticker</th>
                                <th>Quantity</th>
                                <th>Actions</th>
                            </tr>
                        </thead>
                        <tbody>
                            {portfolio.map((item, index) => (
                                <tr key={index}>
                                    <td>{item.stockTicker}</td>
                                    <td>{item.quantity}</td>
                                    <td>
                                        <button className={`${styles.btn} ${styles.deleteBtn}`} onClick={() => handleDeleteRow(index)}>Delete</button>
                                    </td>
                                </tr>
                            ))}
                            <tr>
                                <td>
                                    <input
                                        type="text"
                                        value={stockTicker}
                                        onChange={(e) => setStockTicker(e.target.value)}
                                        placeholder="Enter stock ticker"
                                        className={styles.input}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        value={quantity}
                                        onChange={(e) => setQuantity(e.target.value)}
                                        placeholder="Enter quantity"
                                        className={styles.input}
                                    />
                                </td>
                                <td>
                                    <button className={`${styles.btn} ${styles.addBtn}`} onClick={handleAddRow}>Add</button>
                                </td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            )}
            <button className={`${styles.btn} ${styles.analyzeBtn}`} onClick={fetchPortfolioAnalysis}>Analyze Portfolio</button>
        </div>
    );
};

export default PortfolioAnalysis;