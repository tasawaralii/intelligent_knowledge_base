import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import type { AboutMeResponse } from "../models/response";
import { aboutMeAPI } from "../api/user";

interface AuthContextType {
    isLoggedIn: boolean;
    setIsLoggedIn: (value: boolean) => void;
    isLoading: boolean;
    profile : AboutMeResponse | undefined;
    refetchProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
    const [isLoggedIn, setIsLoggedIn] = useState(false);
    const [isLoading, setIsLoading] = useState(true);
    const [profile, setProfile] = useState<AboutMeResponse | undefined>(undefined)

    useEffect(() => {
        fetchProfile()
    }, [])

    const fetchProfile = async () => {
        const access_token = localStorage.getItem("access_token");
        if (access_token) {
            try {
                const data: AboutMeResponse = await aboutMeAPI()
                setProfile(data)
                setIsLoggedIn(true)
                console.log("Logged In - Token Found")
            } catch (error) {
                localStorage.removeItem("access_token")
            }
        } else {
            console.log("Logged Out")
        }
        setIsLoading(false);
    }

    return (
        <AuthContext.Provider value={{ isLoggedIn, setIsLoggedIn, isLoading, profile, refetchProfile: fetchProfile }}>
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
