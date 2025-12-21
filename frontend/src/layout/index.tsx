import Header from "./Header";
import Footer from "./Footer";
import Sidebar from "./Sidebar";

import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContext";
import { useEffect } from "react";

export default function Layout() {

    const navigate = useNavigate()
    const { isLoggedIn, isLoading } = useAuth()
    useEffect(() => {
        if (!isLoading && !isLoggedIn) {
            navigate("/signin")
        }
    }, [isLoggedIn, isLoading, navigate])

    if (isLoading) {
        return <div>Loading...</div>
    }

    return (
        <div className="min-h-screen flex flex-col">
            <Header/>
            <Sidebar />

            <main className="grow sm:ml-64 mt-14 bg-gray-50">
                <Outlet />
            </main>

            <footer className="sm:ml-64">
                <Footer />
            </footer>
        </div>
    );
}
