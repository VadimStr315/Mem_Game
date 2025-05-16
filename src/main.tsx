import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.scss'
import { BrowserRouter, Route, Routes } from 'react-router-dom'
import Login from './pages/login/login.tsx'
import Main from './pages/main/main.tsx'
import Game from './pages/game/game.tsx'
import Cards from './pages/cards/cards.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <BrowserRouter>
      <Routes>
        <Route path='/login' element={<Login />} />
        <Route path='/' element={<Main/>} />
        <Route path='/game' element={<Game/>}/>
        <Route path='/cards' element={<Cards/>}/>
      </Routes>
    </BrowserRouter>
  </StrictMode>,
)
