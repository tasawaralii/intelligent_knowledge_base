import type { AboutMeResponse } from "../models/response";
import api from "./api"

export const aboutMeAPI = async () : Promise<AboutMeResponse> => {
    const response = await api.get("/user/me");
    return response.data
}