import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const NavBar = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const location = useLocation();
  
  const isActive = (path: string) => {
    return location.pathname === path ? 'bg-indigo-700' : '';
  };

  return (
    <nav className="bg-zinc-800 shadow-md">
      <div className="max-w-6xl mx-auto px-4">
        <div className="flex justify-between h-16">
          <div className="flex items-center">
            <Link to="/" className="flex-shrink-0 flex items-center">
              <span className="text-indigo-400 text-xl font-bold">TradeIQ</span>
            </Link>
            <div className="hidden md:block ml-10 flex items-baseline space-x-4">
              <Link to="/" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/') || 'hover:bg-zinc-700'}`}>
                Dashboard
              </Link>
              <Link to="/upload" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/upload') || 'hover:bg-zinc-700'}`}>
                Upload Portfolio
              </Link>
              <Link to="/analysis" className={`px-3 py-2 rounded-md text-sm font-medium ${isActive('/analysis') || 'hover:bg-zinc-700'}`}>
                Analysis
              </Link>
            </div>
          </div>
          
          {/* Mobile menu button */}
          <div className="md:hidden flex items-center">
            <button 
              onClick={() => setIsMenuOpen(!isMenuOpen)}
              className="inline-flex items-center justify-center p-2 rounded-md text-gray-400 hover:text-white hover:bg-zinc-700 focus:outline-none"
            >
              <svg className="h-6 w-6" stroke="currentColor" fill="none" viewBox="0 0 24 24">
                {isMenuOpen ? (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                ) : (
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M4 6h16M4 12h16M4 18h16" />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile menu */}
      <div className={`${isMenuOpen ? 'block' : 'hidden'} md:hidden`}>
        <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
          <Link to="/" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/') || 'hover:bg-zinc-700'}`}>
            Dashboard
          </Link>
          <Link to="/upload" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/upload') || 'hover:bg-zinc-700'}`}>
            Upload Portfolio
          </Link>
          <Link to="/analysis" className={`block px-3 py-2 rounded-md text-base font-medium ${isActive('/analysis') || 'hover:bg-zinc-700'}`}>
            Analysis
          </Link>
        </div>
      </div>
    </nav>
  );
};

export default NavBar; 