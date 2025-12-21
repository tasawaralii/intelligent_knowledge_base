export type SignupResponse = {
    username: string
    email: string
    first_name?: string
    last_name?: string
}

export type SigninResponse = {
    access_token : string
    token_type: string
}

export type AboutMeResponse = {
    username: string
    email: string
    first_name: string
    last_name: string
  }