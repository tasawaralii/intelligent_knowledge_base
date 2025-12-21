export type SignupResponse = {
    username: string
    email: string
    first_name?: string
    last_name?: string
}

export type SigninResponse = {
    accesstoken : string
    token_type: string
}