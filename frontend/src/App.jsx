import { Route, Routes } from 'react-router-dom'
import Navbar from './components/Navbar.jsx'
import Footer from './components/Footer.jsx'
import Home from './pages/Home.jsx'
import Chat from './pages/Chat.jsx'
import Scan from './pages/Scan.jsx'
import Standards from './pages/Standards.jsx'
import Forms from './pages/Forms.jsx'
import Roadmap from './pages/Roadmap.jsx'

export default function App() {
  return (
    <div className="flex min-h-screen flex-col bg-paper-50">
      <Navbar />
      <main className="flex-1">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/chat" element={<Chat />} />
          <Route path="/scan" element={<Scan />} />
          <Route path="/standards" element={<Standards />} />
          <Route path="/forms" element={<Forms />} />
          <Route path="/roadmap" element={<Roadmap />} />
        </Routes>
      </main>
      <Footer />
    </div>
  )
}
