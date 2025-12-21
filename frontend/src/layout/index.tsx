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
            <div className="flex h-screen items-center justify-center bg-white dark:bg-gray-900">
                <div className="text-lg text-gray-900 dark:text-white">Loading...</div>
            </div>
        )
    }

    return (
        <div className="flex h-screen overflow-hidden bg-white dark:bg-gray-900">
            {/* Sidebar */}
            <Sidebar />
            
            {/* Main Content Area */}
            <div className="flex flex-1 flex-col overflow-hidden">
                {/* Header */}
                <Header />
                
                {/* Main Content */}
                <main className="flex-1 overflow-y-auto bg-gray-50 dark:bg-gray-900 p-6">
                    <Outlet />
                </main>
                
                {/* Footer */}
                <Footer />
            </div>
        </div>
    );
}
