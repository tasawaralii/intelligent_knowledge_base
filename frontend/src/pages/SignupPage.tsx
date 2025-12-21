import { useState, type ChangeEvent, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signupApi } from "../api/auth";
import type {SignupRequest} from "../models/request"
import type { SignupResponse } from "../models/response";

const SignupPage = () => {

    const navigate = useNavigate();

    const [userInfo, setUserInfo] = useState<SignupRequest>({
        username: "",
        email: "",
        password: "",
        first_name: "",
        last_name: ""
    })

    const onChange = (e: ChangeEvent<HTMLInputElement>) => {
        const { name, value } = e.target;
        setUserInfo((prev) => ({ ...prev, [name]: value }))
    }

    const submit = async (e: FormEvent) => {
        e.preventDefault();
        try {
            const newUser: SignupResponse = await signupApi(userInfo)
            if(newUser.username) {
                navigate("/")
            }
        } catch (error) {

        }
    }

    return (
        <div className="flex bg-gray-200 min-h-screen items-center justify-center px-6">
            <div className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl p-8">
                <div className="sm:mx-auto sm:w-full sm:max-w-sm">
                    <h2 className="mt-10 text-center text-2xl font-bold tracking-tight text-gray-900 dark:text-white">
                        Register a New account
                    </h2>
                </div>

                <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
                    <form onSubmit={submit} autoComplete="off" className="space-y-6">
                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-medium text-gray-900 dark:text-gray-100"
                            >
                                Email
                            </label>
                            <div className="mt-2">
                                <input
                                    name="email"
                                    type="email"
                                    value={userInfo.email}
                                    onChange={onChange}
                                    required
                                    autoComplete="new-email"
                                    className="block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        <div>
                            <label
                                htmlFor="email"
                                className="block text-sm font-medium text-gray-900 dark:text-gray-100"
                            >
                                Username
                            </label>
                            <div className="mt-2">
                                <input
                                    id="username"
                                    name="username"
                                    type="text"
                                    value={userInfo.username}
                                    onChange={onChange}
                                    minLength={8}
                                    required
                                    autoComplete="new-username"
                                    className="block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        <div>
                            <div className="flex items-center justify-between">
                                <label
                                    htmlFor="password"
                                    className="block text-sm font-medium text-gray-900 dark:text-gray-100"
                                >
                                    Password
                                </label>
                            </div>
                            <div className="mt-2">
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    value={userInfo.password}
                                    onChange={onChange}
                                    required
                                    minLength={8}
                                    autoComplete="new-password"
                                    className="block w-full rounded-md border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-1.5 text-base text-gray-900 dark:text-white placeholder:text-gray-400 dark:placeholder:text-gray-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 sm:text-sm"
                                />
                            </div>
                        </div>

                        <div>
                            <button
                                type="submit"
                                className="flex w-full justify-center rounded-md bg-indigo-600 hover:bg-indigo-500 px-3 py-1.5 text-sm font-semibold text-white focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900 cursor-pointer"
                            >
                                Register
                            </button>
                        </div>
                    </form>

                    <p className="mt-10 text-center text-sm text-gray-600 dark:text-gray-400">
                        Already Registered?{" "}
                        <Link
                            to="/signin"
                            className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500 dark:hover:text-indigo-300"
                        >
                            Login Now
                        </Link>
                    </p>
                </div>
            </div>
        </div>
    );
};

export default SignupPage;
