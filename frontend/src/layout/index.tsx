import Header from "./Header";
import Footer from "./Footer";
import Sidebar from "./Sidebar";

import { Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../context/authContext";
import { useEffect, useState } from "react";

export default function Layout() {
    const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);
    const navigate = useNavigate()
    const { isLoggedIn, isLoading } = useAuth()
    
    useEffect(() => {
        if (!isLoading && !isLoggedIn) {
            navigate("/signin")
        }
    }, [isLoggedIn, isLoading, navigate])

    if (isLoading) {
        return (
            <div className="flex h-screen items-center justify-center">
                <div className="text-lg">Loading...</div>
            </div>
        )
    }

    return (
        <div className="flex h-screen overflow-hidden">
            {/* Sidebar */}
            <Sidebar />
            
            {/* Main Content Area */}
            <div className="flex flex-1 flex-col overflow-hidden">
                {/* Header */}
                <Header />
                
                {/* Main Content */}
                <main className="flex-1 overflow-y-auto bg-gray-50 p-6">
                    <Outlet />
                </main>
                
                {/* Footer */}
                <Footer />
            </div>
        </div>
    );
}
