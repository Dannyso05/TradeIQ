# TradeIQ Frontend

A modern React TypeScript frontend for the TradeIQ multi-agent financial portfolio analysis system. This frontend interfaces with the TradeIQ backend to provide an intuitive user interface for portfolio analysis.

## Features

- **Portfolio Dashboard**: View and manage your portfolio assets
- **OCR Image Upload**: Upload images of portfolio statements to extract stock data
- **Interactive Analysis**: Run AI-powered portfolio analysis with customizable goals
- **Rich Visualizations**: View risk assessments, sector allocations, and recommendations
- **Responsive Design**: Works seamlessly on desktop and mobile devices

## Tech Stack

- **React**: Frontend library for building user interfaces
- **TypeScript**: Static type checking for enhanced development experience
- **Vite**: Fast and modern build tool for frontend development
- **Tailwind CSS**: Utility-first CSS framework for styling
- **Axios**: Promise-based HTTP client for API requests
- **React Router**: For navigation and routing

## Getting Started

### Prerequisites

- Node.js 16+ and npm

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/TradeIQ.git
cd TradeIQ/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

4. Make sure the backend is running at http://localhost:3000

## Project Structure

```
frontend/
├── public/            # Static files
├── src/
│   ├── components/    # Reusable UI components
│   ├── pages/         # Page components
│   ├── models/        # TypeScript type definitions
│   ├── services/      # API services
│   ├── App.tsx        # Main app component
│   └── main.tsx       # Entry point
└── package.json       # Dependencies and scripts
```

## Development

### Building for Production

```bash
npm run build
```

### Previewing the Build

```bash
npm run preview
```

## Integration with Backend

This frontend is designed to work with the TradeIQ backend, which provides:

- Portfolio data extraction from images using OCR
- Multi-agent financial analysis
- Market sentiment analysis
- Price forecasting with machine learning

Ensure the backend API is running before using the frontend features.
