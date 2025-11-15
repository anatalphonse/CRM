import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import Login from './components/Login';
import Register from './components/Register';
import VerifyEmail from './components/VerifyEmail';

function App() {

  return (
    <>
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/Login" element={<Login />} />
        <Route path="/Register" element={<Register />} />
        <Route path="/verify-email" element={<VerifyEmail />} />
      </Routes>
    </BrowserRouter>
    </>
  )
}

export default App
