import { BrowserRouter, Routes, Route } from "react-router-dom";
import { useState } from "react";

import "bootstrap/dist/css/bootstrap.min.css";

import "./App.css";

import MainLayout from "./components/layout/MainLayout";
import Home from "./components/main/home/Home";
import Search from "./components/main/search/Search";
import Profile from "./components/main/profile/Profile";
import SignUp from "./components/main/singUp/SignUp";
import SignIn from "./components/main/signIn/SignIn";

function App() {
    const [isAuthenticated, setIsAuthenticated] = useState(false);
    const [userData, setUserData] = useState({});

    const toggleUserData = (data) => {
        if (!data) {
            setUserData({});
            setIsAuthenticated(false);
            return;
        }

        setIsAuthenticated(true);
        setUserData(data);
    };

    return (
        <BrowserRouter>
            <div className="App">
                <Routes>
                    <Route path="/" element={<MainLayout isAuthenticated={isAuthenticated} userData={userData} toggleUserData={toggleUserData} />}>
                        <Route index element={<Home />} />
                        <Route path="/search" element={<Search />} />
                        <Route path="/detail/:id" />
                        <Route path="/profile" element={<Profile />} />
                        <Route path="/reservation" />
                        <Route path="/signUp" element={<SignUp />} />
                        <Route path="/signIn" element={<SignIn toggleUserData={toggleUserData} />} />
                        <Route path="/*" />
                    </Route>
                </Routes>
            </div>
        </BrowserRouter>
    );
}

export default App;
