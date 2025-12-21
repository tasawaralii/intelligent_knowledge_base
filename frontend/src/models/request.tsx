export type SignupRequest = {
    username: string
    email: string
    password: string
    first_name?: string
    last_name?: string
}

export type SigninRequest = {
    username: string
    password: string
}