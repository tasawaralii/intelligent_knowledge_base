import api from "./api"
import type {SignupRequest, SigninRequest} from "../models/request"
import type {SignupResponse, SigninResponse} from "../models/response"

// POSTs a signup request and returns the created user without password
export const signupApi = async (user: SignupRequest): Promise<SignupResponse> => {
    const response = await api.post("/auth/signup", user)
    return response.data
}

export const signinApi = async (credentials : SigninRequest) : Promise<SigninResponse> => {
    const formData = new FormData()
    formData.append("username", credentials.username)
    formData.append("password", credentials.password)

    const response = await api.post("/auth/signin", formData)
    return response.data
}