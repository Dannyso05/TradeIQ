import React from 'react'
import PortfolioAnalysis from './components/PortfolioAnalysis/PortfolioAnalysis'
import Recommendations from './components/Recommendations/Recommendations'
import Graph from './components/Graph/Graph'
import './App.css'

function App() {
  return (
    <div>
      <h1>TradeIQ Portfolio Analysis</h1>
      <PortfolioAnalysis />
      <Recommendations />
      <Graph />
    </div>
  )
}

export default App
