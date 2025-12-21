import { useEffect, useState, type FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { signinApi } from "../api/auth";
import type { SigninRequest } from "../models/request";
import type { SigninResponse } from "../models/response";
import { useAuth } from "../context/authContext";

export default function SigninPage() {

  const navigate = useNavigate()
  const { refetchProfile } = useAuth()

  useEffect(() => {
    const access_token = localStorage.getItem("access_token");
    if (access_token) {
      navigate("/")
    }
  },[])

  const [credentials, setCredentials] = useState<SigninRequest>({username:"",password:""})

  const submit = async (e:FormEvent) => {
    e.preventDefault();
    try {
      const response : SigninResponse = await signinApi(credentials)
      localStorage.setItem("access_token", response.access_token);
      await refetchProfile();
      navigate("/")
    } catch (error) { }
  };

  return (
    <div className="flex bg-gray-200 min-h-screen items-center justify-center px-6">
      <div className="w-full max-w-md rounded-2xl bg-white dark:bg-gray-900 shadow-2xl p-8">
        <div className="text-center">
          <h2 className="mt-6 text-3xl font-bold text-gray-900 dark:text-white">
            Welcome Back
          </h2>
          <p className="mt-2 text-sm text-gray-600 dark:text-gray-400">
            Please sign in to continue
          </p>
        </div>

        <form onSubmit={submit} className="mt-8 space-y-6">
          <div>
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-700 dark:text-gray-200"
            >
              Username
            </label>
            <input
              id="username"
              name="username"
              type="text"
              value={credentials.username}
              onChange={(e) => setCredentials({...credentials,username:e.target.value})}
              required
              autoComplete="username"
              className="mt-2 block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none sm:text-sm"
            />
          </div>

          <div>
            <div className="flex items-center justify-between">
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-200"
              >
                Password
              </label>
              <a
                href="#"
                className="text-sm font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500"
              >
                Forgot password?
              </a>
            </div>
            <input
              id="password"
              name="password"
              type="password"
              value={credentials.password}
              onChange={(e) => setCredentials({ ...credentials, password: e.target.value })}
              required
              autoComplete="current-password"
              className="mt-2 block w-full rounded-lg border border-gray-300 dark:border-gray-700 bg-white dark:bg-gray-800 px-3 py-2 text-gray-900 dark:text-white placeholder-gray-400 dark:placeholder-gray-500 focus:ring-2 focus:ring-indigo-500 focus:outline-none sm:text-sm"
            />
          </div>

          <button
            type="submit"
            className="w-full rounded-lg bg-indigo-600 px-4 py-2 text-white font-semibold shadow-md hover:bg-indigo-500 focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 dark:focus:ring-offset-gray-900"
          >
            Sign in
          </button>
        </form>

        <p className="mt-8 text-center text-sm text-gray-600 dark:text-gray-400">
          Don't have an account?{" "}
          <Link
            to="/signup"
            className="font-semibold text-indigo-600 dark:text-indigo-400 hover:text-indigo-500"
          >
            Register now
          </Link>
        </p>
      </div>
    </div>
  );
}