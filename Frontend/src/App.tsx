import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import './index.css';

// Lazy load components for better performance
const Dashboard = lazy(() => import('./pages/Dashboard'));
const PortfolioUpload = lazy(() => import('./pages/PortfolioUpload'));
const PortfolioAnalysis = lazy(() => import('./pages/PortfolioAnalysis'));
const NavBar = lazy(() => import('./components/NavBar'));

function App() {
  return (
    <div className="min-h-screen bg-zinc-900 text-gray-100">
      <Router>
        <Suspense fallback={
          <div className="flex justify-center items-center h-screen">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-indigo-500"></div>
          </div>
        }>
          <NavBar />
          <main className="container mx-auto px-4 py-8 max-w-6xl">
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/upload" element={<PortfolioUpload />} />
              <Route path="/analysis" element={<PortfolioAnalysis />} />
            </Routes>
          </main>
        </Suspense>
      </Router>
    </div>
  );
}

export default App;
