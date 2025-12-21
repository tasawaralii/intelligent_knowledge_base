import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

interface AuthContextType {
    isLoggedIn: boolean;
    setIsLoggedIn: (value: boolean) => void;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        const access_token = localStorage.getItem("access_token");
        if (access_token) {
            setIsLoggedIn(true)
            console.log("Logged In - Token Found")
        } else {
            console.log("Logged Out")
        }
        setIsLoading(false);
    }, [])

    return (
        <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn, isLoading }}>
            {children}
        </AuthContext.Provider>
    );
};

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
};
