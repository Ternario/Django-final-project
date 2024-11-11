import { Outlet } from "react-router-dom";

import Header from "../headers/Header";

function MainLayout({ isAuthenticated, userData, toggleUserData }) {
    return (
        <>
            <Header isAuthenticated={isAuthenticated} userData={userData} toggleUserData={toggleUserData} />
            <Outlet />
        </>
    );
}

export default MainLayout;
