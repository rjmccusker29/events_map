import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import MapPage from './components/MapPage'
import AboutPage from './components/AboutPage'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<MapPage />} />
        <Route path="/about" element={<AboutPage />} />
      </Routes>
    </Router>
  )
}

export default App