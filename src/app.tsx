import { BrowserRouter, Route, Routes } from "react-router-dom";
import Login from "./pages/login/login";
import Main from "./pages/main/main";
import Game from "./pages/game/game";
import Cards from "./pages/cards/cards";

export default function App () {

  return (
    <BrowserRouter>
      <Routes>
        <Route path='/login' element={<Login />} />
        <Route path='/' element={<Main/>} />
        <Route path='/game' element={<Game/>}/>
        <Route path='/cards' element={<Cards/>}/>
      </Routes>
    </BrowserRouter>
  )
}